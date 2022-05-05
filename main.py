# Import Flask Library
from flask import Flask, flash, render_template, request, session, url_for, redirect
import pymysql.cursors
import string
import random
import datetime
from dateutil.relativedelta import relativedelta
import pytz
import hashlib


# Initialize the app from Flask
app = Flask(__name__)

# Configure MySQL
conn = pymysql.connect(host='localhost',
                       user='root',
                       password='root',
                       db='air_ticket_system',
                       port= 8889, 
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)


# Define a route to homepage
@app.route('/')
def hello():
    return render_template('index.html')


# Define a route to hello function
@app.route('/flight_search')
def flight_search():
    if session.get('name'):
        name = session['name']  
        return render_template('flight_search.html', username=name, flights=None)
    return render_template('flight_search.html', flights=None)


# Performs flight search based on the origin city or airport
@app.route('/flight_finder', methods=['GET', 'POST'])
def flight_finder():
    # grabs information from the forms
    origin = request.form['origin_search1']
    destination = request.form['destination_search1']
    dept_date = request.form['dept_date_search1']
    return_date = request.form['return_date_search1']
    cursor = conn.cursor()
    query1 = ''
    # if all input fields were filled out
    if origin and destination and dept_date and return_date:
        query1 = 'SELECT * FROM origin_destination_name '\
                 'WHERE '\
                    '(origin_city IN '\
                        '(SELECT origin_city '\
                        'FROM origin_destination_name '\
                        'WHERE origin_city=%s '\
                        'OR origin_airport=%s) '\
                    'AND DATE(dept_date_time)=%s '\
                    'AND destination_city IN '\
                        '(SELECT destination_city '\
                        'FROM origin_destination_name '\
                        'WHERE destination_city=%s '\
                        'OR destination_airport=%s)) '\
                 'OR (origin_city IN '\
                        '(SELECT origin_city '\
                        'FROM origin_destination_name '\
                        'WHERE origin_city=%s '\
                        'OR origin_airport=%s) '\
                    'AND DATE(dept_date_time)=%s '\
                    'AND destination_city IN '\
                        '(SELECT destination_city '\
                        'FROM origin_destination_name '\
                        'WHERE destination_city=%s '\
                        'OR destination_airport=%s)) '

        cursor.execute(query1, (origin, origin, dept_date, destination, destination, destination, destination, return_date, origin, origin))
    # if all inputs but return date are given
    elif origin and destination and dept_date:
        query1 = 'SELECT * FROM origin_destination_name '\
                 'WHERE '\
                    '(origin_city IN '\
                        '(SELECT origin_city '\
                        'FROM origin_destination_name '\
                        'WHERE origin_city=%s '\
                        'OR origin_airport=%s) '\
                    'AND DATE(dept_date_time)=%s '\
                    'AND destination_city IN '\
                        '(SELECT destination_city '\
                        'FROM origin_destination_name '\
                        'WHERE destination_city=%s '\
                        'OR destination_airport=%s)) '\
                 'OR (origin_city IN '\
                        '(SELECT origin_city '\
                        'FROM origin_destination_name '\
                        'WHERE origin_city=%s '\
                        'OR origin_airport=%s) '\
                    'AND destination_city IN '\
                            '(SELECT destination_city '\
                            'FROM origin_destination_name '\
                            'WHERE destination_city=%s '\
                            'OR destination_airport=%s)) '
        cursor.execute(query1, (origin, origin, dept_date, destination, destination, destination, destination, origin, origin))

    error = None
    # stores the results in a variable
    data = cursor.fetchall()
    # use fetchall() if you are expecting more than 1 data row
    cursor.close()
    if data:
        session['flights_searched'] = data
        if session.get('name'):
            name = session['name']
            return render_template("flight_search.html", flights=data, username=name)
        return render_template("flight_search.html", flights=data)
    else:
        error = "No flight matched your search, maybe try a different search."
        return render_template("flight_search.html", error=error)


# Checks flight status based on airline name, flight number, and arrival/departure date
@app.route('/check_flight_status', methods=['GET', 'POST'])
def check_flight_status():
    # grabs information from the forms
    airline = request.form['airline']
    flight_number = request.form['flight_num']
    arrival_date = request.form['arrival_date']
    departure_date = request.form['departure_date']
    cursor = conn.cursor()
    query = 'SELECT * FROM origin_destination_name '\
            'WHERE airline_name=%s '\
            'AND flight_num=%s'\
            'AND DATE(arr_date_time)=%s'\
            'AND DATE(dept_date_time)=%s'
    cursor.execute(query, (airline, flight_number, arrival_date, departure_date))
    error = None
    # stores the results in a variable
    data = cursor.fetchall()
    # use fetchall() if you are expecting more than 1 data row
    cursor.close()
    if data:
        session['flights_searched'] = data
        if session.get('name'):
            name = session['name']
            return render_template("flight_search.html", flights=data, username=name)
        return render_template("flight_search.html", flights=data)
    else:
        error = "No flight matched your search, maybe try a different search."
        return render_template("flight_search.html", error=error)



# load the flight purchase page
@app.route('/purchase', methods=['GET', 'POST'])
def purchase():
    flight_to_purchase = request.form['flight_to_purchase']
    flights = session['flights_searched']
    name = session['name']
    flight = flights[int(flight_to_purchase)]
    session['flight_to_purchase'] = flight
    check_occupancy = 'SELECT seats_booked, num_seats '\
                      'FROM flight NATURAL JOIN airplane '\
                      'WHERE airplane.ID=%s AND flight.name=%s '\
                      'AND flight_num=%s AND dept_date_time=%s'
    cursor = conn.cursor()
    cursor.execute(check_occupancy, (flight['ID'], flight['airline_name'],
                                     flight['flight_num'], flight['dept_date_time']))
    data = cursor.fetchone()
    base_price = float(flight['base_price'])
    seats_booked = int(data['seats_booked'])
    num_seats = int(data['num_seats'])
    print('seats_booked: ' + str(seats_booked))
    print('num_seats: ' + str(num_seats))
    price = float(base_price)
    if seats_booked/num_seats >= 0.75:
        price = 1.25 * base_price
    cursor.close()
    return render_template('purchase.html', name=name, flight=flight, price=price)


