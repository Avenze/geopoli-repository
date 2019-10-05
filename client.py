import discord
from discord.ext import commands
import os
import random
import json
from auth import token
from imports.format import titleCase, setISO, numbered
from imports.api import wiki
from imports.api.exch import getExchangeRatesUSD, getExchangeRatesEUR

bot = commands.Bot(command_prefix='.')

def idToName(ctx, iden):
    for member in ctx.guild.members:
        if member.id == iden:
            return member.display_name
    return iden+' [BOT]'

def valExists(ctx, atr, val):
    if os.path.exists('game/data'+str(ctx.guild.id)+'.json'):
        with open('game/data'+str(ctx.guild.id)+'.json', 'r') as f:
            data = json.load(f)
            for n in data['nations']:
                if atr in n and type(n[atr]) == list and val in n[atr]:
                    return True
                elif atr in n and val == n[atr]:
                    return True
    return False

@bot.command()
async def dawn(ctx):
    if not os.path.exists('game/data'+str(ctx.guild.id)+'.json'):
        data = {}
        data['nations'] = []
        with open('data/botnations.json', 'r') as f:
            botnations = json.load(f)
            data['nations'] += botnations['botnations']
            f = open('game/isolog'+str(ctx.guild.id)+'.txt', 'a')
            for bn in botnations['botnations']:
                f.write(bn['iso']+'\n')
            f.close()
            with open('game/data'+str(ctx.guild.id)+'.json', 'w') as f:
                json.dump(data, f, indent=4)
        userdata = {}
        userdata['users'] = []
        for member in ctx.guild.members:
            userdata['users'].append({'id':member.id,'balance':{
            'USD':10000, 'EUR':0, 'CNY':0, 'RUB':0, 'MXN':0, 'TRY':0, 'INR':0, 'GBP':0, 
            'KRW':0, 'BRL':0, 'ZAR':0, 'AUD':0, 'JPY':0, 'CAD':0, 'IDR':0
        }})
        with open('game/users'+str(ctx.guild.id)+'.json', 'w') as f:
            json.dump(userdata, f, indent=4)
        await ctx.send('The dawn of civilization in '+ctx.guild.name+' has begun...')
        embed = discord.Embed(title="GEOPOLI", description="The Geopolitical Simulation Bot", color=0xeee657)
        embed.add_field(name=".help", value="Gets a full list of command instructions", inline=False)

        await ctx.send(embed=embed)
    else:
        await ctx.send('Civilization has already dawned in '+ctx.guild.name+'.')
            
