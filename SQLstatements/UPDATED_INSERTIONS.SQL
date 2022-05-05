INSERT INTO airline VALUES ('China Eastern');
INSERT INTO airline VALUES ('EL AL');
INSERT INTO airline VALUES ('Lufthansa');
INSERT INTO airline VALUES ('Delta');

INSERT INTO airport VALUES ('12346', 'EWR', 'Newark', 'USA', 'DOMESTIC & INTERNATIONAL');
INSERT INTO airport VALUES ('12345', 'JFK', 'New York City', 'USA', 'DOMESTIC & INTERNATIONAL');
INSERT INTO airport VALUES ('54321', 'PVG', 'Shanghai', 'China', 'DOMESTIC & INTERNATIONAL');
INSERT INTO airport VALUES ('11333', 'Ben-Gurion', 'Tel-Aviv', 'Israel', 'DOMESTIC & INTERNATIONAL');
INSERT INTO airport VALUES ('01926', 'BER', 'Berlin', 'Germany', 'DOMESTIC & INTERNATIONAL');

INSERT INTO customer VALUES ('kingston@gmail.com', 'Kingston Yip', 'yoyosup', 370, 'Jay Street',
	'Brooklyn', 'NY', '4193331111', '1234567', '2027-11-11', 'China', '2000-12-10');
INSERT INTO customer VALUES ('daniel@gmail.com', 'Daniel Longman', 'makore1', 476, 'Washington Avenue',
	'Brooklyn', 'NY', '8015552222', '9876543', '2027-12-11', 'Germany', '1989-11-01');


INSERT INTO airplane VALUES ('MU2493', 'China Eastern', 333, 'Boeing', 5);
INSERT INTO airplane VALUES ('MU2443', 'China Eastern', 333, 'Boeing', 4);
INSERT INTO airplane VALUES ('LY7', 'EL AL', 345, 'Boeing', 3);
INSERT INTO airplane VALUES ('DLH1111', 'Lufthansa', 285, 'Boeing', 1);
INSERT INTO airplane VALUES ('DLH1113', 'Lufthansa', 285, 'Boeing', 3);
INSERT INTO airplane VALUES ('DL01234', 'Delta', 2, 'Boeing', 2);


INSERT INTO works_for VALUES ('suqiwu@aol.com', 'China Eastern');
INSERT INTO airline_staff VALUES ('suqiwu@aol.com', 'anchor55', 'Suqi', 'Wu', '1999-05-05');
INSERT INTO staff_phone VALUES ('suqiwu@aol.com', '9174531234');
INSERT INTO works_for VALUES ('mzechar1@walla.co.il', 'EL AL');
INSERT INTO airline_staff VALUES ('mzechar1@walla.co.il', 'iloveny', 'Matan', 'Zecharia', '1993-08-05');
INSERT INTO staff_phone VALUES ('mzechar1@walla.co.il', '0508345370');
INSERT INTO works_for VALUES ('wamozart@lufthansa.de', 'Lufthansa');
INSERT INTO airline_staff VALUES ('wamozart@lufthansa.de', 'iloveberlin', 'Wolfgang', 'Mozart', '1985-06-13');
INSERT INTO staff_phone VALUES ('wamozart@lufthansa.de', '0176305304');

INSERT INTO flight VALUES ('MU2493', 'China Eastern', '123', '2022-08-01 11:11:00', '12345', '54321',
	'2022-08-02 11:20:00', 1000.00, 'DELAYED', 0);
INSERT INTO flight VALUES ('LY7', 'EL AL', '98', '2022-08-01 11:11:00', '12345', '11333',
	'2022-08-02 11:20:00', 1000.00, 'ON-TIME', 0);
INSERT INTO flight VALUES ('MU2443', 'China Eastern', '124', '2022-08-05 11:11:00', '54321', '12345',
	'2022-08-06 11:20:00', 1000.00, 'ON-TIME', 0);
INSERT INTO flight VALUES ('LY7', 'EL AL', '99', '2022-08-04 16:10:00', '11333', '12345',
	'2022-08-05 03:15:00', 950.00, 'ON-TIME', 0);
INSERT INTO flight VALUES ('DLH1113', 'Lufthansa', '23', '2022-08-10 16:55:00', '01926', '11333',
	'2022-08-10 23:35:00', 850.00, 'DELAYED', 0);
INSERT INTO flight VALUES ('DLH1111', 'Lufthansa', '90', '2022-03-13 16:55:00', '12345', '01926',
	'2022-03-14 03:50:00', 800.00, 'CANCELED', 0);
INSERT INTO flight VALUES ('UA01234', 'Delta', '10', '2022-04-28 08:00:00', '12346', '12345', 
	'2022-04-08 09:00:00', 250.00, 'ON-TIME', 0);


INSERT INTO ticket VALUES ('HNR101', 'BUSINESS CLASS');
INSERT INTO ticket_flight VALUES ('HNR101', 'MU2493', 'China Eastern', '123', '2022-08-01 11:11:00');
INSERT INTO purchased VALUES ('HNR101', 'kingston@gmail.com', '2022-03-03 10:26:33', 1000.00,
	'VISA', '0902348512349876','Kingston Yip', '2024-07-07');
UPDATE flight SET seats_booked = seats_booked+1
WHERE ID='MU2493' AND name='China Eastern' AND flight_num='123' AND dept_date_time='2022-08-01 11:11:00'

INSERT INTO ticket VALUES ('HNF333', 'ECONOMY CLASS');
INSERT INTO ticket_flight VALUES ('HNF333', 'LY7', 'EL AL', '99', '2022-08-04 16:10:00');
INSERT INTO purchased VALUES ('HNF333', 'daniel@gmail.com', '2022-03-11 15:25:33', 950.00,
	'VISA', '2901348612379875','Daniel Longman', '2024-08-09');

INSERT INTO ticket VALUES ('CDR345', 'FIRST CLASS');
INSERT INTO ticket_flight VALUES ('CDR345', 'DLH1111', 'Lufthansa', '90', '2022-03-13 16:55:00');
INSERT INTO purchased VALUES ('CDR345', 'catherine@yahoo.com', '2022-03-29 08:10:01', 850.00,
	'American Express', '4355777712370123','Catherine Smith', '2024-08-09');

INSERT INTO ticket VALUES ('CDS111', 'FIRST CLASS');
INSERT INTO ticket_flight VALUES ('CDS111', 'DLH1113', 'Lufthansa', '23', '2022-08-10 16:55:00');
INSERT INTO purchased VALUES ('CDS111', 'catherine@yahoo.com', '2022-03-26 08:10:01', 1030.00,
	'American Express', '4355777712370123','Catherine Smith', '2024-08-09');

INSERT INTO ticket VALUES ('WUE235', 'BUSINESS CLASS');
INSERT INTO ticket_flight VALUES ('WUE235', 'MU2443', 'China Eastern', '124', '2022-08-05 11:11:00');
INSERT INTO purchased VALUES ('WUE235', 'kingston@gmail.com', '2022-03-03 10:26:33', 1000.00,
	'VISA', '0902348512349876','Kingston Yip', '2024-07-07');
UPDATE flight SET seats_booked = seats_booked+1
WHERE ID='MU2443' AND name='China Eastern' AND flight_num='124' AND dept_date_time='2022-08-05 11:11:00'

INSERT INTO feedback VALUES ('catherine@yahoo.com', 'DLH1111', 'Lufthansa', '90', '2022-03-13 16:55:00','hello');