import discord
import os
import sys
import logging
from datetime import datetime
from dotenv import load_dotenv
from discord_slash import SlashCommand # Importing the newly installed library.
from discord_slash.utils.manage_commands import create_option
from discord_slash.utils.manage_commands import create_permission
from discord_slash.model import SlashCommandPermissionType
import mysql.connector as sql

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
    def getUserData(self, user_id):
        sqlStr = f'SELECT user_id, rep FROM users WHERE user_id = {user_id}'
        self.cursor.execute(sqlStr)
        userData = self.cursor.fetchall()
        logging.debug(sqlStr + f'\n\t Returned {userData}')
        if self.logLevel == 2:
            print(sqlStr)
            print(f'\t Returned {userData}')
        if userData == []:
            return (False, userData)
        return (True, userData[0][1])
    def vibeCheck(self, context):
        vibes = self.getUserData(context[1].id)
        if self.logLevel == 1:
            print(f'{context[0]} vibechecked {context[1]}- returned {vibes[1]}.')
        return vibes
    def setrep(self, data, context, rep):
        if abs(rep) >= 2147483647:
            logging.error(f'Rep out of range (2147483647): {rep}')
            print(f'ERROR:\tREP OUT OF RANGE (2147483647): {rep}')
            raise Exception('OutOfRange')
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
        userData = self.getUserData(data['receiver'])
        if userData[0]:
            if userData[1] >= 2147483647:
                logging.error(f'{data["receiver"]} already has max rep.')
                print(f'ERROR:\t{data["receiver"]} already has max rep.')
                raise Exception('OutOfRange')
        else:
            self.addUser(data['receiver'])
        sqlStr = f'UPDATE users SET rep = rep + 1 WHERE user_id = {data["receiver"]}'
        self.cursor.execute(sqlStr)
        self.cnx.commit()
        self.addTrans(data)
        if self.logLevel == 1:
            print(f'{context[0]} thanked {context[1]}')
        if self.logLevel == 2:
            print(sqlStr)
        logging.debug(sqlStr)
    def curse(self, data, context):
        userData = self.getUserData(data['receiver'])
        if userData[0]:
            if userData[1] <= -2147483647:
                logging.error(f'{data["receiver"]} already has max negative rep.')
                print(f'ERROR:\t{data["receiver"]} already has max negative rep.')
                raise Exception('OutOfRange')
        else:
            self.addUser(data['receiver'])
        sqlStr = f'UPDATE users SET rep = rep - 1 WHERE user_id = {data["receiver"]}'
        self.cursor.execute(sqlStr)
        self.cnx.commit()
        self.addTrans(data)
        if self.logLevel == 1:
            print(f'{context[0]} cursed {context[1]}')
        if self.logLevel == 2:
            print(sqlStr)
        logging.debug(sqlStr)
    def leaderboard(self):
        sqlStr = f'SELECT user_id, rep FROM users ORDER BY rep DESC LIMIT 5'
        self.cursor.execute(sqlStr)
        logging.debug(sqlStr)
        if self.logLevel == 2:
            print(sqlStr)
        return self.cursor.fetchall()
load_dotenv()
client = discord.Client(intents=discord.Intents.all())
slash = SlashCommand(client, sync_commands=True)
guild_ids = os.getenv('GUID').split()
for i in range(0, len(guild_ids)):
    guild_ids[i] = int(guild_ids[i])
server_roles = {
    'admin':os.getenv('ADMIN_ROLE_ID'),
    'everyone':os.getenv('EVERYONE_ROLE_ID'),
    'owner':os.getenv('OWNER'),
    'everyone2':os.getenv('EVERYONE_ROLE_ID_2')
}

@slash.slash(name='thank',
                description="Thank user by adding rep",
                options=[create_option(
                    name="user",
                    description="The user you wish to +rep",
                    option_type=6,
                    required=True)],
                guild_ids=guild_ids)
async def thank(ctx, user):
    data = {
        'action_id':1,
        'sender':ctx.author.id,
        'receiver':user.id,
        'time':str(datetime.now())[:-7],
        'setrep_param':None
    }
    if data['receiver'] == data['sender']:
         await ctx.send(f"You cant rate yourself bro...")
         return
    context = (ctx.author, user)
    try:
        db.thank(data, context)
        await ctx.send(f"+rep to {user}!")
    except Exception:
        await ctx.send(f"Wow, {user} person is awesome. They have the max rep!")

