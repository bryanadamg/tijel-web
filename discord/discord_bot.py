import os
import discord
import requests
from discord.ext import commands
from discord.utils import get
import json
from chatbot.bot import MeenaBot
from bs4 import BeautifulSoup

chatbot = MeenaBot('discord-msgs')

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

# client = discord.Client()
# bot = discord.Client()
SIGNS = signs = {
    "aries": 1,
    "taurus": 2,
    "gemini": 3,
    "cancer": 4,
    "leo": 5,
    "virgo": 6,
    "libra": 7,
    "scorpio": 8,
    "sagittarius": 9,
    "capricorn": 10,
    "aquarius": 11,
    "pisces": 12,
}

@bot.event
async def on_ready():
  print(f"logged in as {bot.user}")


@bot.command()
async def horoscope(ctx, arg):
    sign = str(arg)
    url = f"https://www.horoscope.com/us/horoscopes/general/horoscope-general-daily-today.aspx?sign={SIGNS[sign]}"
    horoscope = requests.post(url)
    soup = BeautifulSoup(horoscope.text, 'html.parser')
    container = soup.find("p")
    print(container.text.strip())
    try:
      await ctx.channel.send(container.text.strip())
    except:
      await ctx.channel.send("Error")

@bot.command()
async def ask(ctx, *, message=None):
    query = str(message)
    print('!ask command received')
    res = chatbot.ask(query)
    try:
      await ctx.channel.send(res)
    except Exception as e:
      await ctx.channel.send(e)



def embed_leaderboard(dictionary):
  dictionary = dict(sorted(dictionary.items(), key=lambda item: (-item[1][1], item[1][0])))
  embed = discord.Embed(title="__**May Wordle Leaderboard**__",
                        color=0x03f8fc)
  users_string, guesses_string, games_string = '', '', ''
  for user in dictionary:
    users_string += f"{user[:-5]}\n"
    guesses_string += f"{dictionary[user][0]}\n"
    games_string += f"{dictionary[user][1]}\n"
  embed.add_field(name='Name', value=users_string, inline=True)
  embed.add_field(name='Guesses', value=guesses_string,  inline=True)
  embed.add_field(name='Games', value=games_string,  inline=True)
  return embed
  

# client.run(os.environ['TOKEN'])
if os.path.exists('./creds/keys.json'):
    with open('./creds/keys.json') as key:
        creds = json.load(key)
bot.run(creds['discord'])