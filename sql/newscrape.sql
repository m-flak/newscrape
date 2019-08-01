/*** for mysql 8+ ***/
USE newscrape;

/* CREATE USER TABLES */
CREATE TABLE users (
  id INT UNSIGNED NOT NULL AUTO_INCREMENT,
  email VARCHAR(255) DEFAULT NULL,
  name VARCHAR(255) DEFAULT NULL,
  pass BLOB,
  admin TINYINT DEFAULT 0,
  api_key TEXT,
  key_expire DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY email (email),
  UNIQUE KEY name (name)
);

/* CREATE KEYWORDS TABLES */
CREATE TABLE keywords (
  id INT UNSIGNED NOT NULL AUTO_INCREMENT,
  user INT UNSIGNED NOT NULL,
  keyword VARCHAR(32) NOT NULL DEFAULT ' ',
  PRIMARY KEY (id),
  FOREIGN KEY (user)
  REFERENCES users (id)
  ON DELETE RESTRICT
  ON UPDATE CASCADE
);

/* CREATE PROCEDURES FOR USER TABLES */
DELIMITER //
/* Add a new user */
CREATE PROCEDURE add_new_user (IN uname TEXT, IN e_mail TEXT, IN pw TEXT)
BEGIN
  DECLARE hash VARCHAR(130);
  SET hash = (SELECT CAST(SHA2(pw, 512) AS CHAR));

  INSERT INTO users (email,name,pass) VALUES(e_mail, uname, AES_ENCRYPT(pw, hash));
END;//
/* Verify User name & password combo
 * * returns the email & name combo if password correct
 * * * otherwise, NULL
 */
CREATE PROCEDURE verify_user_password(IN uname TEXT, IN pw TEXT)
BEGIN
  DECLARE hash VARCHAR(130);
  DECLARE the_blob BLOB;
  DECLARE dec_pass TEXT;

  SELECT pass FROM users AS u WHERE u.name = uname INTO the_blob;
  SET hash = (SELECT CAST(SHA2(pw, 512) AS CHAR));
  SET dec_pass = (SELECT AES_DECRYPT(the_blob, hash));

  IF (dec_pass = pw) THEN
    SELECT email,name FROM users AS u WHERE u.name = uname;
  ELSE
    SELECT NULL;
  END IF;
END;//
/* Update a user's password */
CREATE PROCEDURE update_user_password(IN uname TEXT, IN pw TEXT)
BEGIN
  DECLARE hash VARCHAR(130);
  SET hash = (SELECT CAST(SHA2(pw, 512) AS CHAR));

  UPDATE users SET pass = AES_ENCRYPT(pw, hash) WHERE name = uname;
END;//
DELIMITER ;
