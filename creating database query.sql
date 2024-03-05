Use Bank_Managment_System;
go

create table Customer(user_id int identity primary key, password varchar(20) not null, user_first_name varchar(20), 
user_last_name varchar(20) not null, user_email varchar(100) unique, user_number int, user_dob varchar(20), user_age int, credit_score int) 

INSERT INTO Customer (password, user_first_name, user_last_name, user_email, user_number, user_dob, user_age, credit_score)
VALUES 
('pass1234', 'John', 'Doe', 'john.doe@email.com', 1234567890, '1990-01-01', 30, 700),
('pass2345', 'Jane', 'Smith', 'jane.smith@email.com', 1345678901, '1985-02-02', 35, 750),
('pass3456', 'Jim', 'Brown', 'jim.brown@email.com', 1456789012, '1992-03-03', 28, 680),
('pass4567', 'Jill', 'Davis', 'jill.davis@email.com', 1567890123, '1988-04-04', 32, 710),
('pass5678', 'Jake', 'Wilson', 'jake.wilson@email.com', 1678901234, '1975-05-05', 45, 730),
('pass6789', 'Jessica', 'Garcia', 'jessica.garcia@email.com', 1789012345, '1980-06-06', 40, 720),
('pass7890', 'Jordan', 'Martinez', 'jordan.martinez@email.com', 1890123456, '1993-07-07', 27, 695),
('pass8901', 'Julie', 'Rodriguez', 'julie.rodriguez@email.com', 1901234567, '1995-08-08', 25, 705),
('pass9012', 'Jeremy', 'Hernandez', 'jeremy.hernandez@email.com', 1012345678, '1982-09-09', 38, 715),
('pass0123', 'Jasmine', 'Moore', 'jasmine.moore@email.com', 1234567890, '1986-10-10', 36, 740);

INSERT INTO Customer (password, user_first_name, user_last_name, user_email, user_number, user_dob, user_age, credit_score)
VALUES 
('a', 'John', 'Doe', 'a', 1234567890, '1990-01-01', 30, 700)

CREATE TABLE Employee(
    employee_id INT IDENTITY(1,1) PRIMARY KEY,
    employee_first_name VARCHAR(20),
    employee_last_name VARCHAR(20) NOT NULL,
    employee_email VARCHAR(100) UNIQUE,
    employee_number INT,
    employee_dob VARCHAR(20),
	department_id VARCHAR(20),
    employee_age INT
)



INSERT INTO Employee (employee_first_name, employee_last_name, employee_email, employee_number, employee_dob, department_id, employee_age)
VALUES 
('Alice', 'Johnson', 'alice.johnson@email.com', 123456789, '1990-01-01', 'A', 30),
('Bob', 'Anderson', 'bob.anderson@email.com', 234567890, '1985-02-02', 'IM', 35),
('Catherine', 'Clark', 'catherine.clark@email.com', 345678901, '1992-03-03', 'CS', 28),
('David', 'White', 'david.white@email.com', 456789012, '1975-05-05', 'HR', 45),
('Ella', 'Gonzalez', 'ella.gonzalez@email.com', 567890123, '1980-06-06', 'A', 40),
('Frank', 'Taylor', 'frank.taylor@email.com', 678901234, '1993-07-07', 'IM', 27),
('Grace', 'Smith', 'grace.smith@email.com', 789012345, '1995-08-08', 'CS', 25),
('Henry', 'Brown', 'henry.brown@email.com', 890123456, '1982-09-09', 'HR', 38),
('Isabella', 'Martinez', 'isabella.martinez@email.com', 901234567, '1986-10-10', 'A', 36),
('Jacob', 'Williams', 'jacob.williams@email.com', 123456780, '1978-11-11', 'IM', 44);

Create table department(department_id varchar(4) PRIMARY KEY, department_name VARCHAR(50) NOT NULL)

INSERT INTO department (department_id, department_name)
VALUES 
('A', 'Accounts'),
('IM', 'Investment_Management'),
('CS', 'Customer_Services'),
('HR', 'Human_Resources');

CREATE TABLE admin (
    admin_id INT IDENTITY(1,1) PRIMARY KEY,
    employee_id INT,
    department_id varchar(4),
    employee_email VARCHAR(100) UNIQUE,
    employee_password VARCHAR(20) NOT NULL
);

INSERT INTO admin (employee_id, department_id, employee_email, employee_password)
VALUES
    ((SELECT employee_id FROM Employee WHERE employee_first_name = 'Henry' AND employee_last_name = 'Brown'), 
    (SELECT department_id FROM department WHERE department_name = 'Human_Resources'),
    'henry.brown@email.com', 'admin_password'),
    
    ((SELECT employee_id FROM Employee WHERE employee_first_name = 'David' AND employee_last_name = 'White'), 
    (SELECT department_id FROM department WHERE department_name = 'Human_Resources'),
    'david.white@email.com', 'admin_password');

