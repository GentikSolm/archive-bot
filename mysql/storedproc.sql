DELIMITER $$
CREATE DEFINER=`root`@`localhost` PROCEDURE `checkLastTrans`(IN sender VARCHAR(45), IN receiver VARCHAR(45), IN action_id INT)
BEGIN
	SELECT time FROM transactions t WHERE t.sender = sender AND t.receiver = receiver AND t.action_id = action_id ORDER BY time DESC LIMIT 1;
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`root`@`localhost` PROCEDURE `getGames`(IN userId varchar(45))
BEGIN
	SELECT game_name FROM games WHERE user_id = userId;
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`root`@`localhost` PROCEDURE `getLeaderboard`(IN _limit INT, IN _page INT)
BEGIN
    DECLARE _start INT;
    DECLARE _end INT;
    SET _start = _limit * (_page-1);
    SET _end = _limit * _page;
    SELECT user_id, rep FROM users ORDER BY rep DESC LIMIT _start,_end;
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`root`@`localhost` PROCEDURE `getLeaderboardPos`(IN user_id VARCHAR(45))
BEGIN
	SELECT (SELECT COUNT(*) FROM users x WHERE x.rep >= users.rep) FROM users WHERE users.user_id = user_id;
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`root`@`localhost` PROCEDURE `getUserData`(IN user_id VARCHAR(45))
BEGIN
	SELECT rep, total_trans, mention_flag, bio FROM users us WHERE us.user_id = user_id;
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`root`@`localhost` PROCEDURE `incRep`(IN user_id VARCHAR(45), IN rep INT)
BEGIN
	UPDATE users u SET u.rep = u.rep + rep WHERE u.user_id = user_id;
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`root`@`localhost` PROCEDURE `insertGame`(IN game varchar(20), IN userId varchar(45))
BEGIN
	INSERT INTO games SET game_name = game, user_id = userId;
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`root`@`localhost` PROCEDURE `insertTrans`(IN action_id INT, IN sender VARCHAR(45), IN receiver VARCHAR(45), IN setrep_param INT)
BEGIN
	INSERT INTO transactions
	(action_id, sender, receiver, setrep_param)
	VALUES (action_id, sender, receiver, setrep_param);
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`root`@`localhost` PROCEDURE `insertUser`(IN user_Id VARCHAR(45), IN rep INT)
BEGIN
	INSERT INTO users (user_id, rep) VALUES (user_Id, rep);
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`root`@`localhost` PROCEDURE `removeGame`(IN game varchar(45),IN userId varchar(45))
BEGIN
	DELETE FROM games WHERE user_id = userId AND game_name = game;
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`root`@`localhost` PROCEDURE `setMentionFlag`(IN user_id VARCHAR(45), IN flag bool)
BEGIN
	UPDATE users u SET u.mention_flag = flag WHERE u.user_id = user_id;
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`root`@`localhost` PROCEDURE `setRep`(IN user_id VARCHAR(45), IN rep INT)
BEGIN
	INSERT INTO users (user_id, rep) VALUE (user_id, rep);
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`Reppo`@`%` PROCEDURE `updateBio`(IN userId varchar(45), IN newBio varchar(512))
BEGIN
	UPDATE users SET bio = newBio WHERE user_id = userId;
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`root`@`localhost` PROCEDURE `updateRep`(IN user_id VARCHAR(45), IN rep INT)
BEGIN
	UPDATE users u SET rep = rep WHERE u.user_id = user_id;
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`Reppo`@`%` PROCEDURE `updateUserInfo`(IN id varchar(45), IN name varchar(45), IN avatar varchar(45))
BEGIN
	UPDATE users SET username = name, avatar = avatar WHERE user_id = id;
END$$
DELIMITER ;
