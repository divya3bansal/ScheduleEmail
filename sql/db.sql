CREATE DATABASE FlaskPythonApp;

USE FlaskPythonApp;

CREATE TABLE `FlaskPythonApp`.`tbl_email` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `event_id` INT NOT NULL,
  `email_subject` VARCHAR(255) NOT NULL,
  `email_content` VARCHAR(1024) NOT NULL,
  `timestamp` TIMESTAMP NOT NULL,
  PRIMARY KEY (`id`));

CREATE TABLE `FlaskPythonApp`.`tbl_user` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `event_id` INT NOT NULL,
  `user_name` VARCHAR(45) NOT NULL,
  `user_emailid` VARCHAR(255) NOT NULL,
  PRIMARY KEY (`id`));

DELIMITER $$
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_saveEmail`(
    IN p_eventid INT,
    IN p_subject VARCHAR(255),
    IN p_content VARCHAR(1024),
    IN p_timestamp TIMESTAMP
)
BEGIN
        insert into tbl_email
        (
	    event_id,
            email_subject,
            email_content,
            timestamp
        )
        values
        (
	    p_eventid,
            p_subject,
            p_content,
            p_timestamp
        );
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_saveUser`(
    IN p_eventid INT,
    IN p_username VARCHAR(45),
    IN p_emailid VARCHAR(255)
)
BEGIN
        insert into tbl_user
        (
            event_id,
            user_name,
            user_emailid
        )
        values
        (
            p_eventid,
            p_username,
            p_emailid
        );
END$$
DELIMITER ;

