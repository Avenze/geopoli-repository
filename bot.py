import discord
from discord.ext import commands
import os
import random
import json
from auth import token
from format import titleCase, setISO, numbered
import wiki
from exch import getExchangeRatesUSD, getExchangeRatesEUR

bot = commands.Bot(command_prefix='.')

def idToName(ctx, iden):
    for member in ctx.guild.members:
        if member.id == iden:
            return member.display_name
    return iden+' [BOT]'

def valExists(ctx, atr, val):
    if os.path.exists('data/data'+str(ctx.guild.id)+'.json'):
        with open('data/data'+str(ctx.guild.id)+'.json', 'r') as f:
            data = json.load(f)
            for n in data['nations']:
                if atr in n and type(n[atr]) == list and val in n[atr]:
                    return True
                elif atr in n and val == n[atr]:
                    return True
    return False

@bot.command()
async def dawn(ctx):
    if not os.path.exists('data/data'+str(ctx.guild.id)+'.json'):
        data = {}
        data['nations'] = []
        with open('botnations.json', 'r') as f:
            botnations = json.load(f)
            data['nations'] += botnations['botnations']
            f = open('data/isolog'+str(ctx.guild.id)+'.txt', 'a')
            for bn in botnations['botnations']:
                f.write(bn['iso']+'\n')
            f.close()
            with open('data/data'+str(ctx.guild.id)+'.json', 'w') as f:
                    json.dump(data, f, indent=4)
        await ctx.send('The dawn of civilization in '+ctx.guild.name+' has begun...')
        embed = discord.Embed(title="GEOPOLI", description="The Geopolitical Simulation Bot", color=0xeee657)
        embed.add_field(name=".help", value="Gets a full list of command instructions", inline=False)

        await ctx.send(embed=embed)
    else:
        await ctx.send('Civilization has already dawned in '+ctx.guild.name+'.')
            
@bot.command()
async def establish(ctx, nation:str):
    if os.path.exists('data/data'+str(ctx.guild.id)+'.json'):
        if not valExists(ctx, 'name', titleCase(nation)):
            if not valExists(ctx, 'members', ctx.message.author.id):
                currISO = [line.rstrip('\n') for line in open('data/isolog'+str(ctx.guild.id)+'.txt')]
                iso = setISO(nation, currISO)
                city = titleCase(nation)+random.choice([' City', 'shire', ' Town', 'berg', 'borough', 'grad',
                                                                   'jing', 'kyo', 'ville', 'field', 'view', 'town', 'fast'])
                if ctx.message.author.bot:
                    hos = ctx.message.author.display_name
                else:
                    hos = ctx.message.author.id
                try:
                    with open('data/data'+str(ctx.guild.id)+'.json', 'r') as f:
                        data = json.load(f)
                        data['nations'].append({
                            'name':titleCase(nation),
                            'iso':iso,
                            'hos':hos,
                            'members':[ctx.message.author.id],
                            'cap':city,
                            'cities':[city]
                            })
                except ValueError:
                    data = {}
                    data['nations'] = []
                    data['nations'].append({
                            'name':titleCase(nation),
                            'iso':iso,
                            'hos':hos,
                            'members':[ctx.message.author.id],
                            'cap':city,
                            'cities':[city]
                            })
                f = open('data/isolog'+str(ctx.guild.id)+'.txt', 'a')
                f.write(iso+'\n')
                f.close()
                os.remove('data/data'+str(ctx.guild.id)+'.json')
                with open('data/data'+str(ctx.guild.id)+'.json', 'w') as f:
                    json.dump(data, f, indent=4)
                await ctx.send(ctx.message.author.display_name+' established the growing nation of '+titleCase(nation)+'.')
            else:
                await ctx.send(ctx.message.author.display_name+'! You are already in a nation.')
        else:
            await ctx.send(ctx.message.author.display_name+'! That nation has already been established.')
    else:
        await ctx.send(ctx.message.author.display_name+'! Civilization has yet to be dawned.')

@bot.command()
async def join(ctx, nation:str):
    if os.path.exists('data/data'+str(ctx.guild.id)+'.json'):
        if valExists(ctx, 'name', titleCase(nation)):
            if not valExists(ctx, 'members', ctx.message.author.id):
                with open('data/data'+str(ctx.guild.id)+'.json', 'r') as f:
                    data = json.load(f)
                    for n in data['nations']:
                        if n['name'] == titleCase(nation):
                            n['members'].append(ctx.message.author.id)
                os.remove('data/data'+str(ctx.guild.id)+'.json')
                with open('data/data'+str(ctx.guild.id)+'.json', 'w') as f:
                    json.dump(data, f, indent=4)
                await ctx.send(ctx.message.author.display_name+' joined the nation of '+titleCase(nation)+'.')
            else:
                await ctx.send(ctx.message.author.display_name+'! You are already in a nation.')
        else:
            await ctx.send(ctx.message.author.display_name+'! This nation does not exist.')
    else:
        await ctx.send(ctx.message.author.display_name+'! Civilization has yet to be dawned.')