# purchase the specified flight
@app.route('/make_purchase', methods=['GET', 'POST'])
def make_purchase():
    flight = session['flight_to_purchase']
    name = session['name']
    email = session['username']
    travel_class = request.form['flight_class']
    card_type = request.form['card_type']
    card_num = request.form['card_number']
    name_on_card = request.form['name_on_card']
    card_expiry = request.form['card_expiry']
    card_expiry = card_expiry + '-01'
    price = request.form['price']

    # First, make sure flight isn't already full:
    get_seats_booked = 'SELECT seats_booked '\
                       'FROM flight '\
                       'WHERE ID=%s AND name=%s AND flight_num=%s AND dept_date_time=%s '
    cursor = conn.cursor()
    cursor.execute(get_seats_booked, (flight['ID'], flight['airline_name'],
                                      flight['flight_num'], flight['dept_date_time']))
    seats_booked = int(cursor.fetchone()['seats_booked'])
    cursor.close()

    get_flight_capacity = 'SELECT num_seats '\
                          'FROM airplane '\
                          'WHERE ID=%s '
    cursor = conn.cursor()
    cursor.execute(get_flight_capacity, (flight['ID']))
    total_seats = int(cursor.fetchone()['num_seats'])
    cursor.close()

    if seats_booked < total_seats:
        purchase_flight1 = 'INSERT INTO ticket '\
                           'VALUES (%s, %s)'
        # create a 6-character random ticket ID: (TODO: make sure it is one that hasn't been used)
        ticket_id = ''.join(random.choice(string.ascii_uppercase+string.digits) for _ in range(6))
        cursor = conn.cursor()
        cursor.execute(purchase_flight1, (ticket_id, travel_class))
        conn.commit()
        cursor.close()

        purchase_flight2 = 'INSERT INTO ticket_flight '\
                           'VALUES (%s, %s, %s, %s, %s)'
        cursor = conn.cursor()
        cursor.execute(purchase_flight2, (ticket_id, flight['ID'], flight['airline_name'],
                                          flight['flight_num'], flight['dept_date_time']))
        conn.commit()
        cursor.close()

        purchase_flight3 = 'INSERT INTO purchased '\
                           'VALUES (%s, %s, NOW(), %s, %s, %s, %s, %s)'
        cursor = conn.cursor()
        cursor.execute(purchase_flight3, (ticket_id, email, price, card_type,
                                          card_num, name_on_card, card_expiry))
        conn.commit()
        cursor.close()

        cursor = conn.cursor()
        update_seats = 'UPDATE flight '\
                       'SET seats_booked = seats_booked+1 '\
                       'WHERE ID=%s AND name=%s AND flight_num=%s AND dept_date_time=%s '

        cursor.execute(update_seats, (flight['ID'], flight['airline_name'],
                                      flight['flight_num'], flight['dept_date_time']))
        conn.commit()
        cursor.close()
        return render_template('purchase.html', name=name, flight=flight, success=True)
    else:
        error = 'We apologize, this flight is already full. Please choose a different one!'
        return render_template('purchase.html', name=name, flight=flight, price=price, error=error)


# Define route for login
@app.route('/login')
def login():
    return render_template('login.html')


# Define route for customer_registration
@app.route('/customer_registration')
def cust_register():
    return render_template('customer_registration.html')


# Define route for staff_registration
@app.route('/staff_registration')
def staff_register():
    return render_template('staff_registration.html')


# Authenticates the login
@app.route('/loginAuth', methods=['GET', 'POST'])
def loginAuth():
    # grabs information from the forms
    username = request.form['username']
    password = request.form['password']
    password = hashlib.md5(password.encode('utf-8')).hexdigest()
    user_type = request.form['user_type']
    # cursor used to send queries
    cursor = conn.cursor()
    # executes query
    error = None
    if user_type == 'CUSTOMER':
        query = 'SELECT * FROM customer WHERE email = %s and password = %s'
        cursor.execute(query, (username, password))
        # stores the results in a variable
        data = cursor.fetchone()
        # use fetchall() if you are expecting more than 1 data row
        cursor.close()
        if data:
            session['name'] = data['name']
            # creates a session for the user
            # session is a built in
            session['username'] = username
            session['user_type'] = user_type
            # cursor used to send queries
            cursor = conn.cursor()
            future_flight_query = 'SELECT * FROM purchased NATURAL JOIN ticket_flight NATURAL JOIN origin_destination_name '\
                                  'WHERE email=%s '\
                                  'AND dept_date_time>NOW()'
            cursor.execute(future_flight_query, (username))
            # stores the results in a variable
            data = cursor.fetchall()
            # use fetchall() if you are expecting more than 1 data row
            cursor.close()
            session['flights'] = data
            # redirects to the function that prints customer
            return redirect(url_for('customer_home'))
        else:
            # returns an error message to the html page
            error = 'Invalid login or username'
            return render_template('login.html', error=error)

    elif user_type == "AIRLINE_EMPLOYEE":
        # username and pw of given login info
        query = 'SELECT * FROM airline_staff WHERE username = %s and password = %s' 
        cursor.execute(query, (username, password))
        
        # store query info into data
        data = cursor.fetchone()
        
        # queries where the employee works from
        works_for_query = 'SELECT name FROM works_for WHERE username = %s'
        cursor.execute(works_for_query, (username))
        works_for_data = cursor.fetchone()
        
        cursor.close()
        
        if data and works_for_data:
            # create user session
            session['staff_name'] = data['first_name']
            session['username'] = username
            session['user_type'] = user_type
            session['employee_airline'] = works_for_data['name']
            return redirect(url_for('staff_home'))
        else:
            error = 'Invalid login or username'
            return render_template('login.html', error = error)            


# Authenticates staff's registration
@app.route('/staff_registerAuth', methods=['GET', 'POST'])
def staff_registerAuth():
    # grabs information from the forms
    username = request.form['username']
    password = request.form['password']
    password = hashlib.md5(password.encode('utf-8')).hexdigest()
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    date_of_birth = request.form['date_of_birth']
    phone_number = request.form['phone_number']

    # cursor used to send queries
    cursor = conn.cursor()
    # executes query
    # Used to check if the given username already holds an account
    query = 'SELECT * FROM airline_staff WHERE username = %s'
    cursor.execute(query, (username))
    # stores the results in a variable
    data = cursor.fetchone()
    # use fetchall() if you are expecting more than 1 data row
    # Used to check if the registration attempt is associated with an existing employee:
    query2 = 'SELECT * FROM works_for WHERE username = %s'
    cursor.execute(query2, (username))
    data2 = cursor.fetchone()
    error = None
    # If query2 returns data, then the employee exists and is authorized to open an account
    if data2:
        if data:
            # If query returns data, then user exists
            error = "This user already exists"
            return render_template('staff_registration.html', error=error)
        else:
            ins = 'INSERT INTO airline_staff VALUES(%s, %s, %s, %s, %s)'
            cursor.execute(ins, (username, password, first_name, last_name, date_of_birth))
            if phone_number:
                ins_phone = 'INSERT INTO staff_phone VALUES(%s, %s)'
                cursor.execute(ins_phone, (username, phone_number))
            conn.commit()
            cursor.close()
            return render_template('index.html')
    else:  # if no entry in works_for exists: not registered as employee
        error = "Invalid username. Only employed airline staff can register for a staff account!"
        return render_template('staff_registration.html', error=error)


