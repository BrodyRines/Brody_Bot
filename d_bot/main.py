import discord                          #Discord wrapper 
from discord.ext import commands
import logging                          #logs content
from dotenv import load_dotenv          #Load environment variable files
import os
import random
import asyncio
import json
import pyjokes
load_dotenv()
token = os.getenv('DISCORD_TOKEN')

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)     #reference bot in discord server using ! / giving bot permissions 

@bot.event
async def on_ready():                                       #waits for connection via discord API and prints statement 
    print(f'We are ready to go in, {bot.user.name}')        #showing successful connection

@bot.event
async def on_member_join(member):
    await member.send(f'Welcome to the server {member.name}, I hope you enjoy yourself!')   #DM's new members

@bot.command()
async def joke(ctx):
    joke_ = pyjokes.get_joke()
    await ctx.send(joke_)

@bot.command()
async def flip(ctx):
    coin = random.choice(['Heads', 'Tails'])
    await ctx.send(coin)

@bot.command()
async def wwjd(ctx):                            #references randomgame.json file to get call and response 
    with open('randomgame.json', 'r') as rando: #variables need changes on names to avoid confusion but is fine for now
        game = json.load(rando)                 #opens and closes json file, gets random value from list, stores in rando, and prints off
    data = game['games']                        #!wwjd command, asking what we should do if we are bored
    choice = random.choice(data)

    await ctx.send('You should...')
    await asyncio.sleep(2)
    await ctx.send(choice)


@bot.command()
async def rps(ctx, choice):
    if choice not in (['rock', 'paper', 'scissors']):
        await ctx.send('Please choose either rock, paper, or scissors =)')
        return
    
    bot_choice = random.choice(['rock', 'paper', 'scissors'])
    await countdown(ctx)


    if choice == bot_choice:        #references countdown bot event block, and runs game logic for !rps command
        await ctx.send(f'You chose {choice} and I chose {bot_choice}----> It is a Tie!')
        return
    elif (choice == 'rock' and bot_choice == 'scissors') or (choice == 'paper' and bot_choice == 'rock') or (choice == 'scissors' and bot_choice == 'paper'):
        await ctx.send(f'You chose {choice} and I chose {bot_choice}----> You Won!')
    else:
        await ctx.send(f'You chose {choice} and I chose {bot_choice}----> You Lost, ha ha!')
    

@bot.event                                              #Sends the phrase rock,paper,scissors,shoot!, but sends each as a newline
async def countdown(ctx):                               #and in .5 second increments
    words = ['rock', 'paper', 'scissors', 'shoot!!!']
    for word in words:
        await ctx.send(word)
        if word != 'shoot':
            await asyncio.sleep(0.5)
    
    
    




bot.run(token, log_handler=handler, log_level=logging.DEBUG)