@bot.command()
async def leave(ctx, nation:str):
    if os.path.exists('data/data'+str(ctx.guild.id)+'.json'):
        if valExists(ctx, 'name', titleCase(nation)):
            if valExists(ctx, 'members', ctx.message.author.id):
                with open('data/data'+str(ctx.guild.id)+'.json', 'r') as f:
                    data = json.load(f)
                    for n in data['nations']:
                        if n['name'] == titleCase(nation):
                            if ctx.message.author.id in n['members']:
                                n['members'].remove(ctx.message.author.id)
                                if n['hos'] == ctx.message.author.id:
                                    if len(n['members'])>=1:
                                        n['hos'] = n['members'][0]
                                        await ctx.send(ctx.message.author.display_name+'! You are the Head of State. You will be preceded by '+idToName(n['members'][0])+'.')
                                    else:
                                        data['nations'].remove(n)
                                        await ctx.send(ctx.message.author.display_name+'! You are the last member of this nation. '+titleCase(nation)+' will be disbanded.')
                            else:
                                await ctx.send(ctx.message.author.display_name+'! You are not a member of that nation.')
                                return
                os.remove('data/data'+str(ctx.guild.id)+'.json')
                with open('data/data'+str(ctx.guild.id)+'.json', 'w') as f:
                    json.dump(data, f, indent=4)
                await ctx.send(ctx.message.author.display_name+' left the nation of '+titleCase(nation)+'.')
            else:
                await ctx.send(ctx.message.author.display_name+'! You are currently stateless.')
        else:
            await ctx.send(ctx.message.author.display_name+'! This nation does not exist.')
    else:
        await ctx.send(ctx.message.author.display_name+'! Civilization has yet to be dawned.')

@bot.command()
async def profile(ctx, nation:str):
    if os.path.exists('data/data'+str(ctx.guild.id)+'.json'):
        try:
            
            with open('data/data'+str(ctx.guild.id)+'.json', 'r') as f:
                data = json.load(f)
                for n in data['nations']:
                    if n['name'] == titleCase(nation):
                        if 'descrip' in n:
                            embed = discord.Embed(title=nation.upper(), description=n['descrip'], color=0xeee657)
                        else:
                            embed = discord.Embed(title=nation.upper(), description=wiki.getSummary(titleCase(nation).replace(' ', '%20')), color=0xeee657)
                        embed.add_field(name="Head of State", value=idToName(ctx, n['hos']), inline=False)
                        embed.add_field(name="Capital City", value=n['cap'], inline=False)
                        embed.add_field(name="ISO Code", value=n['iso'], inline=False)
                        embed.add_field(name="Population", value=str(len(n['members']))+'; use `.citizens "'+titleCase(nation)+'"` to see citizens', inline=False)
                        embed.add_field(name="Cities", value=str(len(n['cities']))+'; use `.cities "'+titleCase(nation)+'"` to see cities', inline=False)
                        await ctx.send(embed=embed)
                        return
            await ctx.send(ctx.message.author.display_name+'! This nation does not exist.') 
        except ValueError:
            await ctx.send(ctx.message.author.display_name+'! This nation does not exist.') 
    else:
        await ctx.send(ctx.message.author.display_name+'! Civilization has yet to be dawned.')

@bot.command()
async def world(ctx):
    if os.path.exists('data/data'+str(ctx.guild.id)+'.json'):
        stage = '```GLOBAL STAGE OF '+ctx.guild.name.upper()+'\n'
        with open('data/data'+str(ctx.guild.id)+'.json', 'r') as f:
            data = json.load(f)
            bots = 0
            sortnations = []
            for n in data['nations']:
                sortnations.append(n['name'])
            sortnations.sort()
            for s in sortnations:
                stage += ' - '+s+'\n'
            stage += '```'
        await ctx.send(stage)
    else:
        await ctx.send(ctx.message.author.display_name+'! Civilization has yet to be dawned.')

@bot.command()
async def citizens(ctx, nation:str):
    if os.path.exists('data/data'+str(ctx.guild.id)+'.json'):
        try:
            stage = '```CITIZENS OF '+nation.upper()+'\n'
            with open('data/data'+str(ctx.guild.id)+'.json', 'r') as f:
                data = json.load(f)
                for n in data['nations']:
                    if n['name'] == titleCase(nation):
                        for mem in n['members']:
                            if str(mem).isdigit:
                                stage += ' - '+idToName(ctx, mem)+'\n'
                            else:
                                stage += ' - '+mem+'\n'
                        stage += '```'
                        await ctx.send(stage)
                        return
            await ctx.send(ctx.message.author.display_name+'! This nation does not exist.') 
        except ValueError:
            await ctx.send(ctx.message.author.display_name+'! This nation does not exist.') 
    else:
        await ctx.send(ctx.message.author.display_name+'! Civilization has yet to be dawned.')

