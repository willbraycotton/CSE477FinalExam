CREATE TABLE IF NOT EXISTS `boards` (
    `board_id`       int(11)     NOT NULL AUTO_INCREMENT,
    `name`           varchar(255) NOT NULL,
    PRIMARY KEY (`board_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COMMENT='Contains board information';