# Authenticates the customer's registration
@app.route('/cust_registerAuth', methods=['GET', 'POST'])
def cust_registerAuth():
    # grabs information from the forms
    email = request.form['email']
    name = request.form['name']
    password = request.form['password']
    password = hashlib.md5(password.encode('utf-8')).hexdigest()
    building_num = request.form['building_num']
    street = request.form['street']
    city = request.form['city']
    state = request.form['state']
    phone_number = request.form['phone_number']
    passport_number = request.form['passport_number']
    passport_expiration = request.form['passport_expiration']
    passport_country = request.form['passport_country']
    date_of_birth = request.form['date_of_birth']
    # cursor used to send queries
    cursor = conn.cursor()
    # executes query
    query = 'SELECT * FROM customer WHERE email = %s'
    cursor.execute(query, (email))
    # stores the results in a variable
    data = cursor.fetchone()
    # use fetchall() if you are expecting more than 1 data row
    error = None
    if data:
        # If the previous query returns data, then user exists
        error = "This user already exists"
        return render_template('register.html', error=error)
    else: 
        ins = 'INSERT INTO customer VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
        cursor.execute(ins,
                       (email, name, password, building_num, street, city,
                        state, phone_number, passport_number, passport_expiration,
                        passport_country, date_of_birth))
        conn.commit()
        cursor.close()
        return render_template('index.html')


@app.route('/staff_home', methods=['GET', 'POST'])
def staff_home():
    username = session['username']
    name = session['staff_name']
    airline_name = session['employee_airline']

    cursor = conn.cursor()
    thirty_day_query = 'SELECT ID, airline_name, flight_num, dept_date_time, status, origin_airport, origin_city, origin_country, destination_airport, destination_city, destination_country FROM origin_destination_name WHERE airline_name=%s and dept_date_time <= DATE_ADD(NOW(), INTERVAL 30 DAY) AND dept_date_time >= NOW()'

    cursor.execute(thirty_day_query, (airline_name))
    flight_data = cursor.fetchall()

    session['flight_data'] = flight_data
    cursor.close()  
    now = pytz.utc.localize(datetime.datetime.now())
    thirty_days = relativedelta(days=30)
    in_thirty_days = now + thirty_days
    begin_date = now.date()
    end_date = in_thirty_days.date()

    # Get most frequent customer from last year:
    last_year = now - relativedelta(years=1)
    get_frequent_customer = 'SELECT name, total_purchases '\
                            'FROM last_year_customer_purchases '\
                            'WHERE airline=%s '\
                            'AND total_purchases=(SELECT MAX(total_purchases) '\
                                                 'FROM last_year_customer_purchases '\
                                                 'WHERE airline=%s) '
    cursor = conn.cursor()
    cursor.execute(get_frequent_customer, (airline_name, airline_name))
    most_freq_customer = cursor.fetchone()
    top_customer = None
    top_customer_total_purchases = None
    if most_freq_customer:
        top_customer = most_freq_customer['name']
        top_customer_total_purchases = most_freq_customer['total_purchases']
        session['top_customer'] = top_customer
        session['top_customer_total_purchases'] = top_customer_total_purchases
    return render_template('staff_home.html', username=username, name=name, employee_airline=airline_name,
                           last_year=last_year.strftime('%Y'), top_customer=top_customer, top_total_tickets=top_customer_total_purchases,
                           range=True, begin_date=begin_date, end_date=end_date, flight_data=flight_data)


@app.route('/show_all_flights', methods=['GET', 'POST'])
def show_all_flights():
    username = session['username']
    name = session['staff_name']
    airline_name = session['employee_airline']
    
    cursor = conn.cursor()
    
    all_day_query = 'SELECT ID, airline_name, flight_num, dept_date_time, status, origin_airport, origin_city, origin_country, destination_airport, destination_city, destination_country FROM origin_destination_name WHERE airline_name=%s'
    
    cursor.execute(all_day_query, (airline_name))
    flight_data = cursor.fetchall()
    
    session['flight_data'] = flight_data
    cursor.close()

    # Load top customer:
    top_customer = None
    top_customer_total_purchases = None
    last_year = None
    if session.get('top_customer'):
        top_customer = session['top_customer']
        top_customer_total_purchases = session['top_customer_total_purchases']
        now = pytz.utc.localize(datetime.datetime.now())
        last_year = now - relativedelta(years=1)
        last_year = last_year.strftime('%Y')
    return render_template('staff_home.html', username=username, name=name, range=False, employee_airline=airline_name,
                           top_customer=top_customer, top_total_tickets=top_customer_total_purchases,
                           last_year=last_year, all_flights=True, flight_data=flight_data)


@app.route('/flight_date_range', methods=['GET', 'POST'])
def flight_date_range():
    username = session['username']
    name = session['staff_name']
    airline_name = session['employee_airline']
    begin_date = request.form['begin_date']
    end_date = request.form['end_date']
    begin_date_obj = datetime.datetime.strptime(begin_date, '%Y-%m')
    end_date_obj = datetime.datetime.strptime(end_date, '%Y-%m')
    x = begin_date_obj
    flights = []
    while x <= end_date_obj:
        get_flights_in_range = 'SELECT ID, airline_name, flight_num, dept_date_time, status, ' \
                               'origin_airport, origin_city, origin_country, destination_airport, ' \
                               'destination_city, destination_country ' \
                               'FROM origin_destination_name ' \
                               'WHERE airline_name=%s '\
                               'AND MONTH(dept_date_time)=%s '\
                               'AND YEAR(dept_date_time)=%s'

        cursor = conn.cursor()
        print(x.strftime('%m'))
        print(x.strftime('%Y'))
        cursor.execute(get_flights_in_range, (airline_name, x.strftime('%m'), x.strftime('%Y')))
        flight_data = cursor.fetchall()
        cursor.close()
        for flight in flight_data:
            flights.append(flight)
        x = x + relativedelta(months=1)

    # Load top customer:
    top_customer = None
    top_customer_total_purchases = None
    last_year = None
    if session.get('top_customer'):
        top_customer = session['top_customer']
        top_customer_total_purchases = session['top_customer_total_purchases']
        now = pytz.utc.localize(datetime.datetime.now())
        last_year = now - relativedelta(years=1)
        last_year = last_year.strftime('%Y')
    if flight_data:
        session['flight_data'] = flights
        return render_template('staff_home.html', username=username, name=name, range=True,
                                employee_airline=airline_name, top_customer=top_customer, last_year=last_year,
                                top_total_tickets=top_customer_total_purchases, begin_date=begin_date,
                                end_date=end_date, flight_data=flights)
    else:
        return render_template('staff_home.html', username=username, name=name, range=True,
                                top_customer=top_customer, last_year=last_year,
                                top_total_tickets=top_customer_total_purchases,
                                employee_airline=airline_name, begin_date=begin_date,
                                end_date=end_date, error='No flights found within chosen range.')


