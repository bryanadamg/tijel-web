import os
import discord
import requests
from discord.ext import commands
from discord.utils import get
import json
from utils.discord_tool import MeenaBot

chatbot = MeenaBot('discord-msgs')

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

# client = discord.Client()
# bot = discord.Client()
advice_url = 'https://api.adviceslip.com/advice'
horoscope_url = 'https://aztro.sameerkumar.website/'

@bot.event
async def on_ready():
  print(f"logged in as {bot.user}")


@bot.command()
async def horoscope(ctx, arg):
    sign = str(arg)
    params = (('sign', sign),('day', 'today'))
    horoscope = requests.post("https://aztro.sameerkumar.website/?sign="+sign+"&day=today")
    print(horoscope)
    try:
      await ctx.channel.send(horoscope.json()["message"][:10])
    except:
      msg_str = horoscope.json()["description"]
      msg_str += '\n\n' + 'Mood: ' + horoscope.json()["mood"]
      msg_str += ', Compatibility: ' + horoscope.json()["compatibility"]
      msg_str += '\n' + 'Lucky Number: ' + horoscope.json()["lucky_number"]
      msg_str += ', Lucky Time: ' + horoscope.json()["lucky_time"]
      await ctx.channel.send(msg_str)

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