@bot.command()
async def establish(ctx, nation:str):
    if os.path.exists('game/data'+str(ctx.guild.id)+'.json'):
        if not valExists(ctx, 'name', titleCase(nation)):
            if not valExists(ctx, 'members', ctx.message.author.id):
                currISO = [line.rstrip('\n') for line in open('game/isolog'+str(ctx.guild.id)+'.txt')]
                iso = setISO(nation, currISO)
                city = titleCase(nation)+random.choice([' City', 'shire', ' Town', 'berg', 'borough', 'grad',
                                                                   'jing', 'kyo', 'ville', 'field', 'view', 'town', 'fast'])
                bank = 'Bank of '+titleCase(nation)
                if ctx.message.author.bot:
                    hos = ctx.message.author.display_name
                else:
                    hos = ctx.message.author.id
                try:
                    with open('game/data'+str(ctx.guild.id)+'.json', 'r') as f:
                        data = json.load(f)
                        data['nations'].append({
                            'name':titleCase(nation),
                            'iso':iso,
                            'hos':hos,
                            'members':[ctx.message.author.id],
                            'cap':city,
                            'cities':[city],
                            'bank':bank
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
                            'cities':[city],
                            'bank':bank
                            })
                f = open('game/isolog'+str(ctx.guild.id)+'.txt', 'a')
                f.write(iso+'\n')
                f.close()
                os.remove('game/data'+str(ctx.guild.id)+'.json')
                with open('game/data'+str(ctx.guild.id)+'.json', 'w') as f:
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
    if os.path.exists('game/data'+str(ctx.guild.id)+'.json'):
        if valExists(ctx, 'name', titleCase(nation)):
            if not valExists(ctx, 'members', ctx.message.author.id):
                with open('game/data'+str(ctx.guild.id)+'.json', 'r') as f:
                    data = json.load(f)
                    for n in data['nations']:
                        if n['name'] == titleCase(nation):
                            n['members'].append(ctx.message.author.id)
                os.remove('game/data'+str(ctx.guild.id)+'.json')
                with open('game/data'+str(ctx.guild.id)+'.json', 'w') as f:
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
    if os.path.exists('game/data'+str(ctx.guild.id)+'.json'):
        if valExists(ctx, 'name', titleCase(nation)):
            if valExists(ctx, 'members', ctx.message.author.id):
                with open('game/data'+str(ctx.guild.id)+'.json', 'r') as f:
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
                os.remove('game/data'+str(ctx.guild.id)+'.json')
                with open('game/data'+str(ctx.guild.id)+'.json', 'w') as f:
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
    if os.path.exists('game/data'+str(ctx.guild.id)+'.json'):
        try:
            
            with open('game/data'+str(ctx.guild.id)+'.json', 'r') as f:
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
    if os.path.exists('game/data'+str(ctx.guild.id)+'.json'):
        stage = '```GLOBAL STAGE OF '+ctx.guild.name.upper()+'\n'
        with open('game/data'+str(ctx.guild.id)+'.json', 'r') as f:
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
    if os.path.exists('game/data'+str(ctx.guild.id)+'.json'):
        try:
            stage = '```CITIZENS OF '+nation.upper()+'\n'
            with open('game/data'+str(ctx.guild.id)+'.json', 'r') as f:
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
    if os.path.exists('game/data'+str(ctx.guild.id)+'.json'):
        try:
            stage = '```CITIES OF '+nation.upper()+'\n'
            with open('game/data'+str(ctx.guild.id)+'.json', 'r') as f:
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
    if os.path.exists('game/data'+str(ctx.guild.id)+'.json'):
        if valExists(ctx, 'name', titleCase(nation)):
            if item == 'description':
                with open('game/data'+str(ctx.guild.id)+'.json', 'r') as f:
                    data = json.load(f)
                    for n in data['nations']:
                        if n['name'] == titleCase(nation) and n['hos'] == ctx.message.author.id:
                            n['descrip'] = content
                            f.close()
                            os.remove('game/data'+str(ctx.guild.id)+'.json')
                            with open('game/data'+str(ctx.guild.id)+'.json', 'w') as f:
                                json.dump(data, f, indent=4)
                            await ctx.send(ctx.message.author.display_name+' changed the national desription.')
                            return
                await ctx.send(ctx.message.author.display_name+'! You are not the Head of State of that nation.')
            elif item == 'iso':
                currISO = [line.rstrip('\n') for line in open('game/isolog'+str(ctx.guild.id)+'.txt')]
                with open('game/data'+str(ctx.guild.id)+'.json', 'r') as f:
                    data = json.load(f)
                    for n in data['nations']:
                        if n['name'] == titleCase(nation) and n['hos'] == ctx.message.author.id:
                            if content not in currISO:
                                if (len(content) == 2 or len(content) == 3) and content.isalpha() and content == content.upper():
                                    n['iso'] = content
                                    f.close()
                                    f = open('game/isolog'+str(ctx.guild.id)+'.txt', 'a')
                                    f.write(content+'\n')
                                    f.close()
                                    os.remove('game/data'+str(ctx.guild.id)+'.json')
                                    with open('game/data'+str(ctx.guild.id)+'.json', 'w') as f:
                                        json.dump(data, f, indent=4)
                                    await ctx.send(ctx.message.author.display_name+' changed the ISO code.')
                                else:
                                    await ctx.send(ctx.message.author.display_name+'! That is an incorrect ISO code format. ISO codes must be 2 to 3 uppercase Latin letters.')
                            else:
                                await ctx.send(ctx.message.author.display_name+'! That ISO code already exists.')
                            return
                await ctx.send(ctx.message.author.display_name+'! You are not the Head of State of that nation.')
            elif item == 'capital':
                with open('game/data'+str(ctx.guild.id)+'.json', 'r') as f:
                    data = json.load(f)
                    for n in data['nations']:
                        if n['name'] == titleCase(nation) and n['hos'] == ctx.message.author.id and titleCase(content) in n['cities']:
                            n['cap'] = titleCase(content)
                            f.close()
                            os.remove('game/data'+str(ctx.guild.id)+'.json')
                            with open('game/data'+str(ctx.guild.id)+'.json', 'w') as f:
                                json.dump(data, f, indent=4)
                            await ctx.send(ctx.message.author.display_name+' changed the capital city.')
                            return
                await ctx.send(ctx.message.author.display_name+'! You are not the Head of State of that nation.')
            elif item == 'city':
                with open('game/data'+str(ctx.guild.id)+'.json', 'r') as f:
                    data = json.load(f)
                    for n in data['nations']:
                        if n['name'] == titleCase(nation) and n['hos'] == ctx.message.author.id:
                            if len(n['members'])//3 >= len(n['cities']):
                                if titleCase(content) not in n['city']:
                                    n['city'].append(titleCase(content))
                                    f.close()
                                    os.remove('game/data'+str(ctx.guild.id)+'.json')
                                    with open('game/data'+str(ctx.guild.id)+'.json', 'w') as f:
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
    if os.path.exists('game/data'+str(ctx.guild.id)+'.json'):
        if valExists(ctx, 'members', ctx.message.author.id):
            with open('game/data'+str(ctx.guild.id)+'.json', 'r') as f:
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
    if os.path.exists('game/data'+str(ctx.guild.id)+'.json'):
        try:
            stage = ''
            with open('game/data'+str(ctx.guild.id)+'.json', 'r') as f:
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
    with open('resources/img/geopoli.jpg', 'rb') as picture:
        await ctx.send(file=discord.File(picture, 'geopoli.jpg'))