@app.route('/flight_origin_destination', methods=['GET', 'POST'])
def flight_origin_destination():
    username = session['username']
    name = session['staff_name']
    airline_name = session['employee_airline']
    origin = request.form['origin']
    destination = request.form['destination']
    flight_data = None
    if origin and destination:
        origin_destination_query = 'SELECT ID, airline_name, flight_num, dept_date_time, status, ' \
                                   'origin_airport, origin_city, origin_country, destination_airport, ' \
                                   'destination_city, destination_country ' \
                                   'FROM origin_destination_name ' \
                                   'WHERE (origin_city IN '\
                                   '(SELECT origin_city '\
                                   'FROM origin_destination_name '\
                                   'WHERE origin_city=%s '\
                                   'OR origin_airport=%s) '\
                                   'AND airline_name=%s '\
                                   'AND destination_city IN '\
                                   '(SELECT destination_city '\
                                   'FROM origin_destination_name '\
                                   'WHERE destination_city=%s '\
                                   'OR destination_airport=%s)) '
        cursor = conn.cursor()
        cursor.execute(origin_destination_query, (origin, origin, airline_name, destination, destination))
        flight_data = cursor.fetchall()
        cursor.close()
    elif origin:
        origin_query = 'SELECT ID, airline_name, flight_num, dept_date_time, status, ' \
                       'origin_airport, origin_city, origin_country, destination_airport, ' \
                       'destination_city, destination_country ' \
                       'FROM origin_destination_name ' \
                       'WHERE (origin_city IN '\
                       '(SELECT origin_city '\
                       'FROM origin_destination_name '\
                       'WHERE origin_city=%s '\
                       'OR origin_airport=%s) '\
                       'AND airline_name=%s) '
        cursor = conn.cursor()
        cursor.execute(origin_query, (origin, origin, airline_name))
        flight_data = cursor.fetchall()
        cursor.close()
    elif destination:
        destination_query = 'SELECT ID, airline_name, flight_num, dept_date_time, status, ' \
                            'origin_airport, origin_city, origin_country, destination_airport, ' \
                            'destination_city, destination_country ' \
                            'FROM origin_destination_name ' \
                            'WHERE (destination_city IN '\
                            '(SELECT destination_city '\
                            'FROM origin_destination_name '\
                            'WHERE destination_city=%s '\
                            'OR destination_airport=%s) '\
                            'AND airline_name=%s) '
        cursor = conn.cursor()
        cursor.execute(destination_query, (destination, destination, airline_name))
        flight_data = cursor.fetchall()
        cursor.close()

    # Load top customer:
    top_customer = None
    top_customer_total_purchases = None
    last_year = None
    if session.get('top_customer'):
        top_customer = session['top_customer']
        top_customer_total_purchases = session['top_customer_total_purchases']
        now = pytz.utc.localize(datetime.datetime.now())
        last_year = now - relativedelta(years=1)
        last_year = last_year.strftime('%Y')
    if flight_data:
        session['flight_data'] = flight_data
        return render_template('staff_home.html', username=username, name=name, range=False,
                                top_customer=top_customer, last_year=last_year,
                                top_total_tickets=top_customer_total_purchases,
                                employee_airline=airline_name, flight_data=flight_data)
    else:
        return render_template('staff_home.html', username=username, name=name, range=False,
                                top_customer=top_customer, last_year=last_year,
                                top_total_tickets=top_customer_total_purchases,
                                employee_airline=airline_name, error='No flights found from/to chosen locations.')


@app.route('/passengers', methods=['GET', 'POST'])
def passengers():
    flight_data = session['flight_data']
    employee_airline = session['employee_airline']
    flight_counter = request.form['check_pass']
    flight_to_show = flight_data[int(flight_counter)]
    session['flight_to_show'] = flight_to_show
    
    airplane_id = flight_to_show['ID']
    
    cursor = conn.cursor()
    query = 'SELECT DISTINCT name, email FROM purchased NATURAL JOIN customer NATURAL JOIN ticket_flight ' \
            'WHERE airplane_id = %s '\
            'AND airline=%s '\
            'AND flight_num=%s '\
            'AND dept_date_time=%s '
    cursor.execute(query, (airplane_id, flight_to_show['airline_name'], flight_to_show['flight_num'],
                           flight_to_show['dept_date_time']))
    passenger_data = cursor.fetchall()
    cursor.close()
    
    isEmpty = False
    session['passenger_data'] = passenger_data
    if cursor.rowcount == 0:
        isEmpty = True
    return render_template('show_passengers.html', passenger_data=passenger_data, airline=employee_airline,
                           airplane_id=airplane_id, flight_num=flight_to_show['flight_num'],
                           dept_date_time=flight_to_show['dept_date_time'], isEmpty=isEmpty)


@app.route('/show_customers_flights', methods=['GET', 'POST'])
def show_customers_flights():
    employee_airline = session['employee_airline']
    flight_to_show = session['flight_to_show']
    passenger_data = session['passenger_data']
    passenger_number = request.form['pass_counter']
    passenger_to_show = passenger_data[int(passenger_number)]
    all_pass_flights_query = 'SELECT * '\
                             'FROM purchased NATURAL JOIN ticket_flight '\
                             'WHERE email=%s AND airline=%s'
    cursor = conn.cursor()
    cursor.execute(all_pass_flights_query, (passenger_to_show['email'], employee_airline))

    # Get flight data for each of the passengers purchased flights:
    all_passenger_flights = cursor.fetchall()
    customer_flights = []
    for flight in all_passenger_flights:
        query = 'SELECT * '\
                'FROM origin_destination_name '\
                'WHERE ID=%s AND airline_name=%s '\
                'AND flight_num=%s AND dept_date_time=%s '
        cursor.execute(query, (flight['airplane_ID'], flight['airline'], flight['flight_num'], flight['dept_date_time']))
        flight_to_add = cursor.fetchone()
        customer_flights.append(flight_to_add)
    return render_template('show_passengers.html', passenger_data=passenger_data, airline=employee_airline,
                           airplane_id=flight_to_show['ID'], flight_num=flight_to_show['flight_num'],
                           dept_date_time=flight_to_show['dept_date_time'], isEmpty=False,
                           passenger_to_show=passenger_to_show, customer_flights=customer_flights)


