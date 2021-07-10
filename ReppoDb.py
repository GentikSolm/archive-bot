import mysql.connector as sql
import logging
from datetime import datetime

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
        rank = self.getPos(context[1].id)
        vibes = (flag, userData, rank)
        if self.logLevel == 1:
            print(f'{context[0]} vibechecked {context[1]}- returned {vibes[1]}.')
        return vibes

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
        r_flag, r_userData = self.getUserData(data['receiver'])
        s_flag, s_userData = self.getUserData(data['sender'])
        #Need to check if sender exists, and their transaction count
        if r_flag:
            if r_userData[0] >= 2147483647:
                raise OutOfRange(r_userData[0])
            elif s_userData[0] >= RANK_REPS[1]:
                rep = 3
            elif s_userData[0] >= RANK_REPS[0]:
                rep = 2
            else:
                rep = 1
        else:
            self.addUser(data['receiver'])
        sqlStr = f'UPDATE users SET rep = rep + {rep} WHERE user_id = {data["receiver"]}'
        self.cursor.execute(sqlStr)
        self.cnx.commit()
        self.addTrans(data)
        if self.logLevel == 1:
            print(f'{context[0]} thanked {context[1]}')
        if self.logLevel == 2:
            print(sqlStr)
        logging.debug(sqlStr)
        return (rep, r_userData[2])

    def curse(self, data, context):
        r_flag, r_userData = self.getUserData(data['receiver'])
        s_flag, s_userData = self.getUserData(data['sender'])
        #Need to check if sender exists, and their transaction count
        if r_flag:
            if r_userdata[0] <= -2147483647:
                raise OutOfRange(r_userData[0])
            elif s_userData[0] >= RANK_REPS[1]:
                rep = 3
            elif s_userData[0] >= RANK_REPS[0]:
                rep = 2
            else:
                rep = 1
        else:
            self.addUser(data['receiver'])
        sqlStr = f'UPDATE users SET rep = rep - {rep} WHERE user_id = {data["receiver"]}'
        self.cursor.execute(sqlStr)
        self.cnx.commit()
        self.addTrans(data)
        if self.logLevel == 1:
            print(f'{context[0]} cursed {context[1]}')
        if self.logLevel == 2:
            print(sqlStr)
        logging.debug(sqlStr)
        return (rep, r_userData[2])

    def leaderboard(self):
        sqlStr = f'SELECT user_id, rep FROM users ORDER BY rep DESC LIMIT 5'
        self.cursor.execute(sqlStr)
        logging.debug(sqlStr)
        if self.logLevel == 2:
            print(sqlStr)
        if self.logLevel == 1:
            print('Someone called Leaderboard')
        return self.cursor.fetchall()
