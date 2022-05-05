# Table of Contents

1. [Introduction](#introduction)
2. [File Explanation](#File-Explanation)
3. [Use Cases](#use-cases)

## Introduction

This project was created by DanLongman89 and kingsotn. It simulates a flight web system incoorporating MySQL, Flask, and HTML. This repo only shows the final project uploaded, all original commits, edits, and changes were worked on in the private repository https://github.com/DanLongman89/databasesApp




## File Explanation

### SQL Files

[UPDATED_CREATE_TABLE.sql](https://github.com/kingsotn/flightApp/blob/master/SQLstatements/UPDATED_CREATE_TABLE.sql): File creates the tables in the sql function

[UPDATED_INSERTIONS.SQL](https://github.com/kingsotn/flightApp/blob/master/SQLstatements/UPDATED_INSERTIONS.SQL): Insertions of the data into the table

[daniel_mysql_config.txt](https://github.com/kingsotn/flightApp/blob/master/SQLstatements/daniel_mysql_config.txt): Daniel’s configuration for mySQL

[experimentation.SQL](https://github.com/kingsotn/flightApp/blob/master/SQLstatements/experimentation.SQL): Experimentation files

[kingston_mysql_config.txt](https://github.com/kingsotn/flightApp/blob/master/SQLstatements/kingston_mysql_config.txt): Kingston’s configuration for mySQL

[origin_destination_view](https://github.com/kingsotn/flightApp/blob/master/SQLstatements/origin_destination_view): A SQL view that is used throughout the code

[origin_destination_view.SQL](https://github.com/kingsotn/flightApp/blob/master/SQLstatements/origin_destination_view.SQL): Different views used in our application

### HTML Templates

[add_airplane.html](https://github.com/kingsotn/flightApp/blob/master/templates/add_airplane.html): Page to create an airplane for staff use case

[add_airport.html](https://github.com/kingsotn/flightApp/blob/master/templates/add_airport.html): Page to create an airport for staff use cases

[create_flight.html](https://github.com/kingsotn/flightApp/blob/master/templates/create_flight.html): Page to create a new flight for staff use cases

[customer_home.html](https://github.com/kingsotn/flightApp/blob/master/templates/customer_home.html): Homepage for the customer

[customer_purchases.html](https://github.com/kingsotn/flightApp/blob/master/templates/customer_purchases.html): Shows the customer purchased flights

[customer_registration.html](https://github.com/kingsotn/flightApp/blob/master/templates/customer_registration.html): Redirect page to create a new customer account

[flight_ratings.html](https://github.com/kingsotn/flightApp/blob/master/templates/flight_ratings.html): Views the flight ratings of the selected flight

[flight_search.html](https://github.com/kingsotn/flightApp/blob/master/templates/flight_search.html): Page to search for flights in the system

[index.html](https://github.com/kingsotn/flightApp/blob/master/templates/index.html): Homepage

[login.html](https://github.com/kingsotn/flightApp/blob/master/templates/login.html): Login page for either customer or airline staff

[modify_status.html](https://github.com/kingsotn/flightApp/blob/master/templates/modify_status.html): Modifies the status of a flight (delayed or on-time)

[purchase.html](https://github.com/kingsotn/flightApp/blob/master/templates/purchase.html): Purchase a flight as a customer

[rate_trip.html](https://github.com/kingsotn/flightApp/blob/master/templates/rate_trip.html): Rate a flight trip as a customer

[register.html](https://github.com/kingsotn/flightApp/blob/master/templates/register.html): Register page for either customer or airline staff

[revenue.html](https://github.com/kingsotn/flightApp/blob/master/templates/revenue.html): Shows revenue

[show_passengers.html](https://github.com/kingsotn/flightApp/blob/master/templates/show_passengers.html): Shows passengers of a given flight

[staff_home.html](https://github.com/kingsotn/flightApp/blob/master/templates/staff_home.html): Staff homepage

[staff_registration.html](https://github.com/kingsotn/flightApp/blob/master/templates/staff_registration.html): Register a new staff account

[top_destinations.html](https://github.com/kingsotn/flightApp/blob/master/templates/top_destinations.html): View top destinations for airline

### master

[master.py](https://github.com/kingsotn/flightApp/blob/master/master.py): Backend Python3 code written with Flask






## Use Cases

### Application:

**View Public Info:** All flights could be searched with through the `flight_finder()`. The query uses the view `origin_destination_name`. The query simply selects the flight that was fetched from the forms that were filled out in the html page. Also, the code accounts for future flights, and allows the user to see the flight status. Same queries as View my flights.

**Register:** Registration redirects the customer from the homepage to either `staff_registration()` or `customer_registration()`. Those values are inserted into the database through the SQL query. Passwords are MD5 hashed.

```python
# staff registration
ins = 'INSERT INTO airline_staff VALUES(%s, %s, %s, %s, %s)'
            cursor.execute(ins, (username, password, first_name, last_name, date_of_birth))
            if phone_number:
                ins_phone = 'INSERT INTO staff_phone VALUES(%s, %s)'
                cursor.execute(ins_phone, (username, phone_number))

# customer
ins = 'INSERT INTO customer VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
        cursor.execute(ins,
                       (email, name, password, building_num, street, city,
                        state, phone_number, passport_number, passport_expiration,
                        passport_country, date_of_birth))
```

**Login:** The customer or the airline staff are able to login and have their names stored as a session variable. Their passwords are checked against its MD5 hash retrieved with a query before logging in. Login fails are indicated to the user. All data of the user is retrieved from the `airline_staff, customer` relations, and shown in each homepage.

```python
password = request.form['password']
    password = hashlib.md5(password.encode('utf-8')).hexdigest()
    user_type = request.form['user_type']

query = 'SELECT * FROM customer WHERE email = %s and password = %s'
        cursor.execute(query, (username, password))
```

**Logout:** Returned the html page back to the home page.

### Customer:

**View My flights:** Same as view public info but has additional feature of being able to purchase flights. `flight_finder()` fetched the `origin, destination, dept_date, return_date` for two-way flights. One way did not have `return_date`.

```python
# 2-way flight search query:
'SELECT * FROM origin_destination_name '\
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

# 1-way flight search query:
'SELECT * FROM origin_destination_name '\
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
               'OR destination_airport=%s))
```

**Search for flights:** Same as view public info but has additional feature of being able to purchase flights. 

**Purchase tickets:** Allows you to purchase tickets, and records the tickets purchased in `purchased` relation. First, we check occupancy to make sure flight is not full, and if above 75% occupancy - we raise the price by 25%.

```python
#Check occupancy query:
'SELECT seats_booked, num_seats '\
'FROM flight NATURAL JOIN airplane '\
'WHERE airplane.ID=%s AND flight.name=%s '\
'AND flight_num=%s AND dept_date_time=%s'

#After occupancy test, we allow for user to enter payment information and insert the ticket with the following queries 
#(we generate a unique ticket ID with a random string generator that generates a 6-character ID consisting of upper-case letters and digits):
	'INSERT INTO ticket_flight '\
      'VALUES (%s, %s, %s, %s, %s)'

	'INSERT INTO purchased '\
      'VALUES (%s, %s, NOW(), %s, %s, %s, %s, %s)'

#Increment number of seats booked in the flight associated with the purchase:
'UPDATE flight '\
'SET seats_booked = seats_booked+1 '\
'WHERE ID=%s AND name=%s AND flight_num=%s AND dept_date_time=%s'
```

**Cancel Trip:** We check that the trip is not within 24 hrs before the flight. Delete from tables `ticket_flight, purchased, ticket` and decrement `seats_booked` in  `flight`

```python
query1 = 'DELETE FROM ticket_flight '\
                 'WHERE ticket_ID=%s '

query2 = 'DELETE FROM purchased '\
                 'WHERE ticket_ID=%s '

query3 = 'DELETE FROM ticket '\
                 'WHERE ID=%s '

query4 = 'UPDATE flight '\
                 'SET seats_booked = seats_booked-1 '\
                 'WHERE ID=%s AND name=%s AND flight_num=%s AND dept_date_time=%s '
```

**Give Comments:** First query gets flights that have taken place, second query checks if the trip has been rated before, and the third allows you to insert if it has not been rated into `feedback`

```python
query = 'SELECT * ' \
            'FROM purchased NATURAL JOIN ticket_flight NATURAL JOIN origin_destination_name ' \
            'WHERE email=%s '\
            'AND dept_date_time<DATE(NOW())'

has_trip_been_rated = 'SELECT * FROM feedback '\
                          'WHERE email=%s AND ID=%s '\
                          'AND airline=%s AND flight_num=%s '\
                          'AND dept_date_time=%s '

add_feedback_query = 'INSERT INTO feedback '\
                             'VALUES (%s, %s, %s, %s, %s, %s)'
```

**Track Spending:** Default shows 1 year back, but could be queried per month separately in the last year. Then have a query to show the flights of what the user has chosen.

```python
get_amount_spent = 'SELECT SUM(sold_price) ' \
                           'FROM purchased NATURAL JOIN ticket_flight NATURAL JOIN origin_destination_name ' \
                           'WHERE email=%s AND MONTH(purchase_date_time)=%s AND YEAR(purchase_date_time)=%s '

query = 'SELECT * ' \
            'FROM purchased NATURAL JOIN ticket_flight NATURAL JOIN origin_destination_name ' \
            'WHERE email=%s AND DATE(purchase_date_time)>DATE(%s) '

query = 'SELECT SUM(sold_price) ' \
            'FROM purchased NATURAL JOIN ticket_flight NATURAL JOIN origin_destination_name ' \
            'WHERE email=%s'
```

### Staff:

**View flights:** Defaults show next 30days, and the Staff can click a button to show all days. This query was achieved with `DATETIME.NOW()`. The customers of a specific flight can be viewed by clicking on a button, which uses a `{{flight_counter}}` within jinja to fetch the correct flight in the `flight_data` session.

```sql
# default 30 days
SELECT ID, airline_name, flight_num, dept_date_time, status, \
origin_airport, origin_city, origin_country, destination_airport, \
destination_city, destination_country \
FROM origin_destination_name \
WHERE airline_name=%s and dept_date_time <= DATE_ADD(NOW(), INTERVAL 30 DAY) \
AND dept_date_time >= NOW()

# all flights
SELECT ID, airline_name, flight_num, dept_date_time, status, \
origin_airport, origin_city, origin_country, destination_airport, \
destination_city, destination_country FROM origin_destination_name \
WHERE airline_name=%s
```

**Create new flights:** Implemented as a button and form that redirects the Staff to create a new flight, flights are simply stored into the `flights` relation.

```python
INSERT INTO flight '\
'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
    cursor = conn.cursor()
    cursor.execute(insert_flight, (ID, airline_name, flight_num, \
dept_date_time_str, origin_code, destination_code, \
arr_date_time_str, base_price, status, "0"))
```

**Change flight status:** Viewed based on the `{{flight_counter}}` in the table, similar to how customers are viewed. Flight status are modified in a new page. SQL query updates the table.

```python
status_query = 'UPDATE flight '\
'SET status = %s '\
'WHERE ID=%s AND name=%s AND flight_num=%s AND dept_date_time=%s '
  cursor = conn.cursor()
  cursor.execute(status_query, (new_status, flight_to_modify['ID'], \
employee_airline, flight_to_modify['flight_num'], flight_to_modify['dept_date_time']))
```

**Add airplane into system:** SQL query updates the table after fetching from the form. It specifically only adds the `employee_airline` flight.

```python
add_airplane_query = 'INSERT INTO airplane '\
                       'VALUES (%s, %s, %s, %s, %s)'
    cursor.execute(add_airplane_query, \
(ID, employee_airline, num_seats, manufacturer, age))
    conn.commit()
```

**Add new airport:** SQL query updates the table after fetching from the form. It specifically only adds the `employee_airline` flight.

```python
insert_query = 'INSERT INTO airport VALUES (%s, %s, %s, %s, %s)'
    cursor.execute(insert_query, (code, name, city, country, flight_type))
    conn.commit()
```

**View Flight ratings:** Similar implementation to Change Flight status. SQL query updates the table.

```python
SELECT * from feedback WHERE airline = %s and ID = %s'
cursor.execute(query, (employee_airline, ID))
```

**View frequent customers:** Retrieves frequent customers in the following SQL query, and also returns top customer

```sql
SELECT name, total_purchases '\
'FROM last_year_customer_purchases '\
'WHERE airline=%s '\
'AND total_purchases=(SELECT MAX(total_purchases) '\
'FROM last_year_customer_purchases '\
'WHERE airline=%s) '
```

**View reports:** Queries under viewing earned revenue. Shows tickets sold based on range of dates in a month-wise table. Iterated over each month in a loop.

```python
get_months_total_tickets = 'SELECT airline, COUNT(*) AS total_tickets ' \
                           'FROM ticket_flight NATURAL JOIN purchased ' \
                           'WHERE airline=%s AND MONTH(purchase_date_time)=%s AND YEAR(purchase_date_time)=%s '\
                           'GROUP BY airline'
```

**View Earned revenue:** Retrieves all earned revenues and sums them up based on whether the user wants to see month or year and class.

```python
last_month_query = 'SELECT SUM(sold_price) FROM purchased NATURAL JOIN ticket_flight '\
                       'WHERE airline=%s AND MONTH(purchase_date_time)=MONTH(%s) '\
                       'AND YEAR(purchase_date_time)=YEAR(%s)'

last_year_query = 'SELECT SUM(sold_price) FROM purchased NATURAL JOIN ticket_flight '\
                      'WHERE airline=%s AND YEAR(purchase_date_time)=YEAR(%s)'

first_class = 'SELECT SUM(sold_price) FROM purchased NATURAL JOIN ticket_flight, ticket '\
                  'WHERE ticket.ID=ticket_ID AND airline=%s AND travel_class=%s'

business_class = 'SELECT SUM(sold_price) FROM purchased NATURAL JOIN ticket_flight, ticket '\
                     'WHERE ticket.ID=ticket_ID AND airline=%s AND travel_class=%s'

economy_class = 'SELECT SUM(sold_price) FROM purchased NATURAL JOIN ticket_flight, ticket '\
                     'WHERE ticket.ID=ticket_ID AND airline=%s AND travel_class=%s'
```

**View Top Destination:** First get destination with max tickets sold, then exclude max to get second most sold, and then exclude them both to get the third most sold. And this is repeated for years as well. Created a view `destination_reservations_3_months, destination_reservations_last_year` 

```python
top_dest_query = 'SELECT destination_city '\
                        'FROM destination_reservations_3_months '\
                        'WHERE airline_name=%s '\
                        'AND total_tickets=(SELECT MAX(total_tickets)' \
                                           'FROM destination_reservations_3_months '\
                                           'WHERE airline_name=%s) '

# 3 months
top_dest_query = 'SELECT destination_city '\
                         'FROM destination_reservations_3_months '\
                         'WHERE airline_name=%s '\
                         'AND destination_city<>%s '\
                         'AND total_tickets=(SELECT MAX(total_tickets) ' \
                                            'FROM destination_reservations_3_months '\
                                            'WHERE airline_name=%s '\
                                            'AND destination_city<>%s)'

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
```
