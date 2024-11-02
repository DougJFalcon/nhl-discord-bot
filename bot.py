import discord
from discord.ext import commands
import asyncpg
import asyncio
import os
import re
from dotenv import load_dotenv
from teams import teams

# reads private bot token and postgresql connection details from env
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
DB_HOST = os.getenv("DB_HOST")

# Intents allow bot to monitor the contents of messages
intents = discord.Intents.default()
intents.message_content = True

# Create a connection to discord by instatiating Client
client = discord.Client(intents=intents)

# Create a bot
bot = commands.Bot(
    command_prefix="/",
    intents=intents,
    description="A bot for getting live notifcations for NHL games.",
)


# Function to connect to postgres db
async def init_db():
    print("Attempting to connect to DB...")
    try:
        bot.db = await asyncpg.create_pool(
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            host=DB_HOST,
            timeout=30,
        )
        print("------")
        print("Connected to DB")
        print("------")
    except asyncio.TimeoutError:
        print("------")
        print("Database connection attempt timed out.")
        print("------")
    except Exception as e:
        print("------")
        print(f"Exception occurred: {e}")
        print("------")


# Initialize the database connection when the bot connects
@bot.event
async def on_connect():
    await init_db()


@bot.event
async def on_ready():
    print("------")
    print(f"Logged into Discord as {bot.user} (ID: {bot.user.id})")
    print("------")

    # db_request = await bot.db.fetch("SELECT * FROM public.discordguilds WHERE followedteam='Pittsburgh Pirates'")
    # print(db_request[0]['guild_id'])


# ADD DB ENTRY WHEN BOT JOINS AND DELETE DB ENTRY WHEN BOT LEAVES GUILD
# function to execute query that inserts guild id into DB
async def add_guild_to_db(guild_id):
    async with bot.db.acquire() as connection:
        try:
            await connection.execute(
                "INSERT INTO discordguilds (guild_id) VALUES ($1)", guild_id
            )
            print("------")
            print(f"Guild ID {guild_id} added to DB.")
            print("------")
        except asyncio.TimeoutError:
            print("------")
            print("Could not write to DB, connection attempt timed out.")
            print("------")
        except Exception as e:
            print("------")
            print(f"Exception occured: {e}")
            print("------")


# function to execute query that removes guild entry from DB
async def remove_guild_from_db(guild_id):
    async with bot.db.acquire() as connection:
        try:
            await connection.execute(
                "DELETE FROM discordguilds WHERE guild_id = $1", guild_id
            )
            print("------")
            print(f"Guild ID {guild_id} removed from DB.")
            print("------")
        except asyncio.TimeoutError:
            print("------")
            print("Could not write to DB, connection attempt timed out.")
            print("------")
        except Exception as e:
            print("------")
            print(f"Exception occured: {e}")
            print("------")


# Bot event that listens for guild join event and calls add_guild_to_db() fucntion
@bot.event
async def on_guild_join(guild):
    await add_guild_to_db(str(guild.id))
    print("------")
    print(f"Bot has joined the guild: {guild.name} (ID: {guild.id})")
    print("------")


# Removes DB entry for guild when bot is removed from guild
@bot.event
async def on_guild_remove(guild):
    await remove_guild_from_db(str(guild.id))
    print("------")
    print(f"Bot has left the guild: {guild.name} (ID: {guild.id})")
    print("------")


# FOLLOW A TEAM
@bot.command()
async def follow(ctx, *, arg):
    if arg.title() not in teams:
        await ctx.send(f"{arg}")
        await ctx.send("uh oh stinky")
        await ctx.send("Team not found.")
    else:
        # need to write a helper function that handles db connections and exceptions YEP
        async with bot.db.acquire() as connection:
            try:
                await connection.execute(
                    "DELETE FROM discordguilds WHERE guild_id = $1", guild_id
                )
            except asyncio.TimeoutError:
                print("------")
                print("Could not write to DB, connection attempt timed out.")
                print("------")
            except Exception as e:
                print("------")
                print(f"Exception occured: {e}")
                print("------")
        await ctx.send(f"You're now following the {arg.title()}.")


# async def table_does_exist():
#    results = await bot.db.fetch('SELECT * FROM public.discordguilds WHERE followedteam="Pittsburgh Pirates"')
#    print(results)


# Run the bot with secret token
bot.run(BOT_TOKEN)

# TODO:
# check if the database has a table for guild ids and teams, if not create one
# check if the guild/server already has an entry in the database if not create one, else send message in channel that one already exists
# ask user to input a team name
# check if that team name is valid, if not try again, else store the team name and guild id
