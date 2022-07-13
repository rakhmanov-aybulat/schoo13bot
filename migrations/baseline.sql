BEGIN;

CREATE TABLE schema_change_log (
	id SERIAL NOT NULL PRIMARY KEY,
	major_release_number VARCHAR(2) NOT NULL,
	minor_release_number VARCHAR(2) NOT NULL,
	point_release_number VARCHAR(4) NOT NULL,
	script_name VARCHAR(50) NOT NULL,
	date_applied TIMESTAMP(0) WITH TIME ZONE NOT NULL
);

INSERT INTO schema_change_log
	(major_release_number
	,minor_release_number
	,point_release_number
	,script_name
	,date_applied)
VALUES
	('01'
	,'00'
	,'0000'
	,'baseline.sql'
	,CURRENT_TIMESTAMP(0));

CREATE TABLE event_schedule (
	event_id SERIAL NOT NULL PRIMARY KEY,
	event_name VARCHAR(255) NOT NULL,
	weekday INT NOT NULL,
	event_start TIME(0) NOT NULL,
	event_end TIME(0) NOT NULL
);

CREATE TABLE grades (
	grade VARCHAR(255) NOT NULL PRIMARY KEY,
	grade_number INT NOT NULL,
	grade_letter VARCHAR(1) NOT NULL
);

CREATE TABLE event_clarification (
	event_id INT NOT NULL,
	grade VARCHAR(255) REFERENCES grades(grade),
	event_clarification VARCHAR(255) NOT NULL
);

CREATE TABLE users (
	chat_id BIGINT NOT NULL PRIMARY KEY,
	first_name VARCHAR(255) NOT NULL,
	last_name VARCHAR(255),
	username VARCHAR(255),
	grade VARCHAR(255)
);

COMMIT;
