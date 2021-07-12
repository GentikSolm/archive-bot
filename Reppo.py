import discord
import os
import sys
import logging
from ReppoDb import OutOfRange, Database

from datetime import datetime
from dotenv import load_dotenv
from discord_slash import SlashCommand # Importing the newly installed library.
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
    embed = discord.Embed(color=EMBED_COLOR)
    if data['receiver'] == data['sender']:
        embed.set_author(name=f'You cant rate yourself bro...')
        await ctx.send(embed=embed)
        return
    context = (ctx.author, user)
    try:
        rep, mention_flag, code = db.thank(data, context)
        if code == 1:
            if mention_flag:
                embed.set_author(name=f'{user.mention} got + {rep} rep!', icon_url=user.avatar_url)
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
    context = (ctx.author, user)
    try:
        rep, mention_flag, code = db.thank(data, context)
        if code == 1:
            if mention_flag:
                embed.set_author(name=f'{user.mention} got - {rep} rep!', icon_url=user.avatar_url)
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
    context = (ctx.author, user)
    try:
        flag, userData, rank = db.vibeCheck(context)
    except Exception as e:
        logging.error(e)
        print(e)
        embed.title ='Oops, looks like I\'ve lost my marbles.'
        embed.description = 'To the logs!'
        await ctx.send(embed=embed)
        return
    embed = discord.Embed(color=EMBED_COLOR)
    if not flag:
        embed.set_author(name=f'{user} has never been given, or had rep taken.', icon_url=user.avatar_url)
        await ctx.send(embed=embed)
    else:
        embed.set_author(name=f'{user} has {userData[0]} rep.', icon_url=user.avatar_url)
        embed.description = f'They are currently Rank **{rank}** on the Leaderboard.'
        await ctx.send(embed=embed)

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
    embed = discord.Embed(color=EMBED_COLOR)
    try:
        db.setrep(data, context, rep)
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
    try:
        topUsers = db.leaderboard()
    except Exception as e:
        logging.error(e)
        print(e)
        embed.title ='Oops, looks like I\'ve lost my marbles.'
        embed.description = 'To the logs!'
        await ctx.send(embed=embed)
        return
    topUsersString = ""
    for count, user in enumerate(topUsers):
        topUsersString += f"**{count+1}.** {await client.fetch_user(user[0])} with **{user[1]}** rep.\n"
    embed = discord.Embed(title='Top users:\n', description=topUsersString, color=EMBED_COLOR)
    await ctx.send(embed=embed)

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
    try:
        db = Database(dbConfig, logLevel)
    except Exception as e:
        print(f"ERROR: {e}")
        logging.error(e)
        exit()
    client.run(os.getenv('TOKEN'))
