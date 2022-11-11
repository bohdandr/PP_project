CREATE TABLE user (
    id INT AUTO_INCREMENT NOT NULL PRIMARY KEY,
    username VARCHAR(32),
    firstName VARCHAR(32),
    lastName VARCHAR(32),
    email VARCHAR(64),
    password VARCHAR(128),
    phone VARCHAR(32),
    birthDate DATE,
    wallet FLOAT,
    userStatus ENUM('0', '1')
);

CREATE TABLE transaction (
    id INT AUTO_INCREMENT NOT NULL PRIMARY KEY,
    sentByUser INT,
    sentToUser INT,
    value FLOAT,
    datePerformed DATETIME,
    FOREIGN KEY(sentByUser) REFERENCES user(id),
    FOREIGN KEY(sentToUser) REFERENCES user(id)
);

-- mysql -u root -p ap
-- source F:/bohdan/3_sem/PP_project/lab6/create_tables.sql

