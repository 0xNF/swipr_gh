BEGIN TRANSACTION;
DROP TABLE IF EXISTS `pics`;
CREATE TABLE IF NOT EXISTS `pics` (
	`path`	TEXT NOT NULL, -- relative path to file
	`label`	INTEGER NOT NULL DEFAULT -2, -- error code of the analysis. anything less than 1 is a failure or one sort or another
	`invalid`	INTEGER NOT NULL DEFAULT 0, -- whether the file was invalid
	`ages`	TEXT, -- a comma separated list of estimated ages of the people in the picture.
	`num_people`	INTEGER, -- number of faces detected in the picture
	`male_present`	INTEGER, -- whether any of the people present is male
	`baby_present`	INTEGER, -- whether a baby is present
	PRIMARY KEY(`path`)
);
COMMIT;
