CREATE TABLE airport(
    code varchar(5),
    name varchar(30),
    city varchar(20),
    country varchar(20),
    type varchar(25),
    PRIMARY KEY (code)
);

CREATE TABLE airline(
    name varchar(25),
    PRIMARY KEY (name)
);

CREATE TABLE airplane(
    ID varchar(10),
    name varchar(25),
    num_seats int,
    manufacturer varchar(25),
    age int,
    PRIMARY KEY (ID, name),
    FOREIGN KEY (name) REFERENCES airline(name)
);

CREATE TABLE works_for(
    username varchar(25),
    name varchar(25),
    PRIMARY KEY (username, name),
    FOREIGN KEY (name) REFERENCES airline(name)
);

CREATE TABLE airline_staff(
    username varchar(25),
    password varchar(400) NOT NULL,
    first_name varchar(15),
    last_name varchar(25),
    date_of_birth date,
    PRIMARY KEY (username),
    FOREIGN KEY (username) REFERENCES works_for(username)
);

CREATE TABLE staff_phone(
    username varchar(25),
    phone_number varchar(15),
    PRIMARY KEY (username, phone_number),
    FOREIGN KEY (username) REFERENCES airline_staff(username)
);


CREATE TABLE flight(
    ID varchar(10),
    name varchar(25),
    flight_num varchar(5),
    dept_date_time datetime,
    origin_code varchar(5),
    destination_code varchar(5),
    arr_date_time datetime,
    base_price numeric(7,2),
    status varchar(8) CHECK (status = 'DELAYED' OR status='ON-TIME' OR status='CANCELED'),
    seats_booked int DEFAULT 0,
    PRIMARY KEY (name, flight_num, ID, dept_date_time),
    FOREIGN KEY (ID, name) REFERENCES airplane(ID, name),
    FOREIGN KEY (origin_code) REFERENCES airport(code),
    FOREIGN KEY (destination_code) REFERENCES airport(code)
);

CREATE TABLE ticket(
    ID varchar(10),
    travel_class varchar(20) CHECK (travel_class='BUSINESS CLASS' OR travel_class='FIRST CLASS' OR travel_class='ECONOMY CLASS'),
    PRIMARY KEY (ID)
);

CREATE TABLE customer(
    email varchar(30),
    name varchar(40),
    password varchar(400) NOT NULL,
    building_num int,
    street varchar(25),
    city varchar(20),
    state varchar(20),
    phone_number varchar(15),
    passport_number varchar(20),
    passport_expiration date,
    passport_country varchar(20),
    date_of_birth date,
    PRIMARY KEY (email)
);

CREATE TABLE feedback(
    email varchar(30),
    ID varchar(5),
    airline varchar(25),
    flight_num varchar(5),
    dept_date_time datetime,
    comment varchar(400),
    PRIMARY KEY (email, ID, airline, flight_num, dept_date_time),
    FOREIGN KEY (email) REFERENCES customer(email),
    FOREIGN KEY (ID, airline, flight_num, dept_date_time) REFERENCES flight(ID, name, flight_num, dept_date_time)
);

CREATE TABLE purchased(
    ticket_ID varchar(10),
    email varchar(30),
    purchase_date_time datetime,
    sold_price numeric(7,2),
    card_type varchar(20),
    card_number varchar(16),
    name_on_card varchar(40),
    card_expiration date,
    PRIMARY KEY (ticket_ID, email),
    FOREIGN KEY (ticket_ID) REFERENCES ticket(ID),
    FOREIGN KEY (email) REFERENCES customer(email)
);

CREATE TABLE ticket_flight(
    ticket_ID varchar(10),
    airplane_ID varchar(10),
    airline varchar(25),
    flight_num varchar(5),
    dept_date_time datetime,
    PRIMARY KEY (ticket_ID, airplane_ID, airline, flight_num, dept_date_time),
    FOREIGN KEY (ticket_ID) REFERENCES ticket(ID),
    FOREIGN KEY (airplane_ID, airline, flight_num, dept_date_time) REFERENCES flight(ID, name, flight_num, dept_date_time)
);

CREATE VIEW origin_destination_name AS
SELECT flight.ID, flight.name AS airline_name, flight.flight_num, flight.dept_date_time, origin_code,
destination_code, arr_date_time, base_price, status, O.name AS origin_airport, O.city AS origin_city,
O.country AS origin_country, O.type as origin_airport_type, D.name AS destination_airport,
D.city AS destination_city, D.country AS destination_country, D.type as destination_airport_type FROM flight,
airport as O, airport as D
WHERE flight.origin_code=O.code
AND flight.destination_code=D.code;