import discord
import os
from dotenv import load_dotenv
from discord_slash import SlashCommand # Importing the newly installed library.
from discord_slash.utils.manage_commands import create_option
load_dotenv()

class User:
    def __init__(self):
        self.rep = 0
    def vibeCheckUser(self):
        return self.rep
    def thankUser(self):
        self.rep += 1
        return
    def curseUser(self):
        self.rep -= 1
class dataBase:
    def __init__(self):
        self.users = {}
    def checkUserExists(self, user):
        if user in self.users:
            return True
        else:
            return False
    def addUser(self, user):
        self.users[user] = User()
    def vibeCheck(self, user):
        if not self.checkUserExists(user):
            return None
        else:
            return self.users[user].vibeCheckUser()
    def thank(self, user):
        if not self.checkUserExists(user):
            self.addUser(user)
        self.users[user].thankUser()
    def curse(self, user):
        if not self.checkUserExists(user):
            self.addUser(user)
        self.users[user].curseUser()
    def delUser(self, user):
        if not self.checkUserExists(user):
            return
        del self.users[user]

db = dataBase()
client = discord.Client(intents=discord.Intents.all())
slash = SlashCommand(client, sync_commands=True)
guild_ids = [852591935938887721]

@slash.slash(name='thank',
                description="Thank user by adding rep",
                options=[create_option(
                    name="user",
                    description="The user you wish to +rep",
                    option_type=6,
                    required=True)],
                guild_ids=guild_ids)
async def thank(ctx, user: str):
    db.thank(user)
    await ctx.send(f"+rep to <@{user}>!")

@slash.slash(name='curse',
                description="Curse user by taking rep",
                options=[create_option(
                    name="user",
                    description="The user you wish to -rep",
                    option_type=6,
                    required=True)],
                guild_ids=guild_ids)
async def curse(ctx, user: str):
    db.curse(user)
    await ctx.send(f"+rep to @{user}!")

@slash.slash(name='vibe-check',
                description="See how much rep a user has",
                options=[create_option(
                    name="user",
                    description="The user you'd like to vibe check",
                    option_type=6,
                    required=True)],
                guild_ids=guild_ids)
async def vibeCheck(ctx, user: str):
    tempRep = db.vibeCheck(user)
    if tempRep == None:
        await ctx.send(f"{user} has never been given, or had rep taken.")
    else:
        await ctx.send(f"{user} has {tempRep} rep.")

#Need perms here!
@slash.slash(name='deleteuser',
                description="Delete user from database",
                options=[create_option(
                    name="user",
                    description="The user you'd like to return to void",
                    option_type=6,
                    required=True)],
                guild_ids=guild_ids)
async def vibeCheck(ctx, user: str):
    db.delUser(user)
    await ctx.send(f"{user} has never been returned to the void.")



client.run(os.getenv('TOKEN'))
