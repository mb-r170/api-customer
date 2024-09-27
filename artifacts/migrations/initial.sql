CREATE TABLE customers (
    id_customer SERIAL PRIMARY KEY,
    id_type INTEGER NOT NULL,
	customer_name  VARCHAR(500) NOT NULL,
    id_occupation INTEGER NOT NULL,
    change_counter INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE customer_types (
    id_type SERIAL PRIMARY KEY,
    type_name VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE occupations (
    id_occupation SERIAL PRIMARY KEY,
    occupation_name VARCHAR(100) UNIQUE NOT NULL
);

ALTER TABLE customers
ADD CONSTRAINT fk_customers_types
FOREIGN KEY (id_type) REFERENCES customer_types(id_type);

ALTER TABLE customers
ADD CONSTRAINT fk_customers_occupations
FOREIGN KEY (id_occupation) REFERENCES occupations(id_occupation);


CREATE TABLE external_interactions (
    id_interaction SERIAL PRIMARY KEY,
    timestamp TIMESTAMP,
    id_interaction_channel INTEGER NOT NULL,
    id_customer INTEGER NOT NULL,
    change_counter INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE interaction_channels (
    id_interaction_channel SERIAL PRIMARY KEY,
    channel_name VARCHAR(50) UNIQUE NOT NULL
);

ALTER TABLE external_interactions
ADD CONSTRAINT fk_external_interactions_channels
FOREIGN KEY (id_interaction_channel) REFERENCES interaction_channels(id_interaction_channel);
ALTER TABLE external_interactions
ADD CONSTRAINT fk_customers
FOREIGN KEY (id_customer) REFERENCES customers(id_customer);

CREATE TABLE products_of_discussion (
    id_product SERIAL PRIMARY KEY,
    month_year TIMESTAMP,
    product_name VARCHAR(100) UNIQUE NOT NULL,
    change_counter INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE users (
    id_user SERIAL PRIMARY KEY,
    username VARCHAR(120) UNIQUE NOT NULL,
    password_hash CHAR(162) NOT NULL,
    permissions JSONB DEFAULT '{}',
    change_counter INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


--crete function for change counter
CREATE OR REPLACE FUNCTION update_change_counter()
RETURNS TRIGGER AS $$
BEGIN
    NEW.change_counter := OLD.change_counter + 1;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

--add triggers
CREATE TRIGGER update_customer_change_counter
BEFORE UPDATE ON customers
FOR EACH ROW
EXECUTE PROCEDURE update_change_counter();

CREATE TRIGGER update_external_interactions_change_counter
BEFORE UPDATE ON external_interactions
FOR EACH ROW
EXECUTE PROCEDURE update_change_counter();

CREATE TRIGGER update_products_of_discussion_change_counter
BEFORE UPDATE ON products_of_discussion
FOR EACH ROW
EXECUTE PROCEDURE update_change_counter();








---views

CREATE VIEW view_customers AS
SELECT c.id_customer,o.occupation_name,c.customer_name,t.type_name,c.created_at,c.updated_at FROM public.customers c
JOIN customer_types t ON c.id_type=t.id_type
JOIN occupations o ON c.id_occupation=o.id_occupation
ORDER BY id_customer;

CREATE VIEW view_interactions AS
SELECT id_customer, jsonb_object_agg(channel_name, channel_count) AS channel_counts
FROM (SELECT c.id_customer, ic.channel_name, COUNT(c.id_interaction_channel) AS channel_count
    FROM external_interactions c
    JOIN interaction_channels ic
    ON c.id_interaction_channel = ic.id_interaction_channel
    GROUP BY c.id_customer, ic.channel_name
) subquery GROUP BY id_customer ORDER BY id_customer;

--demo data
INSERT INTO customer_types (type_name) VALUES
  ('Red'),
  ('Orange'),
  ('Blue');

INSERT INTO occupations (occupation_name) VALUES
  ('Jedi'),
  ('Batman'),
  ('Santa Claus'),
  ('Doctor'),
  ('Plummer');

INSERT INTO interaction_channels (channel_name) VALUES
  ('Email'),
  ('Call'),
  ('Bird');
  
INSERT INTO customers (id_type, id_occupation, customer_name) VALUES
  (1, 1, 'Fluke Starbucker'),
  (2, 2, 'Bruise Dwayne'),
  (3, 3, 'Kris Kringle'),
  (1, 4, 'Who'),
  (2, 5, 'Christopher');

INSERT INTO external_interactions (timestamp, id_interaction_channel, id_customer) VALUES
('04/10/2019 09:00', 1, 5),
('11/02/2020 16:10', 2, 3),
('05/03/2020 11:23', 3, 2),
('06/03/2020 11:23', 3, 2),
('07/03/2020 11:23', 2, 2),
('04/06/2021 13:01', 1, 4);

INSERT INTO products_of_discussion (month_year, product_name) VALUES
  (NOW(), 'Sand'),
  (NOW(), 'Orange');


INSERT INTO users (username,password_hash,permissions) VALUES
  ('admin', 'scrypt:32768:8:1$onTntjZ4HG97J8xR$4a5c16c50fd2836c809ddd5d94a4b221a1964340e3d4446167f45708494439cb66f70971245cc76a0dcaba2b0a91eeb2fdcf3d16bb9b9478d63f4a4562111b87', '{"read_all": "X", "write_all": "X", "admin": "X"}'),
  ('power', 'scrypt:32768:8:1$dXVu1FQhKHIeaS7h$a5edf146a338d12453c1521a15a0af0da646431f15a6b859b52ff8feef3ac3f6981cfecbebcb5dee521afa9631a7d1247a551d93659a02e3d04057176837faab', '{"read_all": "X", "create_customers": "RW"}'),
  ('user', 'scrypt:32768:8:1$6l6CWABvKf3gEWEU$0bd1e670acf1abeafa2b7ec9986863cd0b04347ac083016223b658665da16101275c46ef7d867b1a3e53d38a7aee8aa340990dc0392b8e0ad370728eee7a97ea', '{"get_customers": "R", "get_interactions": "R"}');
  
  