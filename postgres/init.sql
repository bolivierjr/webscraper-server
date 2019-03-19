DROP TABLE IF EXISTS parts_data;

CREATE TABLE parts_data (
 _id serial PRIMARY KEY,
 url_list_id INT NOT NULL,
 url VARCHAR(255) UNIQUE NOT NULL,
 part_num VARCHAR(255) NOT NULL,
 part_num_analyzed VARCHAR NOT NULL,
 details JSONB,
 specs JSONB,
 datasheet_url VARCHAR(255),
 issued_time TIMESTAMP NOT NULL,
 issued_to VARCHAR(100) NOT NULL,
 completed_time TIMESTAMP
);