CREATE TABLE customer_review (
    review_id INT IDENTITY(1,1) PRIMARY KEY,
    user_id INT,
    credit_score INT,
    customer_review NVARCHAR(MAX)
);



INSERT INTO customer_review (user_id, credit_score, customer_review)
VALUES
    ((SELECT user_id FROM Customer WHERE user_first_name = 'Jordan' AND user_last_name = 'Martinez'), 695, 'The bank''s services are excellent, and I''m satisfied with my experience.'),
    ((SELECT user_id FROM Customer WHERE user_first_name = 'Julie' AND user_last_name = 'Rodriguez'), 705, 'The bank provides great financial solutions, and their customer support is top-notch.'),
    ((SELECT user_id FROM Customer WHERE user_first_name = 'Jeremy' AND user_last_name = 'Hernandez'), 715, 'I''ve had a long-standing relationship with this bank, and they''ve always been reliable and trustworthy.');

create table investment_manager(
	investment_manager_id INT IDENTITY(1,1) PRIMARY KEY, 
	employee_id INT, 
	employee_email VARCHAR(100) UNIQUE,
	employee_password VARCHAR(20) NOT NULL
)


INSERT INTO investment_manager (employee_id, employee_email, employee_password)
SELECT employee_id, employee_email, 'password'
FROM Employee
WHERE department_id = 'IM';

create table accountant(
	accountant INT IDENTITY(1,1) PRIMARY KEY, 
	employee_id INT, 
	employee_email VARCHAR(100) UNIQUE,
	employee_password VARCHAR(20) NOT NULL
)



INSERT INTO accountant (employee_id, employee_email, employee_password)
SELECT employee_id, employee_email, 'password'
FROM Employee
WHERE department_id = 'A';

create table customer_service_representative(
	customer_service_representative INT IDENTITY(1,1) PRIMARY KEY,
	employee_id INT, 
	employee_email VARCHAR(100) UNIQUE,
	employee_password VARCHAR(20) NOT NULL
)



INSERT INTO customer_service_representative (employee_id, employee_email, employee_password)
SELECT employee_id, employee_email, 'password'
FROM Employee
WHERE department_id = 'CS';

CREATE TABLE account(
    account_no VARCHAR(15) UNIQUE,
    user_id INT,
    account_age INT,
    credit_score INT,
    account_balance INT,
    saving_account_check BIT DEFAULT 0, 
    saving_account_id VARCHAR(15),
    saving_account_balance INT
);

INSERT INTO account (account_no, user_id, account_age, account_balance, saving_account_check, saving_account_id, saving_account_balance, credit_score)
SELECT 'ACC10001', user_id, 5, 10000, 1, 'SAV10001', 5000, credit_score FROM Customer WHERE user_first_name = 'John' AND user_last_name = 'Doe' UNION
SELECT 'ACC10002', user_id, 8, 15000, 0, NULL, NULL, credit_score FROM Customer WHERE user_first_name = 'Jane' AND user_last_name = 'Smith' UNION
SELECT 'ACC10003', user_id, 3, 8000, 1, 'SAV10002', 3000, credit_score FROM Customer WHERE user_first_name = 'Jim' AND user_last_name = 'Brown' UNION
SELECT 'ACC10004', user_id, 6, 12000, 0, NULL, NULL, credit_score FROM Customer WHERE user_first_name = 'Jill' AND user_last_name = 'Davis' UNION
SELECT 'ACC10005', user_id, 10, 20000, 1, 'SAV10003', 10000, credit_score FROM Customer WHERE user_first_name = 'Jake' AND user_last_name = 'Wilson' UNION
SELECT 'ACC10006', user_id, 7, 14000, 1, 'SAV10004', 7000, credit_score FROM Customer WHERE user_first_name = 'Jessica' AND user_last_name = 'Garcia' UNION
SELECT 'ACC10007', user_id, 4, 9000, 0, NULL, NULL, credit_score FROM Customer WHERE user_first_name = 'Jordan' AND user_last_name = 'Martinez' UNION
SELECT 'ACC10008', user_id, 2, 7000, 1, 'SAV10005', 3500, credit_score FROM Customer WHERE user_first_name = 'Julie' AND user_last_name = 'Rodriguez' UNION
SELECT 'ACC10009', user_id, 9, 18000, 0, NULL, NULL, credit_score FROM Customer WHERE user_first_name = 'Jeremy' AND user_last_name = 'Hernandez' UNION
SELECT 'ACC10010', user_id, 11, 22000, 1, 'SAV10006', 11000, credit_score FROM Customer WHERE user_first_name = 'Jasmine' AND user_last_name = 'Moore';

