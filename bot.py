# bot.py
import os
from random import randint
import random
import asyncio
import discord
import requests
from dotenv import load_dotenv
from discord.ext import commands

# Bot login stuff
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

# Setting up the bot commands
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!',intents=intents)

# Bot Login message on shell
@bot.event
async def on_ready():
    for guild in bot.guilds:
        if guild.name == GUILD:
            break
    print(
        f'{bot.user.name} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
   
    )
    
# Veep Quotes random generator ** Figure out how to make a veep quote list to pull from**

@bot.command (name='veep', help='Responds with a random Veep quote')
async def veep(ctx):
    veep_quotes = [
        'And you know why? Because they\'re ignorant and they\'re dumb as s**t. And that, ladies and gentlemen, is democracy.',
        'I\'ve got to get out of here before I set fire to one of these nerds.'
    ]
    response = random.choice(veep_quotes)
    await ctx.send(response)
# Weather Bot
@bot.command(name='weather', help='current weather, format as !weather city, state')
async def weather(ctx, *, location):
    try:
        # Split input into city and state
        city, state = map(str.strip, location.split(','))

        # Format city and state for the API request
        formatted_location = f'{city},{state}'

        api_key = '{api_key}'
        url = f'https://api.weatherapi.com/v1/current.json?key={api_key}&q={formatted_location}&aqi=no'
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()

            # Extract city, region, and country information
            city = data['location']['name']
            region = data['location'].get('region', '')  # Get region if available, otherwise empty string
            country = data['location']['country']

            # Extract temperature and weather condition description
            temp = data['current']['temp_f']
            desc = data['current']['condition']['text']

            # Send weather information including city, region, and country
            weather_info = f'Weather in {city}, {region}, {country}:' if region else f'Weather in {city}, {country}:'
            await ctx.send(weather_info)
            await ctx.send(f'Temperature: {temp} F')
            await ctx.send(f'Description: {desc}')
        else:
            await ctx.send('Error fetching weather data')
    except Exception as e:
        print(e)
        await ctx.send('An error occurred while fetching weather data.')

# Roll the Dice
# Determines if a message is owned by the bot
def is_me(m):
    return m.author == bot.user

