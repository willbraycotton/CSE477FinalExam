CREATE TABLE IF NOT EXISTS `user_boards` (
    `user_id`        int(11)     NOT NULL,
    `board_id`       int(11)     NOT NULL,
    PRIMARY KEY (`user_id`, `board_id`),
    FOREIGN KEY (`user_id`) REFERENCES `users`(`user_id`) ON DELETE CASCADE,
    FOREIGN KEY (`board_id`) REFERENCES `boards`(`board_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Links users to boards in a many-to-many relationship';
