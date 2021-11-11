DELIMITER $$
CREATE DEFINER=`root`@`localhost` PROCEDURE `checkLastTrans`(IN sender VARCHAR(45), IN receiver VARCHAR(45), IN action_id INT)
BEGIN
	SELECT time FROM transactions t WHERE t.sender = sender AND t.receiver = receiver AND t.action_id = action_id ORDER BY time DESC LIMIT 1;
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`root`@`localhost` PROCEDURE `getLeaderboard`(IN _limit INT)
BEGIN
	SELECT user_id, rep FROM users ORDER BY rep DESC LIMIT _limit;
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`root`@`localhost` PROCEDURE `getLeaderboardPos`(IN user_id VARCHAR(45))
BEGIN
	SELECT (SELECT COUNT(*) FROM users u WHERE u.rep >= rep) FROM users us WHERE us.user_id = user_id;
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`root`@`localhost` PROCEDURE `getUserData`(IN user_id VARCHAR(45))
BEGIN
	SELECT rep, total_trans, mention_flag FROM users us WHERE us.user_id = user_id;
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`root`@`localhost` PROCEDURE `incRep`(IN user_id VARCHAR(45), IN rep INT)
BEGIN
	UPDATE users u SET u.rep = u.rep + rep WHERE u.user_id = user_id;
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
CREATE DEFINER=`root`@`localhost` PROCEDURE `setMentionFlag`(IN user_id VARCHAR(45), IN flag bool)
BEGIN
	UPDATE users u SET u.mention_flag = flag WHERE u.user_id = user_id;
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`root`@`localhost` PROCEDURE `insertUser`(IN user_Id VARCHAR(45), IN rep INT)
BEGIN
	INSERT INTO users (user_id, rep) VALUES (user_Id, rep);
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`root`@`localhost` PROCEDURE `setRep`(IN user_id VARCHAR(45), IN rep INT)
BEGIN
	INSERT INTO users (user_id, rep) VALUE (user_id, rep);
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`root`@`localhost` PROCEDURE `updateRep`(IN user_id VARCHAR(45), IN rep INT)
BEGIN
	UPDATE users u SET rep = rep WHERE u.user_id = user_id;
END$$
DELIMITER ;
