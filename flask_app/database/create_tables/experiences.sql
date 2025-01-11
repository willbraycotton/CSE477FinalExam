CREATE TABLE IF NOT EXISTS `experiences` (
`experience_id`      int(11)       NOT NULL AUTO_INCREMENT	COMMENT 'The primary key, and unique identifier for each experience',
`position_id`        int(11)       NOT NULL 				COMMENT 'a foreign key that references  positions.position_id',
`name`               varchar(100)  NOT NULL					COMMENT 'The name of the experience',
`description`        varchar(2000) NOT NULL                 COMMENT 'A description of the experience',
`hyperlink`          varchar(100)  DEFAULT NULL             COMMENT 'A link where people can learn more about the experience',
`start_date`         date          DEFAULT NULL             COMMENT 'The start date of the experience',
`end_date`           date          DEFAULT NULL             COMMENT 'The end date of the experience',
PRIMARY KEY (`experience_id`),
FOREIGN KEY (position_id) REFERENCES positions(position_id)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COMMENT="Experiences I had";