@bot.command()
async def cities(ctx, nation:str):
    if os.path.exists('data/data'+str(ctx.guild.id)+'.json'):
        try:
            stage = '```CITIES OF '+nation.upper()+'\n'
            with open('data/data'+str(ctx.guild.id)+'.json', 'r') as f:
                data = json.load(f)
                for n in data['nations']:
                    if n['name'] == titleCase(nation):
                        for cit in n['cities']:
                            stage += ' - '+cit+'\n'
                        stage += '```'
                        await ctx.send(stage)
                        return
            await ctx.send(ctx.message.author.display_name+'! This nation does not exist.') 
        except ValueError:
            await ctx.send(ctx.message.author.display_name+'! This nation does not exist.') 
    else:
        await ctx.send(ctx.message.author.display_name+'! Civilization has yet to be dawned.')

@bot.command()
async def set(ctx, item:str, nation:str, content:str):
    if os.path.exists('data/data'+str(ctx.guild.id)+'.json'):
        if valExists(ctx, 'name', titleCase(nation)):
            if item == 'description':
                with open('data/data'+str(ctx.guild.id)+'.json', 'r') as f:
                    data = json.load(f)
                    for n in data['nations']:
                        if n['name'] == titleCase(nation) and n['hos'] == ctx.message.author.id:
                            n['descrip'] = content
                            f.close()
                            os.remove('data/data'+str(ctx.guild.id)+'.json')
                            with open('data/data'+str(ctx.guild.id)+'.json', 'w') as f:
                                json.dump(data, f, indent=4)
                            await ctx.send(ctx.message.author.display_name+' changed the national desription.')
                            return
                await ctx.send(ctx.message.author.display_name+'! You are not the Head of State of that nation.')
            elif item == 'iso':
                currISO = [line.rstrip('\n') for line in open('data/isolog'+str(ctx.guild.id)+'.txt')]
                with open('data/data'+str(ctx.guild.id)+'.json', 'r') as f:
                    data = json.load(f)
                    for n in data['nations']:
                        if n['name'] == titleCase(nation) and n['hos'] == ctx.message.author.id:
                            if content not in currISO:
                                if (len(content) == 2 or len(content) == 3) and content.isalpha() and content == content.upper():
                                    n['iso'] = content
                                    f.close()
                                    f = open('data/isolog'+str(ctx.guild.id)+'.txt', 'a')
                                    f.write(content+'\n')
                                    f.close()
                                    os.remove('data/data'+str(ctx.guild.id)+'.json')
                                    with open('data/data'+str(ctx.guild.id)+'.json', 'w') as f:
                                        json.dump(data, f, indent=4)
                                    await ctx.send(ctx.message.author.display_name+' changed the ISO code.')
                                else:
                                    await ctx.send(ctx.message.author.display_name+'! That is an incorrect ISO code format. ISO codes must be 2 to 3 uppercase Latin letters.')
                            else:
                                await ctx.send(ctx.message.author.display_name+'! That ISO code already exists.')
                            return
                await ctx.send(ctx.message.author.display_name+'! You are not the Head of State of that nation.')
            elif item == 'capital':
                with open('data/data'+str(ctx.guild.id)+'.json', 'r') as f:
                    data = json.load(f)
                    for n in data['nations']:
                        if n['name'] == titleCase(nation) and n['hos'] == ctx.message.author.id:
                            n['cap'] = titleCase(content)
                            f.close()
                            os.remove('data/data'+str(ctx.guild.id)+'.json')
                            with open('data/data'+str(ctx.guild.id)+'.json', 'w') as f:
                                json.dump(data, f, indent=4)
                            await ctx.send(ctx.message.author.display_name+' changed the capital city.')
                            return
                await ctx.send(ctx.message.author.display_name+'! You are not the Head of State of that nation.')
            elif item == 'city':
                with open('data/data'+str(ctx.guild.id)+'.json', 'r') as f:
                    data = json.load(f)
                    for n in data['nations']:
                        if n['name'] == titleCase(nation) and n['hos'] == ctx.message.author.id:
                            if len(n['members'])//3 >= len(n['cities']):
                                if titleCase(content) not in n['city']:
                                    n['city'].append(titleCase(content))
                                    f.close()
                                    os.remove('data/data'+str(ctx.guild.id)+'.json')
                                    with open('data/data'+str(ctx.guild.id)+'.json', 'w') as f:
                                        json.dump(data, f, indent=4)
                                    await ctx.send(ctx.message.author.display_name+' added the city of '+titleCase(content)+'.')
                                    return
                                await ctx.send(ctx.message.author.display_name+'! That city already exists.')
                                return
                            await ctx.send(ctx.message.author.display_name+'! You need a population of at least '+str(len(n['cities'])*3)+' to establish another city')
                            return
                await ctx.send(ctx.message.author.display_name+'! You are not the Head of State of that nation.')
                return
        else:
            await ctx.send(ctx.message.author.display_name+'! This nation does not exist.')
    else:
        await ctx.send(ctx.message.author.display_name+'! Civilization has yet to be dawned.')

