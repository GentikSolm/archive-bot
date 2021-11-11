import discord
import os
import sys
import logging
from ReppoDb import OutOfRange, Database

from datetime import datetime
from dotenv import load_dotenv
from discord_slash import SlashCommand
from discord_slash.utils.manage_commands import create_option
from discord_slash.utils.manage_commands import create_permission
from discord_slash.model import SlashCommandPermissionType


load_dotenv()
EMBED_COLOR = 0x38e4ff
client = discord.Client(intents=discord.Intents.all())
slash = SlashCommand(client, sync_commands=True)
guild_ids = os.getenv('GUID').split()
for i in range(0, len(guild_ids)):
    guild_ids[i] = int(guild_ids[i])
server_roles = {
    'admin':os.getenv('ADMIN_ROLE_ID'),
    'everyone':os.getenv('EVERYONE_ROLE_ID'),
    'owner':os.getenv('OWNER'),
    'everyone2':os.getenv('EVERYONE_ROLE_ID_2'),
    'jacobEveryone':os.getenv('JACOBSERVER')
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
    # give rep to a user
    data = {
        'action_id':1,
        'sender':ctx.author.id,
        'receiver':user.id,
        'time':str(datetime.now())[:-7],
        'setrep_param':None
    }
    embed = discord.Embed(color=EMBED_COLOR)
    if data['receiver'] == data['sender']:
        embed.set_author(name=f'You cant rate yourself bro...')
        await ctx.send(embed=embed)
        return
    try:
        rep, mention_flag, code = db.thank(data)
        #code is used to determine what the result of the thank was, see db
        if code == 1:
            if mention_flag:
                embed.set_author(name=f'{user} got + {rep} rep!', icon_url=user.avatar_url)
                embed.description = user.mention
            else:
                embed.set_author(name=f'{user} got + {rep} rep!', icon_url=user.avatar_url)
            await ctx.send(embed=embed)
        elif code == 2:
            embed.set_author(name=f'Oi! you\'ve reached your transaction limit!')
            embed.description = "Sorry, no can do, atleast untill you reach the next rank!"
            await ctx.send(embed=embed)
        elif code == 3:
            embed.set_author(name=f'Hold on now')
            embed.description = "Your rank isnt high enough to thank someone twice."
            await ctx.send(embed=embed)
        elif code == 4:
            embed.set_author(name=f'Slow down Fella')
            embed.description = "Gotta wait 4 weeks from your last thank for this user"
            await ctx.send(embed=embed)
    except OutOfRange:
        print(excep)
        embed.set_author(name=f'{user} is awesome, They have the max rep!', icon_url=user.avatar_url)
        await ctx.send(embed=embed)
    except Exception as e:
        logging.error(e)
        print(e)
        embed.title ='Oops, looks like I\'ve lost my marbles.'
        embed.description = 'To the logs!'
        await ctx.send(embed=embed)

@slash.slash(name='curse',
                description="Curse user by taking rep",
                options=[create_option(
                    name="user",
                    description="The user you wish to -rep",
                    option_type=6,
                    required=True)],
                guild_ids=guild_ids)
async def curse(ctx, user):
    # take rep away from user
    data = {
        'action_id':2,
        'sender':ctx.author.id,
        'receiver':user.id,
        'time':str(datetime.now())[:-7],
        'setrep_param':None
    }
    embed = discord.Embed(color=EMBED_COLOR)
    if data['receiver'] == data['sender']:
        embed.set_author(name=f'You cant rate yourself bro...')
        await ctx.send(embed=embed)
        return
    try:
        rep, mention_flag, code = db.curse(data)
        if code == 1:
            if mention_flag:
                embed.set_author(name=f'{user} got - {rep} rep!', icon_url=user.avatar_url)
                embed.description = user.mention
            else:
                embed.set_author(name=f'{user} got - {rep} rep!', icon_url=user.avatar_url)
            await ctx.send(embed=embed)
        elif code == 2:
            embed.set_author(name=f'Oi! you\'ve reached your transaction limit!')
            embed.description = "Sorry, no can do, atleast untill you reach the next rank!"
            await ctx.send(embed=embed)
        elif code == 3:
            embed.set_author(name=f'Hold on now')
            embed.description = "Your rank isnt high enough to curse someone twice."
            await ctx.send(embed=embed)
        elif code == 4:
            embed.set_author(name=f'Slow down Fella')
            embed.description = "Gotta wait 4 weeks from your last curse for this user"
            await ctx.send(embed=embed)
    except OutOfRange:
        embed.set_author(name=f'{user} sucks... They have hit rock bottom and cannot be cursed any more', icon_url=user.avatar_url)
        await ctx.send(embed=embed)
    except Exception as e:
        logging.error(e)
        print(e)
        embed.title ='Oops, looks like I\'ve lost my marbles.'
        embed.description = 'To the logs!'
        await ctx.send(embed=embed)

@slash.slash(name='vibe-check',
                description="See how much rep a user has",
                options=[create_option(
                    name="user",
                    description="The user you'd like to vibe check",
                    option_type=6,
                    required=True)],
                guild_ids=guild_ids)
async def vibeCheck(ctx, user):
    # show all data on a user
    try:
        userDict = db.vibeCheck(user.id)
        embed = discord.Embed(color=EMBED_COLOR)
        if not userDict['exists']:
            embed.set_author(name=f'{user} has never been given, or had rep taken.', icon_url=user.avatar_url)
            await ctx.send(embed=embed)
        else:
            mentionStr = 'Enabled' if userDict["mention_flag"] else 'Disabled'
            embed.set_author(name=f'{user}', icon_url=user.avatar_url)
            embed.add_field(name='Leaderboard', value=f'# **{userDict["pos"]}**', inline=True)
            embed.add_field(name='Reputation', value=f'total: **{userDict["rep"]}**', inline=True)
            embed.add_field(name='Mentions', value=f'**{mentionStr}**', inline=True)
            embed.add_field(name='Transactions', value=f'total: **{userDict["total_trans"]}**', inline=True)
            await ctx.send(embed=embed)
    except Exception as e:
        logging.error(e)
        print(e)
        embed.title ='Oops, looks like I\'ve lost my marbles.'
        embed.description = 'To the logs!'
        await ctx.send(embed=embed)
        return

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
                    ],
                    guild_ids[3]:[
                        create_permission(server_roles['jacobEveryone'], SlashCommandPermissionType.ROLE, False),
                    ]},
                guild_ids=guild_ids)
