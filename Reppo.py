import discord
import os
from datetime import date, datetime
from dotenv import load_dotenv
from discord_slash import SlashCommand # Importing the newly installed library.
from discord_slash.utils.manage_commands import create_option
from discord_slash.utils.manage_commands import create_permission
from discord_slash.model import SlashCommandPermissionType
import mysql.connector as sql

load_dotenv()
dbConfig = {
    'user':os.getenv('DB_USERNAME'),
    'password':os.getenv('DB_PASSWORD'),
    'host':'127.0.0.1',
    'database':'reppo'
}
class Database:
    def __init__(self, config):
        self.cnx = sql.connect(**config)
        self.cursor = self.cnx.cursor()
        self.insertUser = ('INSERT INTO users'
                           '(user_id, rep)'
                           'VALUES (%s, %s)')
        self.insertTran = ('INSERT INTO transactions'
                           '(action_id, sender, receiver, time)'
                           'VALUES (%(action_id)s, %(sender)s, %(receiver)s, %(time)s)')
    def __del__(self):
        self.cursor.close()
        self.cnx.close()
    def addUser(self, user_id):
        self.cursor.execute(self.insertUser, (user_id, 0))
        self.cnx.commit()
    def addTrans(self, data):
        self.cursor.execute(self.insertTran, data)
        self.cnx.commit()
    def getUserData(self, user_id):
        self.cursor.execute(f'SELECT * FROM users WHERE user_id = {user_id}')
        userData = self.cursor.fetchall()
        if userData == []:
            return (False, userData)
        return (True, userData[0][1])
    def setrep(self, user_id, rep):
        if (self.getUserData(user_id))[0]:
            self.cursor.execute(f'UPDATE users SET rep = {rep} WHERE user_id = {user_id}')
        else:
            self.cursor.execute(f'INSERT INTO users (user_id, rep) VALUE ({user_id}, {rep})')
        self.cnx.commit()
    def thank(self, data):
        self.addTrans(data)
        if not (self.getUserData(data['receiver']))[0]:
            self.addUser(data['receiver'])
        self.cursor.execute(f'UPDATE users SET rep = rep + 1 WHERE user_id = {data["receiver"]}')
        self.cnx.commit()
    def curse(self, data):
        self.addTrans(data)
        if not (self.getUserData(data['receiver']))[0]:
            self.addUser(data['receiver'])
        self.cursor.execute(f'UPDATE users SET rep = rep - 1 WHERE user_id = {data["receiver"]}')
        self.cnx.commit()
db = Database(dbConfig)
client = discord.Client(intents=discord.Intents.all())
slash = SlashCommand(client, sync_commands=True)
guild_ids = [os.getenv('GUID')]

@slash.slash(name='thank',
                description="Thank user by adding rep",
                options=[create_option(
                    name="user",
                    description="The user you wish to +rep",
                    option_type=6,
                    required=True)],
                guild_ids=guild_ids)
async def thank(ctx, user):
    time = str(datetime.now())[:-7]
    sender = ctx.author.id
    receiver = user.id
    data = {
        'action_id':1,
        'sender':str(sender),
        'receiver':str(receiver),
        'time':time
    }
    db.thank(data)
    print(f'{ctx.author} thanked {user}')
    await ctx.send(f"+rep to {user.mention}!")

@slash.slash(name='curse',
                description="Curse user by taking rep",
                options=[create_option(
                    name="user",
                    description="The user you wish to -rep",
                    option_type=6,
                    required=True)],
                guild_ids=guild_ids)
async def curse(ctx, user):
    time = str(datetime.now())[:-7]
    sender = ctx.author.id
    receiver = user.id
    data = {
        'action_id':2,
        'sender':sender,
        'receiver':receiver,
        'time':time
    }
    db.curse(data)
    print(f'{ctx.author} cursed {user}')
    await ctx.send(f"-rep to {user.mention}!")

@slash.slash(name='vibe-check',
                description="See how much rep a user has",
                options=[create_option(
                    name="user",
                    description="The user you'd like to vibe check",
                    option_type=6,
                    required=True)],
                guild_ids=guild_ids)
async def vibeCheck(ctx, user):
    data = db.getUserData(user.id)
    print(f'{ctx.author} checked {user}')
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
                        create_permission(852591935938887721, SlashCommandPermissionType.ROLE, False),
                        create_permission(855130847933235261, SlashCommandPermissionType.ROLE, True)
                        ]},
                guild_ids=guild_ids)
async def setrep(ctx, user, rep):
    db.setrep(user.id, rep)
    print(f'{ctx.author} setrep for {user}')
    await ctx.send(f"{user.mention} has had their rep set to {rep}")

client.run(os.getenv('TOKEN'))