@app.route('/airport_adder', methods=['GET', 'POST'])
def airport_adder():
    cursor = conn.cursor()
    show_airport_query = 'SELECT * FROM airport'
    cursor.execute(show_airport_query)
    
    cursor.close()
    data = cursor.fetchall()
    return render_template('add_airport.html', data=data)


@app.route('/add_airport', methods=['GET', 'POST'])
def add_airport():
    code = request.form['code']
    name = request.form['name']
    city = request.form['city']
    country = request.form['country']
    flight_type = request.form['type']
    
    cursor = conn.cursor()
    insert_query = 'INSERT INTO airport VALUES (%s, %s, %s, %s, %s)'
    cursor.execute(insert_query, (code, name, city, country, flight_type))
    conn.commit() 
    
    show_airport = 'SELECT * FROM airport'
    cursor.execute(show_airport)
    _data = cursor.fetchall()
    cursor.close()
    
    success = True

    return render_template('add_airport.html', success=success, data=_data)


@app.route('/flight_ratings', methods=['GET', 'POST'])
def flight_ratings():
    flight_data = session['flight_data']
    flight_counter = request.form['view_ratings']
    flight_to_view = flight_data[int(flight_counter)]
    session['flight_to_view'] = flight_to_view
    return redirect(url_for('ratings_page'))
    
    
@app.route('/ratings_page', methods=['GET', 'POST'])
def ratings_page():
    employee_airline = session['employee_airline']
    flight_to_view = session['flight_to_view']
    ID = flight_to_view['ID']
    
    
    cursor = conn.cursor()
    query = 'SELECT * from feedback WHERE airline = %s and ID = %s'
    cursor.execute(query, (employee_airline, ID))
    data = cursor.fetchall()
    cursor.close()
    
    print(data)
    
    return render_template('flight_ratings.html', employee_airline=employee_airline, ID = flight_to_view['ID'], data = data)
    

@app.route('/flight_adder', methods=['GET', 'POST'])
def flight_adder():
    airline_name = session['employee_airline']
    return render_template('create_flight.html', employee_airline=airline_name)


@app.route('/create_flight', methods=['GET', 'POST'])
def create_flight():
    ID = request.form['ID']
    airline_name = session['employee_airline']
    flight_num = request.form['flight_num']
    dept_date_time = request.form['dept_date_time']
    dept_date_time_str = dept_date_time[:-6] + " " + dept_date_time[-5:] + ":00"
    origin_code = request.form['origin_code']
    destination_code = request.form['destination_code']
    arr_date_time = request.form['arr_date_time']
    arr_date_time_str = arr_date_time[:-6] + " " + arr_date_time[-5:] + ":00"
    base_price = request.form['base_price']
    status = request.form['status']
    
    # if submit button is clicked: also have a message that displays yes, you have succesfully added flight
    insert_flight = 'INSERT INTO flight '\
                       'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
    cursor = conn.cursor()
    cursor.execute(insert_flight, (ID, airline_name, flight_num, dept_date_time_str, origin_code, destination_code, arr_date_time_str, base_price, status, "0"))
    conn.commit()
    cursor.close()
    
    success = True
    return render_template('create_flight.html', success=success, employee_airline=airline_name)


@app.route('/modify_status', methods=['GET', 'POST'])
def modify_status():
    flight_data = session['flight_data']
    flight_counter = request.form['modify_flight_status']
    flight_to_modify = flight_data[int(flight_counter)]
    session['flight_to_modify'] = flight_to_modify
    employee_airline = session['employee_airline']
    
    #if submit button has been clicked
    return render_template('modify_status.html', flight_to_modify = flight_to_modify, employee_airline=employee_airline)


@app.route('/new_status', methods=['GET', 'POST'])
def new_status():
    flight_to_modify = session['flight_to_modify']
    employee_airline = session['employee_airline']
    # will retreive ONTIME or DELASYED
    new_status = request.form['status']
    
    status_query = 'UPDATE flight '\
             'SET status = %s '\
             'WHERE ID=%s AND name=%s AND flight_num=%s AND dept_date_time=%s '
    cursor = conn.cursor()
    cursor.execute(status_query, (new_status, flight_to_modify['ID'], employee_airline, flight_to_modify['flight_num'], flight_to_modify['dept_date_time']))
    conn.commit()
    cursor.close()
    # if query runs
    success = True
    # update the table that shows in modify_status
    flight_to_modify['status'] = new_status
    # not rly needed session
    session['flight_to_modify']['status'] = flight_to_modify['status']
    
    return render_template('modify_status.html', flight_to_modify=flight_to_modify, employee_airline=employee_airline, success =success)


@app.route('/airplane_adder', methods=['GET', 'POST'])
def airplane_adder():
    employee_airline = session['employee_airline']
    # get all the airplane data of employee
    cursor = conn.cursor()
    show_airplane_query = 'SELECT * FROM airplane WHERE name = %s'
    cursor.execute(show_airplane_query, (employee_airline))
    
    cursor.close()
    airplane_data = cursor.fetchall()
    return render_template('add_airplane.html', employee_airline=employee_airline, airplane_data=airplane_data)


@app.route('/add_airplane', methods=['GET', 'POST'])
def add_airplane():
    employee_airline = session['employee_airline']
    
    ID = request.form['ID']
    num_seats = request.form['num_seats']
    manufacturer = request.form['manufacturer']
    age = request.form['age']

    # add airplane into database
    cursor = conn.cursor()
    add_airplane_query = 'INSERT INTO airplane '\
                       'VALUES (%s, %s, %s, %s, %s)'
    cursor.execute(add_airplane_query, (ID, employee_airline, num_seats, manufacturer, age))
    conn.commit() 
    
    show_airplane_query = 'SELECT * FROM airplane WHERE name = %s'
    cursor.execute(show_airplane_query, (employee_airline))
    airplane_data = cursor.fetchall()
    cursor.close()
    
    success = True

    return render_template('add_airplane.html', success=success, airplane_data=airplane_data,employee_airline=employee_airline)


