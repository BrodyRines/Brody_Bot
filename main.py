import discord                          #Discord wrapper 
from discord.ext import commands
import logging                          #logs content
from dotenv import load_dotenv          #Load environment variable files
import os
import random
import asyncio
import json
import pyjokes
import sqlite3

conn = sqlite3.connect('inventory.db')
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS inventory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    skin TEXT NOT NULL,
    wear TEXT NOT NULL,
    pattern_index INTEGER NOT NULL              
)
               """)
conn.commit()

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

async def float():
    roll = random.uniform(.00, .52)
    if roll <= .07:
        wear = ('Factory New')
    elif roll > .07 and roll < .15:
        wear = ('Minimal Wear')
    elif roll > .15 and roll < .37:
        wear = ('Field Tested')
    elif roll > .37 and roll < .44:
        wear = ('Well Worn')
    else:
        wear = ('Battle Scarred')
    return wear

async def pattern():
    index = random.randint(1, 1001)
    return index

async def open(ctx):
    odds = random.uniform(.01, 100.01)
    if odds <= 79.92:
        skin = random.choice(['MP7 | Skulls', 'AUG | Wings', 'SG 553 | Ultraviolet'])
        await ctx.send(skin)
    elif odds > 79.92 and odds < 96:
        skin = random.choice(['Glock-18 | Dragon Tattoo', 'USP-S | Dark Water', 'M4A1-S | Dark Water'])
        await ctx.send(skin)
    elif odds >= 96 and odds < 99.1:
        skin = random.choice(['AK-47 | Case Hardened', 'Desert Eagle | Hypnotic'])
        await ctx.send(skin)
    elif odds > 99.1 and odds < 99.74:
        skin = random.choice(['AWP | Lightning Strike'])
        await ctx.send(skin)
    else:
        knife = random.choice(["Bayonet", "Flip", "Karambit", "M9 Bayonet", "Gut"])
        finish = random.choice(["Fade", "Marble Fade", "Slaughter", "Case Hardened", "Blue Steel", "Stained", "Doppler", "Tiger Tooth", "Damascus Steel", "Ultraviolet"])
        skin = (f'{knife} | {finish}')
        await ctx.send(skin)
    return skin 

@bot.command()
async def case(ctx):
    i = 0 
    while i < 4:
        await open(ctx)
        await asyncio.sleep(.4 * i)
        i += 1
    if i == 4:
        final_skin = await open(ctx)
        wear = await float()
        pattern_index = await pattern()
        await asyncio.sleep(1)
        await ctx.send(f'You just unboxed: {final_skin} | Wear: {wear} | Pattern Index: {pattern_index}')
        
        user_id = ctx.author.id
        cursor.execute(
            """
            INSERT INTO inventory (user_id, skin, wear, pattern_index)
            VALUES (?, ?, ?, ?) 
            """,
            (user_id, final_skin, wear, pattern_index)
        )
        conn.commit()

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
    

@bot.command()
async def inventory(ctx, member: discord.Member = None):
    target = member or ctx.author
    user_id = target.id
    
    cursor.execute(
        """
        SELECT skin, wear, pattern_index
        FROM inventory
        WHERE user_id = ?
        ORDER BY id DESC
        """,
        (user_id,)
    )
    rows = cursor.fetchall()

    if not rows:
        await ctx.send(f'{target.display_name} has no items yet.')
        return
    
    parts = [
        f'{skin} ({wear}, #{pattern_index})'
        for skin, wear, pattern_index in rows
    ]

    msg = ', '.join(parts)

    if len(msg) > 1900:
        msg = msg[:1900] + ' ...'
    
    await ctx.send(f"{target.display_name}'s inventory: {msg}")



bot.run(token, log_handler=handler, log_level=logging.DEBUG)