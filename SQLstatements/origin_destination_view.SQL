CREATE VIEW origin_destination_name AS
SELECT flight.ID, flight.name AS airline_name, flight.flight_num, flight.dept_date_time, origin_code,
destination_code, arr_date_time, base_price, status, O.name AS origin_airport, O.city AS origin_city,
O.country AS origin_country, O.type as origin_airport_type, D.name AS destination_airport,
D.city AS destination_city, D.country AS destination_country, D.type as destination_airport_type,
seats_booked
FROM flight, airport as O, airport as D
WHERE flight.origin_code=O.code
AND flight.destination_code=D.code;

# Show total tickets for each destination in last 3 months as a VIEW:
CREATE VIEW destination_reservations_3_months AS
SELECT destination_city, airline_name, SUM(seats_booked) AS total_tickets
FROM origin_destination_name
WHERE dept_date_time>DATE_SUB(NOW(), INTERVAL 3 MONTH)
AND dept_date_time<=NOW()
GROUP BY destination_city, airline_name

# Show total tickets for each destination in last year as a VIEW:
CREATE VIEW destination_reservations_year AS
SELECT destination_city, airline_name, SUM(seats_booked) AS total_tickets
FROM origin_destination_name
WHERE YEAR(dept_date_time)=YEAR(DATE_SUB(NOW(), INTERVAL 1 YEAR))
AND dept_date_time<=NOW()
GROUP BY destination_city, airline_name

# Show total tickets for each destination as a VIEW:
CREATE VIEW destination_reservations_3_months AS
SELECT destination_city, SUM(seats_booked) AS total_tickets
FROM origin_destination_name 
HAVING dept_date_time>DATE_SUB(NOW(), INTERVAL 3 MONTH)
GROUP BY destination_city

# View to show most frequent customer in last calendar year:
CREATE VIEW last_year_customer_purchases AS
SELECT name, email, airline, COUNT(email) as total_purchases
FROM purchased NATURAL JOIN customer NATURAL JOIN ticket_flight
WHERE YEAR(dept_date_time)=YEAR(DATE_SUB(NOW(), INTERVAL 1 YEAR))
GROUP BY email, airline

# Search for flights based on all 4 parameters origin,destination,departue date, and return date:
SELECT *
FROM `origin_destination_name`
WHERE
    (origin_city IN
        (SELECT origin_city
         FROM origin_destination_name
         WHERE origin_city='New York City'
         OR origin_airport='JFK')
    AND DATE(dept_date_time)='2022-08-01'
    AND destination_city IN
        (SELECT destination_city
         FROM origin_destination_name
         WHERE destination_city='Shanghai'
         OR destination_airport='PVG'))
OR (origin_city IN
        (SELECT origin_city
         FROM origin_destination_name
         WHERE origin_city='Shanghai'
         OR origin_airport='PVG')
    AND DATE(dept_date_time)='2022-08-05'
    AND destination_city IN
        (SELECT destination_city
         FROM origin_destination_name
         WHERE destination_city='New York City'
         OR destination_airport='JFK'));