@app.route('/top_destinations', methods=['GET', 'POST'])
def top_destinations():
    airline_name = session['employee_airline']
    now = pytz.utc.localize(datetime.datetime.now())
    one_year = relativedelta(years=1)
    year_ago = now - one_year

    top_dest1_3months = None
    top_dest2_3months = None
    top_dest3_3months = None
    top_dest1_year = None
    top_dest2_year = None
    top_dest3_year = None
    cursor = conn.cursor()
    top_dest_query = 'SELECT destination_city '\
                        'FROM destination_reservations_3_months '\
                        'WHERE airline_name=%s '\
                        'AND total_tickets=(SELECT MAX(total_tickets)' \
                                           'FROM destination_reservations_3_months '\
                                           'WHERE airline_name=%s) '
    cursor.execute(top_dest_query, (airline_name, airline_name))
    top_dest1_3months = cursor.fetchone()
    if top_dest1_3months:
        top_dest1_3months = top_dest1_3months['destination_city']
        print(top_dest1_3months)
        top_dest_query = 'SELECT destination_city '\
                         'FROM destination_reservations_3_months '\
                         'WHERE airline_name=%s '\
                         'AND destination_city<>%s '\
                         'AND total_tickets=(SELECT MAX(total_tickets) ' \
                                            'FROM destination_reservations_3_months '\
                                            'WHERE airline_name=%s '\
                                            'AND destination_city<>%s)'
        cursor.execute(top_dest_query, (airline_name, top_dest1_3months, airline_name, top_dest1_3months))
        top_dest2_3months = cursor.fetchone()
        if top_dest2_3months:
            top_dest2_3months = top_dest2_3months['destination_city']
            print(top_dest2_3months)
            top_dest_query = 'SELECT destination_city '\
                             'FROM destination_reservations_3_months '\
                             'WHERE airline_name=%s '\
                             'AND destination_city<>%s '\
                             'AND destination_city<>%s '\
                             'AND total_tickets=(SELECT MAX(total_tickets) ' \
                                                'FROM destination_reservations_3_months '\
                                                'WHERE airline_name=%s '\
                                                'AND destination_city<>%s '\
                                                'AND destination_city<>%s) '
            cursor.execute(top_dest_query, (airline_name, top_dest1_3months, top_dest2_3months, airline_name,
                                            top_dest1_3months, top_dest2_3months))
            top_dest3_3months = cursor.fetchone()
            if top_dest3_3months:
                top_dest3_3months = top_dest3_3months['destination_city']
                print(top_dest3_3months)

    top_dest_query = 'SELECT destination_city '\
                     'FROM destination_reservations_year '\
                     'WHERE airline_name=%s '\
                     'AND total_tickets=(SELECT MAX(total_tickets)' \
                                        'FROM destination_reservations_year '\
                                        'WHERE airline_name=%s) '
    cursor.execute(top_dest_query, (airline_name, airline_name))
    top_dest1_year = cursor.fetchone()
    if top_dest1_year:
        top_dest1_year = top_dest1_year['destination_city']
        print(top_dest1_year)
        top_dest_query = 'SELECT destination_city '\
                         'FROM destination_reservations_year '\
                         'WHERE airline_name=%s '\
                         'AND destination_city<>%s '\
                         'AND total_tickets=(SELECT MAX(total_tickets) ' \
                                            'FROM destination_reservations_year '\
                                            'WHERE airline_name=%s '\
                                            'AND destination_city<>%s)'
        cursor.execute(top_dest_query, (airline_name, top_dest1_year, airline_name, top_dest1_year))
        top_dest2_year = cursor.fetchone()
        if top_dest2_year:
            top_dest2_year = top_dest2_year['destination_city']
            print(top_dest2_year)
            top_dest_query = 'SELECT destination_city '\
                             'FROM destination_reservations_year '\
                             'WHERE airline_name=%s '\
                             'AND destination_city<>%s '\
                             'AND destination_city<>%s '\
                             'AND total_tickets=(SELECT MAX(total_tickets) ' \
                                                'FROM destination_reservations_year '\
                                                'WHERE airline_name=%s '\
                                                'AND destination_city<>%s '\
                                                'AND destination_city<>%s)'
            cursor.execute(top_dest_query, (airline_name, top_dest1_year, top_dest2_year, airline_name,
                                            top_dest1_year, top_dest2_year))
            top_dest3_year = cursor.fetchone()
            if top_dest3_year:
                top_dest3_year = top_dest3_year['destination_city']
                print(top_dest3_year)
    cursor.close()
    return render_template('top_destinations.html', employee_airline=airline_name, destination1=top_dest1_3months,
                           destination2=top_dest2_3months, destination3= top_dest3_3months,
                           last_year=year_ago.strftime('%Y'), destination4=top_dest1_year, destination5=top_dest2_year,
                           destination6=top_dest3_year)


@app.route('/revenue', methods=['GET', 'POST'])
def revenue():
    airline = session['employee_airline']
    now = pytz.utc.localize(datetime.datetime.now())
    one_year = relativedelta(years=1)
    year_ago = now - one_year

    now = pytz.utc.localize(datetime.datetime.now())
    one_month = relativedelta(months=1)
    month_ago = now - one_month
    print(month_ago)
    last_month_query = 'SELECT SUM(sold_price) FROM purchased NATURAL JOIN ticket_flight '\
                       'WHERE airline=%s AND MONTH(purchase_date_time)=MONTH(%s) '\
                       'AND YEAR(purchase_date_time)=YEAR(%s)'
    cursor = conn.cursor()
    cursor.execute(last_month_query, (airline, month_ago, month_ago))
    last_month_revenue = cursor.fetchone()['SUM(sold_price)']
    if not last_month_revenue:
        last_month_revenue = 0
    print(last_month_revenue)

    last_year_query = 'SELECT SUM(sold_price) FROM purchased NATURAL JOIN ticket_flight '\
                      'WHERE airline=%s AND YEAR(purchase_date_time)=YEAR(%s)'
    cursor.execute(last_year_query, (airline, year_ago))
    last_year_revenue = cursor.fetchone()['SUM(sold_price)']
    if not last_year_revenue:
        last_year_revenue = 0

    first_class = 'SELECT SUM(sold_price) FROM purchased NATURAL JOIN ticket_flight, ticket '\
                  'WHERE ticket.ID=ticket_ID AND airline=%s AND travel_class=%s'
    cursor.execute(first_class, (airline, 'FIRST CLASS'))
    first_class_revenue = cursor.fetchone()['SUM(sold_price)']
    if not first_class_revenue:
        first_class_revenue = 0

    business_class = 'SELECT SUM(sold_price) FROM purchased NATURAL JOIN ticket_flight, ticket '\
                     'WHERE ticket.ID=ticket_ID AND airline=%s AND travel_class=%s'
    cursor.execute(business_class, (airline, 'BUSINESS CLASS'))
    business_class_revenue = cursor.fetchone()['SUM(sold_price)']
    if not business_class_revenue:
        business_class_revenue = 0

    economy_class = 'SELECT SUM(sold_price) FROM purchased NATURAL JOIN ticket_flight, ticket '\
                     'WHERE ticket.ID=ticket_ID AND airline=%s AND travel_class=%s'
    cursor.execute(economy_class, (airline, 'ECONOMY CLASS'))
    economy_class_revenue = cursor.fetchone()['SUM(sold_price)']
    if not economy_class_revenue:
       economy_class_revenue = 0
    cursor.close()
    return render_template('revenue.html', employee_airline=airline, last_month=month_ago.strftime('%B'),
                           year=month_ago.strftime('%Y'), last_month_revenue=last_month_revenue,
                           last_year_revenue=last_year_revenue, last_year=year_ago.strftime('%Y'),
                           first_class_revenue=first_class_revenue, business_class_revenue=business_class_revenue,
                           economy_class_revenue=economy_class_revenue)