@bot.command()
async def economy(ctx):
    bases = ['USD', 'N', 'EUR', 'N']
    await ctx.send('WORLD ECONOMY')
    for i in range(4):
        with open('resources/img/rates'+str(i)+'.png', 'rb') as picture:
            if bases[i] == 'N':
                await ctx.send(file=discord.File(picture, bases[i-1]+'.png'))
            else:
                await ctx.send('Currency exchange rates ('+bases[i]+')')
                await ctx.send(file=discord.File(picture, bases[i]+'.png'))

@bot.command()
async def register(ctx):
    if os.path.exists('game/data'+str(ctx.guild.id)+'.json'):
        if valExists(ctx, 'members', ctx.message.author.id):
            with open('game/users'+str(ctx.guild.id)+'.json', 'r') as f:
                data = json.load(f)
                for u in data['users']:
                    if ctx.message.author.id == u['id']:
                        await ctx.send(ctx.message.author.display_name+'! You already have a financial portfolio.') 
                        return
                data['users'].append({'id':ctx.message.author.id,'balance':{
                    'USD':10000, 'EUR':0, 'CNY':0, 'RUB':0, 'MXN':0, 'TRY':0, 'INR':0, 'GBP':0, 
                    'KRW':0, 'BRL':0, 'ZAR':0, 'AUD':0, 'JPY':0, 'CAD':0, 'IDR':0
                }})
                f.close()
                with open('game/users'+str(ctx.guild.id)+'.json', 'w') as f:
                    json.dump(data, f, indent=4)
                await ctx.send(ctx.message.author.display_name+'! You have successfully registered a financial portfolio.')
        else:
            await ctx.send(ctx.message.author.display_name+'! You are currently stateless.')
    else:
        await ctx.send(ctx.message.author.display_name+'! Civilization has yet to be dawned.')

@bot.command()
async def portfolio(ctx):
    if os.path.exists('game/data'+str(ctx.guild.id)+'.json'):
        if valExists(ctx, 'members', ctx.message.author.id):
            with open('game/users'+str(ctx.guild.id)+'.json', 'r') as f:
                data = json.load(f)
                for u in data['users']:
                    if ctx.message.author.id == u['id']:
                        pf = '```'
                        with open('game/data'+str(ctx.guild.id)+'.json', 'r') as nf:
                            nations = json.load(nf)
                            for n in nations['nations']:
                                if ctx.message.author.id in n['members']:
                                    pf += ctx.message.author.display_name.upper()+', '+n['bank'].upper()+'\n'
                        with open('data/dataRecord.json', 'r') as rf:
                            rates = json.load(rf)
                            networth = 0
                            networth_e = 0
                            ratelist = list(u['balance'].keys())
                            listed = []
                            curr_values = []
                            for r in range(len(ratelist)):
                                if ratelist[r] != 'USD':
                                    networth += u['balance'][ratelist[r]]/rates['usd'][len(rates['usd'])-1]['rates'][ratelist[r]]
                                    curr_values.append(u['balance'][ratelist[r]]/rates['usd'][len(rates['usd'])-1]['rates'][ratelist[r]])
                                else:
                                    networth += u['balance'][ratelist[r]]
                                    curr_values.append(u['balance'][ratelist[r]])
                                if ratelist[r] != 'EUR':
                                    networth_e += u['balance'][ratelist[r]]/rates['eur'][len(rates['eur'])-1]['rates'][ratelist[r]]
                                else:
                                    networth_e += u['balance'][ratelist[r]]
                                listed.append(str("%.2f" % u['balance'][ratelist[r]])+' '+ratelist[r])
                            for li in range(len(listed)):
                                if curr_values[li]>0:
                                    pf += listed[li]+' ('+str(int(100*curr_values[li]/networth))+'%)\n'
                            pf += 'Networth (USD): '+str("%.2f" % networth)+'\nNetworth (EUR): '+str("%.2f" % networth_e)+'```'
                        await ctx.send(pf)
                        return
                await ctx.send(ctx.message.author.display_name+'! You do not have a bank account. If you joined this server after this bot was added, you need to use `.register` to open a financial portfolio.') 
        else:
            await ctx.send(ctx.message.author.display_name+'! You are currently stateless.')
    else:
        await ctx.send(ctx.message.author.display_name+'! Civilization has yet to be dawned.')