async def setrep(ctx, user, rep):
    # set the rep of user to rep
    data = {
        'action_id':3,
        'sender':ctx.author.id,
        'receiver':user.id,
        'time':str(datetime.now())[:-7],
        'setrep_param':rep
    }
    embed = discord.Embed(color=EMBED_COLOR)
    try:
        db.setrep(data, rep)
        embed.set_author(name=f'{user} has had their rep set to {rep}', icon_url=user.avatar_url)
        await ctx.send(embed=embed)
    except OutOfRange:
        embed.title ='Oops, that number was out of range!'
        embed.description = 'Number must be in range ±2147483646'
        await ctx.send(embed=embed)
    except Exception as e:
        logging.error(e)
        print(e)
        embed.title ='Oops, looks like I\'ve lost my marbles.'
        embed.description = 'To the logs!'
        await ctx.send(embed=embed)

@slash.slash(name='leaderboard',
                description="Display the top 5 most reputable people",
                guild_ids=guild_ids)
async def leaderboard(ctx):
    # display leaderboard
    try:
        topUsers = db.leaderboard()
        topUsersString = ""
        for count, user in enumerate(topUsers):
            topUsersString += f"**{count+1}.** {await client.fetch_user(user[0])} with **{user[1]}** rep.\n"
        embed = discord.Embed(title='Top users:\n', description=topUsersString, color=EMBED_COLOR)
        await ctx.send(embed=embed)
    except Exception as e:
        logging.error(e)
        print(e)
        embed.title ='Oops, looks like I\'ve lost my marbles.'
        embed.description = 'To the logs!'
        await ctx.send(embed=embed)
        return

@slash.slash(name='mention',
                description="Set your mention flag",
                options=[create_option(
                    name="flag",
                    description="Bool for true / false",
                    option_type=5,
                    required=True)],
                guild_ids=guild_ids)
async def mention(ctx, flag):
    # set mention flag
    embed = discord.Embed(color=EMBED_COLOR)
    try:
        db.setMentionFlag(flag, ctx.author.id)

        embed.title ='Sounds good boss'
        embed.description = f'Mentions set to {flag}'
        await ctx.send(embed=embed)
    except Exception as e:
        print(e)
        logging.error(e)
        embed.title ='Oops, looks like I\'ve lost my marbles.'
        embed.description = 'To the logs!'
        await ctx.send(embed=embed)