@slash.slash(name='curse',
                description="Curse user by taking rep",
                options=[create_option(
                    name="user",
                    description="The user you wish to -rep",
                    option_type=6,
                    required=True)],
                guild_ids=guild_ids)
async def curse(ctx, user):
    data = {
        'action_id':2,
        'sender':ctx.author.id,
        'receiver':user.id,
        'time':str(datetime.now())[:-7],
        'setrep_param':None
    }
    if data['receiver'] == data['sender']:
         await ctx.send(f"You cant rate yourself bro...")
         return
    context = (ctx.author, user)
    try:
        db.curse(data, context)
        await ctx.send(f"-rep to {user}!")
    except Exception:
        await ctx.send(f"Wow, this {user} sucks. They have hit rock bottom and cannot be cursed any more...")

@slash.slash(name='vibe-check',
                description="See how much rep a user has",
                options=[create_option(
                    name="user",
                    description="The user you'd like to vibe check",
                    option_type=6,
                    required=True)],
                guild_ids=guild_ids)
async def vibeCheck(ctx, user):
    context = (ctx.author, user)
    data = db.vibeCheck(context)
    if not data[0]:
        await ctx.send(f"{user} has never been given, or had rep taken.")
    else:
        await ctx.send(f"{user} has {data[1]} rep.")

@slash.slash(name='setrep',
                description="Set rep of user",
                options=[
                    create_option(
                        name="user",
                        description="The user you'd like to return to void",
                        option_type=6,
                        required=True),
                    create_option(
                        name="rep",
                        description="Ammount of rep",
                        option_type=4,
                        required=True)],
                permissions={
                    guild_ids[0]:[
                        create_permission(server_roles['everyone'], SlashCommandPermissionType.ROLE, False),
                        create_permission(server_roles['admin'], SlashCommandPermissionType.ROLE, True)
                        ],
                    guild_ids[1]:[
                        create_permission(server_roles['everyone2'], SlashCommandPermissionType.ROLE, False),
                        create_permission(server_roles['owner'], SlashCommandPermissionType.ROLE, True)
                    ]},
                guild_ids=guild_ids)
async def setrep(ctx, user, rep):
    data = {
        'action_id':3,
        'sender':ctx.author.id,
        'receiver':user.id,
        'time':str(datetime.now())[:-7],
        'setrep_param':rep
    }
    context = (ctx.author, user)
    try:
        db.setrep(data, context, rep)
        await ctx.send(f"{user.mention} has had their rep set to {rep}")
    except Exception:
        await ctx.send(f"Oops, that number was out of range! Number must be in range ±2147483646")

@slash.slash(name='leaderboard',
                description="Display the top 5 most reputable people",
                guild_ids=guild_ids)
async def leaderboard(ctx):
    topUsers = db.leaderboard()
    topUsersString = "Top users:\n>>> "
    for count, user in enumerate(topUsers):
        topUsersString += f"{count+1}) {await client.fetch_user(user[0])} with {user[1]} rep.\n"
    await ctx.send(topUsersString)

if __name__ == '__main__':
    if '-d' in sys.argv:
        logging.basicConfig(filename='reppo.log', encoding='utf-8', level=logging.DEBUG, format='%(asctime)s %(message)s')
        logLevel = 2
    elif '-v' in sys.argv:
        logging.basicConfig(filename='reppo.log', encoding='utf-8', level=logging.INFO, format='%(asctime)s %(message)s')
        logLevel = 1
    else:
        logging.basicConfig(filename='reppo.log', encoding='utf-8', level=logging.WARNING, format='%(asctime)s %(message)s')
        logLevel = 0;
    dbConfig = {
        'user':os.getenv('DB_USERNAME'),
        'password':os.getenv('DB_PASSWORD'),
        'host':'127.0.0.1',
        'database':'reppo'
    }
    db = Database(dbConfig, logLevel)
    client.run(os.getenv('TOKEN'))
