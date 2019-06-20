import discord
from discord.ext import tasks, commands
from discord.ext.commands import Bot
import asyncio
import os
import json
bot=commands.Bot(command_prefix="bot!")

#Définition des fonctions:

def I_conf(guildName: str):
    if not(os.path.isdir("./" + guildName)):
        os.mkdir("./" + guildName)
    if not(os.path.exists("./" + guildName + "/server.json")):
        with open("./" + guildName+ "/server.json","w") as f:
            f.write("{ }")
            f.close()
     


@bot.command()
async def tierSet(ctx,tier):
    C=[]
    try:
        int(tier)
    except:
        await ctx.send("usage de la commande: bot!tierSet (int)tier @role @role  ... ")
        return
    
    if len(ctx.message.role_mentions)==0:
        await ctx.send("usage de la commande: bot!tierSet (int)tier @role @role  ... \nle rôle doit pouvoir être mentioner")
    else:
        for r in ctx.message.role_mentions:
            C.append(r.mention)

        I_conf(ctx.guild.name)

        Rconfig= open("./" + ctx.guild.name + "/server.json","r")
        Jconfig=json.load(Rconfig)
        
        Tname="Tier "+tier
        if Tname in Jconfig :
            Jconfig[Tname]=C
        else:
            if "Tier 1" in Jconfig:
                print(Jconfig["Tier 1"])
            Jconfig[Tname]=C
            Rconfig.close()
            Rconfig=open("./" + ctx.guild.name + "/server.json","w+")
            json.dump(Jconfig,Rconfig,indent = 4, sort_keys=True)

        await ctx.send('le tier {} est associer au rôle(s): {}'.format(tier,' , '.join(C)))
        
    


@bot.event
async def on_message(message):
    await bot.process_commands(message)



@bot.event
async def on_ready():
    print("My body is ready !")



bot.run("NTkwNDkxMDI3NjMxMTEyMjAy.XQnYRQ.0U-M5F__kWzklClaUd2wfkjoDJ4")