CREATE TABLE Loan(
    Loan_ID INT,
    User_ID INT,
    Loan_Status VARCHAR(255),
    Interest_Rate DECIMAL(10, 2),
    Loan_Type TEXT,
    Amount_Loaned DECIMAL(10, 2),
    Estimated_Payback_Plan VARCHAR(255),
    Loan_number int)

INSERT INTO Loan (Loan_ID, User_ID, Loan_Status, Interest_Rate, Loan_Type, Amount_Loaned, Estimated_Payback_Plan, Loan_number) 
VALUES 
(1, 1, 'late', 5.5, 'Mortgage', 250000, '2028-12-31', 1),
(2, 2, 'paid', 4.2, 'Student Loan', 30000, '2023-06-15', 1),
(3, 3, 'due', 6.0, 'Home Equity Loan', 50000, '2025-11-20', 1),
(4, 4, 'late', 3.8, 'Car Loan', 15000, '2024-07-10', 1),
(5, 5, 'paid', 5.2, 'Personal Loan', 10000, '2022-09-30', 1),
(6, 6, 'due', 4.6, 'Mortgage', 200000, '2027-05-25', 1),
(7, 7, 'late', 7.0, 'Business Loan', 75000, '2026-08-14', 1),
(8, 1, 'paid', 4.5, 'Debt Consolidation', 35000, '2023-03-21', 2),
(9, 8, 'due', 3.9, 'Student Loan', 40000, '2025-12-15', 1),
(10, 9, 'late', 6.5, 'Home Equity Loan', 60000, '2027-07-19', 1),
(11, 10, 'paid', 4.0, 'Car Loan', 12000, '2024-02-28', 1),
(12, 2, 'due', 5.8, 'Personal Loan', 9000, '2026-04-22', 2),
(13, 3, 'late', 6.3, 'Mortgage', 180000, '2028-10-30', 2),
(14, 4, 'paid', 4.1, 'Business Loan', 30000, '2023-01-10', 2),
(15, 5, 'due', 5.4, 'Debt Consolidation', 20000, '2025-09-05', 2);

CREATE TABLE interest_type(
    saving_account_id VARCHAR(15) PRIMARY KEY,  
    saving_account_balance INT,
    interest_type VARCHAR(50) CHECK (interest_type IN ('Simple Interest', 'Compound Interest')),  
    interest_rate DECIMAL(10,2),
    payout_duration VARCHAR(10) CHECK (payout_duration IN ('Yearly', 'Monthly', 'Quarterly')),  
    saving_account_period INT
);

INSERT INTO interest_type (saving_account_id, saving_account_balance, interest_type, interest_rate, payout_duration, saving_account_period)
VALUES 
('SAV10001', 5000, 'Simple Interest', 2.50, 'Yearly', 5),
('SAV10002', 3000, 'Compound Interest', 3.00, 'Quarterly', 10),
('SAV10003', 10000, 'Simple Interest', 2.75, 'Monthly', 3),
('SAV10004', 7000, 'Compound Interest', 3.50, 'Yearly', 8),
('SAV10005', 3500, 'Simple Interest', 2.25, 'Quarterly', 4),
('SAV10006', 11000, 'Compound Interest', 3.25, 'Monthly', 6);

/* sorry did not populate this didnt understand how to total everything*/
CREATE TABLE Accounts_Balance_Sheet(
    Total_Savings_Account DECIMAL(10, 2),
    Investor_Funding DECIMAL(10, 2),
    Monthly_Costs DECIMAL(10, 2),
    Total_Amount_Loaned DECIMAL(10, 2),
    Profit_Loss_Total DECIMAL(10, 2)
)

CREATE TABLE loan_approval (
    request_id INT ,
    user_id INT,
    amount INT,
    loan_type VARCHAR(100)
)





--ALTER TABLE loan_approval
--ALTER COLUMN request_id INT;



/*all the display of the tables*/
SELECT * FROM Customer;
SELECT * FROM loan_approval;
SELECT * FROM Employee;
SELECT * FROM department;
SELECT * FROM customer_review;
SELECT * FROM admin;
SELECT * FROM investment_manager;
SELECT * FROM accountant;
SELECT * FROM customer_service_representative;
SELECT * FROM account;
SELECT * FROM Loan;
SELECT * FROM interest_type;