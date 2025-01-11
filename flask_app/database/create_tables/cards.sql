CREATE TABLE IF NOT EXISTS `cards` (
    `card_id` INT(11) NOT NULL AUTO_INCREMENT,
    `name` VARCHAR(255) NOT NULL,
    `list` ENUM('To Do', 'Doing', 'Completed') NOT NULL,
    `board_id` INT(11) NOT NULL,
    PRIMARY KEY (`card_id`),
    FOREIGN KEY (`board_id`) REFERENCES `boards`(`board_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Contains card information';