@app.route('/customer_home')
def customer_home():
    username = session['username']
    name = session['name']
    user_type = session['user_type']
    cursor = conn.cursor()
    future_flight_query = 'SELECT * FROM purchased NATURAL JOIN ticket_flight NATURAL JOIN origin_destination_name '\
                          'WHERE email=%s '\
                          'AND dept_date_time>NOW()'
    cursor.execute(future_flight_query, (username))
    # stores the results in a variable
    data = cursor.fetchall()
    # use fetchall() if you are expecting more than 1 data row
    cursor.close()
    session['future_flights'] = data
    # cursor.execute(query, (username))
    # data1 = cursor.fetchall()
    # for each in data1:
    #    print(each['blog_post'])
    # cursor.close()
    return render_template('customer_home.html', username=username, flights=data, name=name)  # , posts=data1)


@app.route('/purchase_history', methods=['GET', 'POST'])
def purchase_history():
    email = session['username']
    name = session['name']

    # By default - show 1 year back:
    now = pytz.utc.localize(datetime.datetime.now())
    one_year = relativedelta(years=1)
    year_ago = now - one_year
    begin_date = year_ago.date()
    end_date = now.date()

    months = {}
    x = begin_date
    while x <= end_date:
        get_amount_spent = 'SELECT SUM(sold_price) ' \
                           'FROM purchased NATURAL JOIN ticket_flight NATURAL JOIN origin_destination_name ' \
                           'WHERE email=%s AND MONTH(purchase_date_time)=%s AND YEAR(purchase_date_time)=%s '
        cursor = conn.cursor()
        print(x.strftime('%m'))
        print(x.strftime('%Y'))
        cursor.execute(get_amount_spent, (email, x.strftime('%m'), x.strftime('%Y')))
        amount = cursor.fetchone()
        print(amount)
        if amount['SUM(sold_price)']:
            amount_spent = float(amount['SUM(sold_price)'])
            months[x.strftime('%B') + ', ' + x.strftime('%Y')] = amount_spent
        else:
            months[x.strftime('%B') + ', ' + x.strftime('%Y')] = 0
        cursor.close()
        x = x + relativedelta(months=1)

    cursor = conn.cursor()
    query = 'SELECT * ' \
            'FROM purchased NATURAL JOIN ticket_flight NATURAL JOIN origin_destination_name ' \
            'WHERE email=%s AND DATE(purchase_date_time)>DATE(%s) '
    cursor.execute(query, (email, year_ago))
    purchases = cursor.fetchall()
    conn.commit()
    cursor.close()

    cursor = conn.cursor()
    query = 'SELECT SUM(sold_price) ' \
            'FROM purchased NATURAL JOIN ticket_flight NATURAL JOIN origin_destination_name ' \
            'WHERE email=%s'
    cursor.execute(query, (email))
    total_spending = cursor.fetchone()
    conn.commit()
    cursor.close()
    return render_template('customer_purchases.html', begin_date=begin_date, end_date=end_date, months=months, flights=purchases,
                           total=total_spending['SUM(sold_price)'], name=name)


@app.route('/spending_date_range', methods=['GET', 'POST'])
def spending_date_range():
    email = session['username']
    name = session['name']
    begin_date = request.form['begin_date']
    end_date = request.form['end_date']
    begin_date_obj = datetime.datetime.strptime(begin_date, '%Y-%m')
    end_date_obj = datetime.datetime.strptime(end_date, '%Y-%m')
    months = {}
    purchases = []
    x = begin_date_obj
    total_spent = 0
    while x <= end_date_obj:
        get_amount_spent = 'SELECT SUM(sold_price) ' \
                           'FROM purchased NATURAL JOIN ticket_flight NATURAL JOIN origin_destination_name ' \
                           'WHERE email=%s AND MONTH(purchase_date_time)=%s AND YEAR(purchase_date_time)=%s '
        cursor = conn.cursor()
        print(x.strftime('%m'))
        print(x.strftime('%Y'))
        cursor.execute(get_amount_spent, (email, x.strftime('%m'), x.strftime('%Y')))
        amount = cursor.fetchone()
        if amount['SUM(sold_price)']:
            amount_spent = float(amount['SUM(sold_price)'])
            months[x.strftime('%B') + ', ' + x.strftime('%Y')] = amount_spent
            total_spent += amount_spent
            print(total_spent)
        else:
            months[x.strftime('%B') + ', ' + x.strftime('%Y')] = 0
        cursor.close()

        get_purchased_flights = 'SELECT * ' \
                                'FROM purchased NATURAL JOIN ticket_flight NATURAL JOIN origin_destination_name ' \
                                'WHERE email=%s AND MONTH(purchase_date_time)=%s AND YEAR(purchase_date_time)=%s '
        cursor = conn.cursor()
        cursor.execute(get_purchased_flights, (email, x.strftime('%m'), x.strftime('%Y')))
        monthly_purchases = cursor.fetchall()
        for purchase in monthly_purchases:
            purchases.append(purchase)
            print(purchase)
        cursor.close()
        x = x + relativedelta(months=1)

    return render_template('customer_purchases.html', begin_date=begin_date, end_date=end_date, months=months,
                           name=name, flights=purchases, total=total_spent)


