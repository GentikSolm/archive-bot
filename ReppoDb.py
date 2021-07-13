import mysql.connector as sql
import logging
from datetime import datetime, timedelta

RANK_REPS = [10, 100]

class OutOfRange(Exception):
    def __init__(self, rep, message='Out of Range'):
        logging.error(f'Rep out of range (2147483647): {rep}')
        print(f'ERROR:\tREP OUT OF RANGE (2147483647): {rep}')
        super(OutOfRange, self).__init__(message)

class Database:
    def __init__(self, config, logLevel):
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
    def __del__(self):
        self.cursor.close()
        self.cnx.close()
    def addUser(self, user_id):
        self.cursor.execute(self.insertUser, (user_id, 0))
        self.cnx.commit()
        if self.logLevel == 2:
            print(self.insertUser % (user_id, 0))
        logging.debug(self.insertUser % (user_id, 0))
    def addTrans(self, data):
        self.cursor.execute(self.insertTran, data)
        self.cnx.commit()
        if self.logLevel == 2:
            print(self.insertTran % (data))
        logging.debug(self.insertTran % (data))
    def getPos(self, user_id):
        self.cursor.execute(self.getPosStr % user_id)
        userData = self.cursor.fetchall()
        logging.debug(f'\n\t Returned {userData}')
        if self.logLevel == 2:
            print(self.getPosStr, user_id)
            print(f'\t Returned {userData}')
        return userData[0][0]
    def getUserData(self, user_id):
        # userData is [rep, total_trans, mention_flag]
        sqlStr = f'SELECT rep, total_trans, mention_flag FROM users WHERE user_id = {user_id}'
        self.cursor.execute(sqlStr)
        userData = self.cursor.fetchall()
        logging.debug(sqlStr + f'\n\t Returned {userData}')
        if self.logLevel == 2:
            print(sqlStr)
            print(f'\t Returned {userData}')
        if userData == []:
            return (False, userData)
        return (True, userData[0])
    def vibeCheck(self, context):
        # Vibes is (User exists, [rep], rank)
        flag, userData = self.getUserData(context[1].id)
        if flag:
            pos = self.getPos(context[1].id)
        else:
            pos = None
        vibes = (flag, userData, pos)
        if self.logLevel == 1:
            print(f'{context[0]} vibechecked {context[1]}- returned {vibes[1]}.')
        return vibes
    def checkRank(self, rep):
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
    def setrep(self, data, context, rep):
        if abs(rep) >= 2147483647:
            raise OutOfRange(rep)
        if (self.getUserData(data['receiver']))[0]:
            sqlStr = f'UPDATE users SET rep = {rep} WHERE user_id = {data["receiver"]}'
        else:
            sqlStr = f'INSERT INTO users (user_id, rep) VALUE ({data["receiver"]}, {rep})'
        self.cursor.execute(sqlStr)
        self.cnx.commit()
        if self.logLevel == 1:
            print(f'{context[0]} setrep of {context[1]} to {rep}')
        if self.logLevel == 2:
            print(sqlStr)
        logging.debug(sqlStr)
        self.addTrans(data)
    def thank(self, data, context):
        # returns (rep, mention_flag, code)
        #   1: Success
        #   2: transLimit Reached
        #   3: repeatTime is never
        #   4: Too soon since last
        r_flag, r_userData = self.getUserData(data['receiver'])
        s_flag, s_userData = self.getUserData(data['sender'])
        if not r_flag:
            self.addUser(data['receiver'])
            r_userData = [0,0,0]
        if not s_flag:
            self.addUser(data['sender'])
            s_userData = [0,0,0]
        rep, transLimit, repeatTime, mesPerm = self.checkRank(s_userData[0])

        if s_userData[1] >= transLimit and transLimit != -1:
            return (0, r_userData[2], 2)

        sqlStr = f"SELECT time, action_id FROM transactions WHERE sender = {data['sender']} AND receiver = {data['receiver']} ORDER BY time DESC LIMIT 1;"
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
                    return (0, r_userData[2], 3)
                elif repeatTime == 'MONTH':
                    if not (time + timedelta(weeks=4)) < datetime.now():
                        return (0, r_userData[2], 4)

        sqlStr = f'UPDATE users SET rep = rep + {rep} WHERE user_id = {data["receiver"]}'
        self.cursor.execute(sqlStr)
        self.cnx.commit()
        self.addTrans(data)
        if self.logLevel == 1:
            print(f'{context[0]} thanked {context[1]}')
        if self.logLevel == 2:
            print(sqlStr)
        logging.debug(sqlStr)
        return (rep, r_userData[2], 1)
    def curse(self, data, context):
        # returns (rep, mention_flag, code)
        #   1: Success
        #   2: transLimit Reached
        #   3: repeatTime is never
        #   4: Too soon since last
        r_flag, r_userData = self.getUserData(data['receiver'])
        s_flag, s_userData = self.getUserData(data['sender'])
        if not r_flag:
            self.addUser(data['receiver'])
            r_userData = [0,0,0]
        if not s_flag:
            self.addUser(data['sender'])
            s_userData = [0,0,0]
        rep, transLimit, repeatTime, mesPerm = self.checkRank(s_userData[0])

        if s_userData[1] >= transLimit and transLimit != -1:
            return (0, r_userData[2], 2)

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
                    return (0, r_userData[2], 3)
                elif repeatTime == 'MONTH':
                    if not (time + timedelta(weeks=4)) < datetime.now():
                        return (0, r_userData[2], 4)

        sqlStr = f'UPDATE users SET rep = rep - {rep} WHERE user_id = {data["receiver"]}'
        self.cursor.execute(sqlStr)
        self.cnx.commit()
        self.addTrans(data)
        if self.logLevel == 1:
            print(f'{context[0]} cursed {context[1]}')
        if self.logLevel == 2:
            print(sqlStr)
        logging.debug(sqlStr)
        return (rep, r_userData[2], 1)
    def leaderboard(self):
        sqlStr = f'SELECT user_id, rep FROM users ORDER BY rep DESC LIMIT 5'
        self.cursor.execute(sqlStr)
        logging.debug(sqlStr)
        if self.logLevel == 2:
            print(sqlStr)
        if self.logLevel == 1:
            print('Someone called Leaderboard')
        return self.cursor.fetchall()
    def setMentionFlag(self, flag, user_id):
        sqlStr = f"UPDATE users SET mention_flag = {flag} WHERE user_id = {user_id}"
        self.cursor.execute(sqlStr)
        self.cnx.commit()