@slash.slash(name='addGame',
                description="Add to your favorite list of games",
                options=[create_option(
                    name="game",
                    description="Game Name",
                    option_type=3,
                    required=True)],
                guild_ids=guild_ids)
async def addGame(ctx, game):
    # set mention flag
    embed = discord.Embed(color=EMBED_COLOR)
    try:
        status = db.insertGame(ctx.author.id, game)
        if(status == 0):
            embed.title = f'Added {game} to your favorites!'
        elif(status == 1):
            embed.title = f'That game is already in your favorites!'
        await ctx.send(embed=embed)
    except Exception as e:
        print(e)
        logging.error(e)
        embed.title ='Oops, looks like I\'ve lost my marbles.'
        embed.description = 'To the logs!'
        await ctx.send(embed=embed)

@slash.slash(name='listGames',
                description="List your favorite games",
                options=[create_option(
                    name="user",
                    description="The user you'd like to list games for",
                    option_type=6,
                    required=True)],
                guild_ids=guild_ids)
async def listGames(ctx, user):
    # set mention flag
    embed = discord.Embed(color=EMBED_COLOR)
    try:
        games = db.listGames(user.id)
        descString = "In no particular order:\n"
        if(len(games) !=0 ):
            for count, game in enumerate(games[0]):
                descString += f"{count+1}. {game}\n"
            embed = discord.Embed(title=f'{user}\'s Games', description=descString, color=EMBED_COLOR)
        else:
            embed = discord.Embed(title=f'{user} plays no games!', color=EMBED_COLOR)
        await ctx.send(embed=embed)
    except Exception as e:
        print(e)
        logging.error(e)
        embed.title ='Oops, looks like I\'ve lost my marbles.'
        embed.description = 'To the logs!'
        await ctx.send(embed=embed)

@slash.slash(name='removeGame',
                description="Remove a game from your favorites",
                options=[create_option(
                    name="game",
                    description="Game Name",
                    option_type=3,
                    required=True)],
                guild_ids=guild_ids)
async def removeGame(ctx, game):
    # set mention flag
    embed = discord.Embed(color=EMBED_COLOR)
    try:
        db.removeGame(ctx.author.id, game)
        embed.title = f'Removed {game} from your favorites!'
        await ctx.send(embed=embed)
    except Exception as e:
        print(e)
        logging.error(e)
        embed.title ='Oops, looks like I\'ve lost my marbles.'
        embed.description = 'To the logs!'
        await ctx.send(embed=embed)

@slash.slash(name='help',
                description="See commands and info",
                options=[],
                guild_ids=guild_ids)
async def help(ctx):
    # disp help message
    embed = discord.Embed(color=EMBED_COLOR)
    embed.title = 'So, you wanna know how I work...'
    embed.description = """ Well, I track your reputation across servers. Here is the stuff you should know"""
    embed.add_field(name='Ranks', value=f'There are 3 Ranks, determined by rep. Default, 10+ and 100+ Each Rank has different properties & commands ', inline=True)
    embed.add_field(name='Transactions', value=f'A record is kept every time a curse or thank is used on another user\nDefault can have up to **10** transactions\n10+ can have **50**\n100+ have **unlimited**', inline=True)
    embed.add_field(name='Commands ---------------', value='Well, only the cool ones', inline=False)
    embed.add_field(name='Thank / Curse', value='Thank/Curse a user\nDefault: **±1**\n10+: **±2**\n100+: **±3**\nAfter 10+ rep, you can thank or curse a user once every 4 weeks', inline=True)
    embed.add_field(name='Mention', value='Turns **on** or **off** mentioning. Enabling this will cause reppo to **notify** you when a user Thanks or Curses you.', inline=True)
    embed.add_field(name='VibeCheck', value='Displays info on a user if they are in the Database', inline=True)
    embed.add_field(name='Leaderboard', value='Displays the top **5** users', inline=True)
    await ctx.send(embed=embed)

if __name__ == '__main__':
    if '-d' in sys.argv:
        logLevel = 2
    elif '-v' in sys.argv:
        logLevel = 1
    else:
        logLevel = 0
    dbConfig = {
        'user':os.getenv('DB_USERNAME'),
        'password':os.getenv('DB_PASSWORD'),
        'host':'localhost',
        'port':os.getenv("DB_PORT"),
        'database':'reppo',
        }
    try:
        db = Database(dbConfig, logLevel)
    except Exception as e:
        print(f"ERROR: {e}")
        exit()
    client.run(os.getenv('TOKEN'))