@app.route('/cancel_trip', methods=['GET', 'POST'])
def cancel_trip():
    flight = request.form['flight_to_cancel']
    print(flight)
    flights = session['future_flights']
    name = session['name']
    print(flights[int(flight)])

    # First, we check if flight is more than 24 hours away:
    now = pytz.utc.localize(datetime.datetime.now())
    one_day = datetime.timedelta(days=1)
    tomorrow = now + one_day

    if flights[int(flight)]['dept_date_time'] > tomorrow:
        cursor = conn.cursor()
        query1 = 'DELETE FROM ticket_flight '\
                 'WHERE ticket_ID=%s '
        #'IF DATE(%s)>DATE_ADD(DATE(NOW()), INTERVAL 1 DAY) THEN '\
        #'END IF'
        cursor.execute(query1, (flights[int(flight)]['ticket_ID']))
        conn.commit()
        cursor.close()

        cursor = conn.cursor()
        query2 = 'DELETE FROM purchased '\
                 'WHERE ticket_ID=%s '
        #'IF %s NOT IN (SELECT ticket_ID FROM ticket_flight) THEN '\
        #'END IF'
        cursor.execute(query2, (flights[int(flight)]['ticket_ID']))
        conn.commit()
        cursor.close()

        cursor = conn.cursor()
        query3 = 'DELETE FROM ticket '\
                 'WHERE ID=%s '
        #'IF %s NOT IN (SELECT ticket_ID FROM purchased) THEN '\
        #'END IF'
        cursor.execute(query3, (flights[int(flight)]['ticket_ID']))
        conn.commit()
        cursor.close()

        cursor = conn.cursor()
        query4 = 'UPDATE flight '\
                 'SET seats_booked = seats_booked-1 '\
                 'WHERE ID=%s AND name=%s AND flight_num=%s AND dept_date_time=%s '

        cursor.execute(query4, (flights[int(flight)]['ID'],
                                flights[int(flight)]['airline'], flights[int(flight)]['flight_num'],
                                flights[int(flight)]['dept_date_time']))
        conn.commit()
        cursor.close()

        cursor = conn.cursor()
        future_flight_query = 'SELECT * FROM purchased NATURAL JOIN ticket_flight NATURAL JOIN origin_destination_name '\
                              'WHERE email=%s '\
                              'AND dept_date_time>NOW()'
        cursor.execute(future_flight_query, (session['username']))
        flights = cursor.fetchall()
        session['future_flights'] = flights
        cursor.close()
        return render_template('customer_home.html', name=name, flights=flights, flight_counter=0, canceled=True)
    else:
        error = 'Flights departing in 24 hours or less can not be cancelled, sorry'
        return render_template('customer_home.html', name=name, flights=flights, flight_counter=0, error=error)


@app.route('/rate_trip', methods=['GET', 'POST'])
def rate_trip():
    email = session['username']
    name = session['name']
    cursor = conn.cursor()
    query = 'SELECT * ' \
            'FROM purchased NATURAL JOIN ticket_flight NATURAL JOIN origin_destination_name ' \
            'WHERE email=%s '\
            'AND dept_date_time<DATE(NOW())'

    cursor.execute(query, (email))
    past_trips = cursor.fetchall()
    conn.commit()
    cursor.close()
    session['flights'] = past_trips
    # cursor = conn.cursor()
    # query = 'SELECT SUM(sold_price) ' \
    #         'FROM purchased NATURAL JOIN ticket_flight NATURAL JOIN origin_destination_name ' \
    #         'WHERE email=%s'
    # cursor.execute(query, (email))
    # total_spending = cursor.fetchone()
    # conn.commit()
    # cursor.close()
    return render_template('rate_trip.html', name=name, flights=past_trips, trip=None)


@app.route('/rate_this_trip', methods=['GET', 'POST'])
def rate_this_trip():
    flight = request.form['flight_to_rate']
    flights = session['flights']
    name = session['name']
    session['flight_to_rate'] = flight
    return render_template('rate_trip.html', name=name, flights=flights, trip=flight)


@app.route('/add_feedback', methods=['GET', 'POST'])
def add_feedback():
    feedback = request.form['feedback']
    flights = session['flights']
    name = session['name']
    email = session['username']
    flight = session['flight_to_rate']
    has_trip_been_rated = 'SELECT * FROM feedback '\
                          'WHERE email=%s AND ID=%s '\
                          'AND airline=%s AND flight_num=%s '\
                          'AND dept_date_time=%s '
    cursor = conn.cursor()
    cursor.execute(has_trip_been_rated, (email, flights[int(flight)]['airplane_ID'],
                                        flights[int(flight)]['airline'], flights[int(flight)]['flight_num'],
                                        flights[int(flight)]['dept_date_time']))
    trip = cursor.fetchone()
    cursor.close()
    if trip:
        return render_template('rate_trip.html', name=name, flights=flights, trip=None, error='Trip already rated!')
    else:
        add_feedback_query = 'INSERT INTO feedback '\
                             'VALUES (%s, %s, %s, %s, %s, %s)'
        # print(flights[int(flight)]['airplane_ID'])
        # print(flights[int(flight)]['airline'])
        # print(flights[int(flight)]['flight_num'])
        # print(flights[int(flight)]['dept_date_time'])
        cursor = conn.cursor()
        cursor.execute(add_feedback_query, (email, flights[int(flight)]['airplane_ID'],
                                            flights[int(flight)]['airline'], flights[int(flight)]['flight_num'],
                                            flights[int(flight)]['dept_date_time'], feedback))
        conn.commit()
        cursor.close()
        print('feedback given')
        print(name)
        print(flights)
        print(feedback)
        return render_template('rate_trip.html', name=name, flights=flights, trip=None, rated_flight=flights[int(flight)], feedback=feedback)


@app.route('/home')
def home():
    username = session['username']
    user_type = session['user_type']
    # cursor = conn.cursor();
    # query = ''
    if user_type == 'AIRLINE_EMPLOYEE':
        query = 'SELECT * from airline_staff'
    elif user_type == 'CUSTOMER':
        query = 'SELECT * from customer'
    # cursor.execute(query, (username))
    # data1 = cursor.fetchall()
    # for each in data1:
    #    print(each['blog_post'])
    # cursor.close()
    return render_template('home.html', username=username)  # , posts=data1)


@app.route('/post', methods=['GET', 'POST'])
def post():
    username = session['username']
    cursor = conn.cursor()
    blog = request.form['blog']
    query = 'INSERT INTO blog (blog_post, username) VALUES(%s, %s)'
    cursor.execute(query, (blog, username))
    conn.commit()
    cursor.close()
    return redirect(url_for('home'))


@app.route('/logout')
def logout():
    # session.pop('username')
    session.clear()
    return redirect('/')


app.secret_key = 'some key that you will never guess'
# Run the app on localhost port 5000
# debug = True -> you don't have to restart flask
# for changes to go through, TURN OFF FOR PRODUCTION
if __name__ == "__main__":
    # print(hashlib.md5('hi'.encode('utf-8')).hexdigest())
    # print(hashlib.md5('012345'.encode('utf-8')).hexdigest())
    # print(hashlib.md5('makore1'.encode('utf-8')).hexdigest())
    # print(hashlib.md5('alabama3'.encode('utf-8')).hexdigest())
    print(hashlib.md5('yoyosup'.encode('utf-8')).hexdigest())
    print(hashlib.md5('iloveny'.encode('utf-8')).hexdigest())
    print(hashlib.md5('lkj'.encode('utf-8')).hexdigest())
    print(hashlib.md5('iloveberlin'.encode('utf-8')).hexdigest())
    app.run('127.0.0.1', 5000, debug=True)
