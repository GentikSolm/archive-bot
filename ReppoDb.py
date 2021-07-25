import mysql.connector as sql
import logging
from datetime import datetime, timedelta

RANK_REPS = [10, 100]
# These are the min rep required for each rank

class OutOfRange(Exception):
    # Custom exception class for handling ints too big for db
    def __init__(self, rep, message='Out of Range'):
        logging.error(f'Rep out of range (2147483647): {rep}')
        print(f'ERROR:\tREP OUT OF RANGE (2147483647): {rep}')
        super(OutOfRange, self).__init__(message)

class Database:
    def __init__(self, config, logLevel):
        try:
            self.cnx = sql.connect(**config)
            self.cursor = self.cnx.cursor()
            self.insertUser = ('INSERT INTO users'
                               '(user_id, rep)'
                               'VALUES (%s, %s)')
            self.insertTran = ('INSERT INTO transactions'
                               '(action_id, sender, receiver, time, setrep_param)'
                               'VALUES (%(action_id)s, %(sender)s, %(receiver)s, %(time)s, %(setrep_param)s)')
            self.getPosStr = ("SELECT (SELECT COUNT(*) FROM users x WHERE x.rep >= users.rep) FROM users WHERE user_id = %s")
            self.logLevel = logLevel
        except Exception as e:
            print(e)
            print("Cannot connect to Database, see MySql in services.msc")
            print("EXITING")
            logging.error("Database connection failed")
            exit()
    def __del__(self):
        self.cursor.close()
        self.cnx.close()
    def addUser(self, user_id):
        # adds user_id to db with 0 rep, retunrs nothing
        self.cursor.execute(self.insertUser, (user_id, 0))
        self.cnx.commit()
        if self.logLevel == 2:
            print(self.insertUser % (user_id, 0))
        logging.debug(self.insertUser % (user_id, 0))
    def addTrans(self, data):
        # Adds transaction to db, with everthing in data. Returns nothing
        self.cursor.execute(self.insertTran, data)
        self.cnx.commit()
        if self.logLevel == 2:
            print(self.insertTran % (data))
        logging.debug(self.insertTran % (data))
    def getPos(self, user_id):
        # returns the [int] position in leaderboard of the user with user_id.
        self.cursor.execute(self.getPosStr % user_id)
        userData = self.cursor.fetchall()
        logging.debug(f'\n\t Returned {userData}')
        if self.logLevel == 2:
            print(self.getPosStr, user_id)
            print(f'\t Returned {userData}')
        return userData[0][0]
    def getUserData(self, user_id):
        # checks db for user_id and returns a dict with all info on user
        # dict contains:
        #   exists, rep, total_trans, mention_flag, pos
        # POS IS NOT DECLARED, SINCE IT IS VERY EXPENSIVE. MUST BE GATHERED FROM getPos IF NEEDED
        sqlStr = f'SELECT rep, total_trans, mention_flag FROM users WHERE user_id = {user_id}'
        self.cursor.execute(sqlStr)
        userData = self.cursor.fetchall()
        logging.debug(sqlStr + f'\n\t Returned {userData}')
        if self.logLevel == 2:
            print(sqlStr)
            print(f'\t Returned {userData}')
        if userData == []:
            userDict = {
                'exists': False,
                'rep': 0,
                'total_trans': 0,
                'mention_flag': 0,
                'pos':None
            }
            return userDict
        userDict = {
            'exists': True,
            'rep': userData[0][0],
            'total_trans': userData[0][1],
            'mention_flag': userData[0][2],
            'pos':None
        }
        return userDict
    def vibeCheck(self, user_id):
        # collects all info from userData and finds & updates pos in userDict.
        # returns userDict with pos
        userDict = self.getUserData(user_id)
        if userDict['exists']:
            userDict['pos'] = self.getPos(user_id)
        if self.logLevel == 1:
            print(f'{user_id} was vibechecked- returned {vibes}.')
        return userDict
    def checkRank(self, rep):
        # returns perms for each rank depending on rep
        #   (rep, transLimit, repeatTime, mesPerm)
        if rep >= RANK_REPS[1]:
            rep = 3
            transLimit = -1
            repeatTime = 'MONTH'
            mesPerm = True
        elif rep >= RANK_REPS[0]:
            rep = 2
            transLimit = 50
            repeatTime = 'MONTH'
            mesPerm = False
        else:
            rep = 1
            transLimit = 10
            repeatTime = 'NEVER'
            mesPerm = False
        return (rep, transLimit, repeatTime, mesPerm)
    def setrep(self, data, rep):
        # sets rep of data[receiver] to rep
        # also adds transaction, but this does not count towards trans limit, since it is an
        # admin tool
        if abs(rep) >= 2147483647:
            raise OutOfRange(rep)
        if (self.getUserData(data['receiver'])['exists']):
            sqlStr = f'UPDATE users SET rep = {rep} WHERE user_id = {data["receiver"]}'
        else:
            sqlStr = f'INSERT INTO users (user_id, rep) VALUE ({data["receiver"]}, {rep})'
        self.cursor.execute(sqlStr)
        self.cnx.commit()
        if self.logLevel == 1:
            print(f'{data["sender"]} setrep of {data["receiver"]} to {rep}')
        if self.logLevel == 2:
            print(sqlStr)
        logging.debug(sqlStr)
        self.addTrans(data)
    def thank(self, data):
        # returns (rep, mention_flag, code)
        #   1: Success
        #   2: transLimit Reached
        #   3: repeatTime is never
        #   4: Too soon since last
        r_userDict = self.getUserData(data['receiver'])
        s_userDict = self.getUserData(data['sender'])
        if not r_userDict['exists']:
            self.addUser(data['receiver'])
        if not s_userDict['exists']:
            self.addUser(data['sender'])
        rep, transLimit, repeatTime, mesPerm = self.checkRank(s_userDict['rep'])

        if s_userDict['total_trans'] >= transLimit and transLimit != -1:
            return (0, r_userDict['mention_flag'], 2)

        sqlStr = f"SELECT time, action_id FROM transactions WHERE sender = {data['sender']} AND receiver = {data['receiver']} AND action_id = 1 ORDER BY time DESC LIMIT 1;"
        self.cursor.execute(sqlStr)
        payload = self.cursor.fetchall()

        if self.logLevel == 1:
            print(f"Checked last trans of {data['sender']} AND {data['receiver']}- {payload}")
        if self.logLevel == 2:
            print(sqlStr, payload)

        if payload != []:
            time, action_id = payload[0]
            if action_id == 1:
                if repeatTime == 'NEVER':
                    return (0, r_userDict['mention_flag'], 3)
                elif repeatTime == 'MONTH':
                    if not (time + timedelta(weeks=4)) < datetime.now():
                        return (0, r_userDict['mention_flag'], 4)

        sqlStr = f'UPDATE users SET rep = rep + {rep} WHERE user_id = {data["receiver"]}'
        self.cursor.execute(sqlStr)
        self.cnx.commit()
        self.addTrans(data)
        if self.logLevel == 1:
            print(f'{data["sender"]} thanked {data["receiver"]}')
        if self.logLevel == 2:
            print(sqlStr)
        logging.debug(sqlStr)
        return (rep, r_userDict['mention_flag'], 1)
    def curse(self, data):
        # returns (rep, mention_flag, code)
        #   1: Success
        #   2: transLimit Reached
        #   3: repeatTime is never
        #   4: Too soon since last
        r_userDict = self.getUserData(data['receiver'])
        s_userDict = self.getUserData(data['sender'])
        if not r_userDict['exists']:
            self.addUser(data['receiver'])
        if not s_userDict['exists']:
            self.addUser(data['sender'])
        rep, transLimit, repeatTime, mesPerm = self.checkRank(s_userDict['rep'])

        if r_userDict['total_trans'] >= transLimit and transLimit != -1:
            return (0, r_userDict['mention_flag'], 2)

        sqlStr = f"SELECT time, action_id FROM transactions WHERE sender = {data['sender']} AND receiver = {data['receiver']} ORDER BY time DESC LIMIT 1;"
        self.cursor.execute(sqlStr)
        payload = self.cursor.fetchall()

        if self.logLevel == 1:
            print(f"Checked last trans of {data['sender']} AND {data['receiver']}- {payload}")
        if self.logLevel == 2:
            print(sqlStr, payload)

        if payload != []:
            time, action_id = payload[0]
            if action_id == 2:
                if repeatTime == 'NEVER':
                    return (0, r_userDict['mention_flag'], 3)
                elif repeatTime == 'MONTH':
                    if not (time + timedelta(weeks=4)) < datetime.now():
                        return (0, r_userDict['mention_flag'], 4)

        sqlStr = f'UPDATE users SET rep = rep - {rep} WHERE user_id = {data["receiver"]}'
        self.cursor.execute(sqlStr)
        self.cnx.commit()
        self.addTrans(data)
        if self.logLevel == 1:
            print(f'{data["sender"]} cursed {data["receiver"]}')
        if self.logLevel == 2:
            print(sqlStr)
        logging.debug(sqlStr)
        return (rep, r_userDict['mention_flag'], 1)
    def leaderboard(self):
        # retuns the top users in the db by rep. DOES NOT GUARENTEE 5
        sqlStr = f'SELECT user_id, rep FROM users ORDER BY rep DESC LIMIT 5'
        self.cursor.execute(sqlStr)
        logging.debug(sqlStr)
        if self.logLevel == 2:
            print(sqlStr)
        if self.logLevel == 1:
            print('Someone called Leaderboard')
        return self.cursor.fetchall()
    def setMentionFlag(self, flag, user_id):
        # sets mention flag of user_id to flag
        sqlStr = f"UPDATE users SET mention_flag = {flag} WHERE user_id = {user_id}"
        self.cursor.execute(sqlStr)
        self.cnx.commit()