@bot.command()
async def passport(ctx):
    if os.path.exists('data/data'+str(ctx.guild.id)+'.json'):
        if valExists(ctx, 'members', ctx.message.author.id):
            with open('data/data'+str(ctx.guild.id)+'.json', 'r') as f:
                data = json.load(f)
                for n in data['nations']:
                    if ctx.message.author.id in n['members']:
                        pp = '```\nPASSPORT\n'
                        pp += 'Name: '+idToName(ctx, ctx.message.author.id)+'\n'
                        pp += 'Citizenship: '+n['name']+'\n'
                        if n['hos'] == ctx.message.author.id:
                            pp += 'Rank: Head of State\n'
                        else:
                            pp += 'Rank: Citizen\n'
                        pp += 'You are the '+numbered(n['members'].index(ctx.message.author.id)+1)+' member of '+n['name']+'\n'
                        pp += '```'
                        await ctx.send(pp)
                        return
        else:
            await ctx.send(ctx.message.author.display_name+'! You are currently stateless.') 
    else:
        await ctx.send(ctx.message.author.display_name+'! Civilization has yet to be dawned.')

@bot.command()
async def bank(ctx, nation:str):
    if os.path.exists('data/data'+str(ctx.guild.id)+'.json'):
        try:
            stage = ''
            with open('data/data'+str(ctx.guild.id)+'.json', 'r') as f:
                data = json.load(f)
                for n in data['nations']:
                    if n['name'] == titleCase(nation):
                        stage = '```'+n['bank']+'\n1 USD is '+str(n['usd'])+' '+n['curr']+'.\n1 EUR is '+str(n['eur'])+' '+n['curr']+'```'
                        await ctx.send(stage) 
                        return
            await ctx.send(ctx.message.author.display_name+'! This nation does not exist.') 
        except ValueError:
            await ctx.send(ctx.message.author.display_name+'! This nation does not exist.') 
    else:
        await ctx.send(ctx.message.author.display_name+'! Civilization has yet to be dawned.')

@bot.command()
async def icon(ctx):
    with open('geopoli.jpg', 'rb') as picture:
        await ctx.send(file=discord.File(picture, 'geopoli.jpg'))

@bot.command()
async def ping(ctx):
    await ctx.send('pong')

bot.remove_command('help')

@bot.command()
async def help(ctx):
    embed = discord.Embed(title="GEOPOLI", description="The Geopolitical Simulation Bot", color=0xeee657)
    if not os.path.exists('data/data'+str(ctx.guild.id)+'.json'):
        embed.add_field(name=".dawn", value="Starts the simulation", inline=False)
    else:
        embed = discord.Embed(title="Geopoli", description="The Geopolitical Simulation Bot", color=0xeee657)
        embed.add_field(name=".help", value="Gets a full list of command instructions", inline=False)
        embed.add_field(name=".establish <nation-name>", value="Establishes a new nation", inline=False)
        embed.add_field(name=".join <nation-name>", value="Joins an existing nation", inline=False)
        embed.add_field(name=".leave <nation-name>", value="Leaves current nation", inline=False)
        embed.add_field(name=".world", value="Views the current world stage", inline=False)
        embed.add_field(name=".passport", value="Views your passport", inline=False)
        embed.add_field(name=".profile <nation-name>", value="Displays the profile of a nation", inline=False)
        embed.add_field(name=".citizens <nation-name>", value="Lists the citizens of a nation in chronological order", inline=False)
        embed.add_field(name=".cities <nation-name>", value="Lists the cities of a nation in chronological order", inline=False)
        embed.add_field(name=".set description <nation-name> <description>", value="Change nation description", inline=False)
        embed.add_field(name=".set iso <nation-name> <iso>", value="Change nation ISO code", inline=False)
        embed.add_field(name=".set capital <nation-name> <city>", value="Change nation capital city", inline=False)
        embed.add_field(name=".set city <nation-name> <city>", value="Adds a city to your country", inline=False)
        embed.add_field(name=".bank <nation-name>", value="Views the financial information of a nation", inline=False)
    await ctx.message.author.send(embed=embed)

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name="with peace talks"))
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

bot.run(token)