# Determines if the value can be converted to an integer
# Parameters: s - input string
# Returns: boolean. True if can be converted, False if it throws an error.
def is_num(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

@bot.command(name='roll_dice', help='Simulates rolling dice.')
async def roll_basic(a, b, modifier, threshold):
    results = ""
    base = randint(int(a), int(b))
    if (base + modifier) >= threshold:
        if modifier != 0:
            if modifier > 0:
                results += "***Success***: {}+{} [{}] meets or beats the {} threshold.".format(base, modifier, (base + modifier), threshold)
            else:
                results += "***Success***: {}{} [{}] does not meet the {} threshold.".format(base, modifier, (base + modifier), threshold)
        else:
            results += "***Success***: {}".format(base)
    else:
        if modifier != 0:
            if modifier > 0:
                results += "***Failure***: {}+{} [{}]".format(base, modifier, (base + modifier))
            else:
                results += "***Failure***: {}{} [{}]".format(base, modifier, (base + modifier))
        else:
            results += "***Failure***: {}".format(base)
    return results

# Rolls a set of die and returns either number of hits or the total amount
# Parameters: num_of_dice [Number of dice to roll], dice_type[die type (e.g. d8, d6), 
# hit [number that must be exceeded to count as a success], modifier [amount to add to/subtract from total],
# threshold [number of successes needed to be a win]
# Returns: String with results 
def roll_hit(num_of_dice, dice_type, hit, modifier, threshold):
    results = ""
    total = 0
    for x in range(0, int(num_of_dice)):
        y = randint(1, int(dice_type))
        if (int(hit) > 0):
            if (y >= int(hit)):
                results += "**{}** ".format(y)
                total += 1
            else:
                results += "{} ".format(y)
        else:
            results += "{} ".format(y)
            total += y
    total += int(modifier)
    if modifier != 0:
        if modifier > 0:
            results += "+{} = {}".format(modifier, total)
        else:
            results += "{} = {}".format(modifier, total)
    else:
        results += "= {}".format(total)
    if threshold != 0:
        if total >= threshold:
            results += " meets or beats the {} threshold. ***Success***".format(threshold)
        else:
            results += " does not meet the {} threshold. ***Failure***".format(threshold)
    return results

# Parse !roll verbiage
@bot.command(pass_context=True,description='Rolls dice.\nExamples:\n100  Rolls 1-100.\n50-100  Rolls 50-100.\n3d6  Rolls 3 d6 dice and returns total.\nModifiers:\n! Hit success. 3d6!5 Counts number of rolls that are greater than 5.\nmod: Modifier. 3d6mod3 or 3d6mod-3. Adds 3 to the result.\n> Threshold. 100>30 returns success if roll is greater than or equal to 30.\n\nFormatting:\nMust be done in order.\nSingle die roll: 1-100mod2>30\nMultiple: 5d6!4mod-2>2')
async def roll(ctx, roll : str):
    a, b, modifier, hit, num_of_dice, threshold, dice_type = 0, 0, 0, 0, 0, 0, 0
    # author: Writer of discord message
    author = ctx.message.author
    if (roll.find('>') != -1):
        roll, threshold = roll.split('>')
    if (roll.find('mod') != -1):
        roll, modifier = roll.split('mod')
    if (roll.find('!') != -1):
        roll, hit = roll.split('!')
    if (roll.find('d') != -1):
        num_of_dice, dice_type = roll.split('d')
    elif (roll.find('-') != -1):
        a, b = roll.split('-')
    else:
        a = 1
        b = roll
    #Validate data
    try:
        if (modifier != 0):
            if (is_num(modifier) is False):
                raise ValueError("Modifier value format error. Proper usage 1d4+1")
                return
            else:
                modifier = int(modifier)
        if (hit != 0):
            if (is_num(hit) is False):
                raise ValueError("Hit value format error. Proper usage 3d6!5")
                return
            else:
                hit = int(hit)
        if (num_of_dice != 0):
            if (is_num(num_of_dice) is False):
                raise ValueError("Number of dice format error. Proper usage 3d6")
                return
            else:
                num_of_dice = int(num_of_dice)
        if (num_of_dice > 200):
            raise ValueError("Too many dice. Please limit to 200 or less.")
            return
        if (dice_type != 0):
            if (is_num(dice_type) is False):
                raise ValueError("Dice type format error. Proper usage 3d6")
                return
            else:
                dice_type = int(dice_type)
        if (a != 0):
            if (is_num(a) is False):
                raise ValueError("Error: Minimum must be a number. Proper usage 1-50.")
                return
            else:
                a = int(a)
        if (b != 0):
            if (is_num(b) is False):
                raise ValueError("Error: Maximum must be a number. Proper usage 1-50 or 50.")
                return
            else:
                b = int(b)
        if (threshold != 0):
            if (is_num(threshold) is False):
                raise ValueError("Error: Threshold must be a number. Proper usage 1-100>30")
                return
            else:
                threshold = int(threshold)
        if (dice_type != 0 and hit != 0):
            if (hit > dice_type):
                raise ValueError("Error: Hit value cannot be greater than dice type")
                return
            elif (dice_type < 0):
                raise ValueError("Dice type cannot be a negative number.")
                return
            elif (num_of_dice < 0):
                raise ValueError("Number of dice cannot be a negative number.")
                return
        if a != 0 and b != 0:
            await ctx.send("{} rolls {}-{}. Result: {}".format(author, a, b, roll_basic(a, b, modifier, threshold)))
        else:
            await ctx.send("{} rolls {}d{}. Results: {}".format(author, num_of_dice, dice_type, roll_hit(num_of_dice, dice_type, hit, modifier, threshold)))
    except ValueError as err:
        # Display error message to channel
        await ctx.send(err)

#Bot command to delete all messages the bot has made.        
@bot.command(pass_context=True,description='Deletes all messages the bot has made')
async def purge(ctx):
    channel = ctx.message.channel
    deleted = await bot.purge_from(channel, limit=100, check=is_me)
    await bot.send_message(channel, 'Deleted {} message(s)'.format(len(deleted)))

# Don't touch this. Keep it at the end.
bot.run(TOKEN)
