-- Step 1: Create the tables
CREATE TABLE customers (
    Customer_Id INT PRIMARY KEY,
    Occupation VARCHAR(255),
    Type VARCHAR(255)
);


CREATE TABLE interactions (
    date_start TIMESTAMP,
    event VARCHAR(255),
    customers INT
);

CREATE TABLE products (
    date VARCHAR(7),
    product VARCHAR(255)
);