@bot.command()
async def calc(ctx, src:str, dest:str, amount:float):
    src = src.upper()
    dest = dest.upper()
    if os.path.exists('game/data'+str(ctx.guild.id)+'.json'):
        with open('data/dataRecord.json', 'r') as rf:
            rates = json.load(rf)
            if (src in list(rates['usd'][len(rates['usd'])-1]['rates'].keys()) or src == 'USD') and (dest in list(rates['usd'][len(rates['usd'])-1]['rates'].keys()) or dest == 'USD'):
                if src != 'USD':
                    src_rate = rates['usd'][len(rates['usd'])-1]['rates'][src]
                else:
                    src_rate = 1
                if dest != 'USD':
                    dest_rate = rates['usd'][len(rates['usd'])-1]['rates'][dest] 
                else:
                    dest_rate = 1
                transac = amount/dest_rate * src_rate
            else:
                await ctx.send('Error in processing calculation: one of those currencies is non-existent.')
                return
        await ctx.send(str("%.2f" % amount)+' '+dest+' is '+str("%.2f" % transac)+' '+src+'.')
        return
    else:
        await ctx.send(ctx.message.author.display_name+'! Civilization has yet to be dawned.')

@bot.command()
async def buy(ctx, src:str, dest:str, amount:float):
    src = src.upper()
    dest = dest.upper()
    if os.path.exists('game/data'+str(ctx.guild.id)+'.json'):
        if valExists(ctx, 'members', ctx.message.author.id):
            with open('game/users'+str(ctx.guild.id)+'.json', 'r') as f:
                data = json.load(f)
                transac = 0
                for u in data['users']:
                    if ctx.message.author.id == u['id']:
                        with open('data/dataRecord.json', 'r') as rf:
                            rates = json.load(rf)
                            if src in list(u['balance'].keys()) and dest in list(u['balance'].keys()):
                                total_src = u['balance'][src]
                                if src != 'USD':
                                    src_rate = rates['usd'][len(rates['usd'])-1]['rates'][src]
                                else:
                                    src_rate = 1
                                total_dest = u['balance'][dest]
                                if dest != 'USD':
                                    dest_rate = rates['usd'][len(rates['usd'])-1]['rates'][dest] 
                                else:
                                    dest_rate = 1
                                if total_src >= amount/dest_rate * src_rate:
                                    transac = amount/dest_rate * src_rate
                                    u['balance'][src] -= amount/dest_rate * src_rate
                                    u['balance'][dest] += amount
                                else:
                                    await ctx.send("Sorry "+ctx.message.author.display_name+", you do not have enough "+src+" to make that transaction.")
                                    return
                            else:
                                await ctx.send('Error in processing request: one of those currencies is non-existent.')
                                return
                        f.close()
                        os.remove('game/users'+str(ctx.guild.id)+'.json')
                        with open('game/users'+str(ctx.guild.id)+'.json', 'w') as ff:
                            json.dump(data, ff, indent=4)
                        await ctx.send(ctx.message.author.display_name+'! Transaction success! You exchanged '+str("%.2f" % transac)+' '+src+' for '+str("%.2f" % amount)+' '+dest+'!')
                        return
        else:
            await ctx.send(ctx.message.author.display_name+'! You are currently stateless.') 
    else:
        await ctx.send(ctx.message.author.display_name+'! Civilization has yet to be dawned.')

@bot.command()
async def ping(ctx):
    await ctx.send('pong')

bot.remove_command('help')

@bot.command()
async def help(ctx):
    embed = discord.Embed(title="GEOPOLI", description="The Geopolitical Simulation Bot", color=0xeee657)
    if not os.path.exists('game/data'+str(ctx.guild.id)+'.json'):
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
        embed.add_field(name=".economy", value="Views historical financial information of the current world stage", inline=False)
        embed.add_field(name=".portfolio", value="Views personal financial information", inline=False)
        embed.add_field(name=".buy <desposited-currency> <withdrawn-currency> <amount-withdrawn>", value="Exchanges currency", inline=False)
    await ctx.message.author.send(embed=embed)

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name="with the economy"))
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

bot.run(token)
