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
        self.cnxString = config
        self.logLevel = logLevel

    def addUser(self, user_id):
        # adds user_id to db with 0 rep, retunrs nothing
        status = self.callProc("insertUser", (user_id, 0))
        logging.debug(status)

    def addTrans(self, data):
        # Adds transaction to db, with everthing in data. Returns nothing
        args = (data["action_id"], data["sender"], data["receiver"], data["setrep_param"])
        status = self.callProc("insertTrans", args)
        logging.debug(status)

    def getPos(self, user_id):
        # returns the [int] position in leaderboard of the user with user_id.
        userData = self.callProc("getLeaderboardPos", (user_id,))
        logging.debug(f'\n\t Returned {userData}')
        return userData[0][0]

    def getUserData(self, user_id):
        # checks db for user_id and returns a dict with all info on user
        # dict contains:
        #   exists, rep, total_trans, mention_flag, pos
        # POS IS NOT DECLARED, SINCE IT IS VERY EXPENSIVE. MUST BE GATHERED FROM getPos IF NEEDED
        userData = self.callProc("getUserData", (user_id,))
        logging.debug(f'\n\t Returned {userData}')
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
            self.callProc("updateRep", (data['receiver'], rep))
        else:
            self.callProc("setRep", (data['receiver'], rep))
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

        args = (data['sender'], data['receiver'], 1)
        payload = self.callProc("checkLastTrans", args)
        if payload != []:
            time = payload[0][0]
            if repeatTime == 'NEVER':
                return (0, r_userDict['mention_flag'], 3)
            elif repeatTime == 'MONTH':
                if not (time + timedelta(weeks=4)) < datetime.now():
                    return (0, r_userDict['mention_flag'], 4)

        args = (data["receiver"], rep)
        self.callProc("incRep", args)
        self.addTrans(data)
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

        payload = self.callProc("checkLastTrans", (data['sender'], data['receiver'], 2))

        if payload != []:
            time = payload[0][0]
            if repeatTime == 'NEVER':
                return (0, r_userDict['mention_flag'], 3)
            elif repeatTime == 'MONTH':
                if not (time + timedelta(weeks=4)) < datetime.now():
                    return (0, r_userDict['mention_flag'], 4)

        self.callProc("incRep", (data["receiver"], rep))
        self.addTrans(data)
        return (rep, r_userDict['mention_flag'], 1)

    def leaderboard(self):
        # retuns the top users in the db by rep. DOES NOT GUARENTEE 5
        leaderboard = self.callProc("getLeaderboard", (5,))
        # logging.debug(status)
        return leaderboard

    def setMentionFlag(self, flag, user_id):
        # sets mention flag of user_id to flag
        self.callProc("setMentionFlag", (user_id, flag))

    def insertGame(self, user_id, game):
        try:
            self.callProc("insertGame", (game, user_id))
            return 0
        except sql.Error as err:
            if(err.errno == 1062):
                print("Duplicate entry")
                return 1
            else:
                print(err)
                return -1

    def listGames(self, user):
        return self.callProc("getGames", (user,))

    def removeGame(self, user, game):
        self.callProc("removeGame", (game, user))

    def callProc(self, storedProcedure, args):
        try:
            cnx = sql.connect(**self.cnxString)
        except Exception as e:
            print(e)
            print("Cannot connect to Database, see MySql in services.msc")
            print("EXITING")
            logging.error("Database connection failed")
            exit()
        if(self.logLevel >= 1):
            print(storedProcedure, ": ", args)
        cursor = cnx.cursor()
        cursor.callproc(storedProcedure, args)
        payload = None
        for result in cursor.stored_results():
            payload = result.fetchall()
        if(self.logLevel >= 1):
            print('\t- ' + str(payload))
        cursor.close()
        cnx.commit()
        cnx.close()
        logging.debug(storedProcedure)
        logging.debug(args)
        logging.debug(payload)
        return payload
