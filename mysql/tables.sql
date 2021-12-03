CREATE DATABASE `reppo` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
CREATE TABLE `actions` (
  `action_id` int NOT NULL AUTO_INCREMENT,
  `action_name` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`action_id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `games` (
  `user_id` varchar(45) NOT NULL,
  `game_name` varchar(45) NOT NULL,
  PRIMARY KEY (`user_id`,`game_name`),
  CONSTRAINT `FK_games_users` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `tags` (
  `user_id` varchar(45) NOT NULL,
  `tag_name` varchar(20) NOT NULL,
  `platform` varchar(20) NOT NULL,
  PRIMARY KEY (`user_id`,`tag_name`),
  CONSTRAINT `FK_tag_users` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `transactions` (
  `transaction_id` int NOT NULL AUTO_INCREMENT,
  `action_id` int NOT NULL,
  `sender` varchar(45) NOT NULL,
  `receiver` varchar(45) NOT NULL,
  `time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `setrep_param` int DEFAULT NULL,
  PRIMARY KEY (`transaction_id`),
  KEY `user_id_idx` (`sender`,`receiver`),
  KEY `receiver_idx` (`receiver`),
  KEY `FK_action_actions_idx` (`action_id`),
  CONSTRAINT `FK_action_actions` FOREIGN KEY (`action_id`) REFERENCES `actions` (`action_id`),
  CONSTRAINT `FK_receiver_users` FOREIGN KEY (`receiver`) REFERENCES `users` (`user_id`),
  CONSTRAINT `FK_sender_users` FOREIGN KEY (`sender`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=308 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `users` (
  `user_id` varchar(45) NOT NULL,
  `rep` int NOT NULL,
  `total_trans` int NOT NULL DEFAULT '0',
  `mention_flag` tinyint NOT NULL DEFAULT '0',
  `username` varchar(45) DEFAULT NULL,
  `bio` varchar(512) DEFAULT NULL,
  `avatar` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
