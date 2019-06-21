import discord
from discord.ext import tasks, commands
from discord.ext.commands import Bot
import asyncio
import os
import json
import math
bot=commands.Bot(command_prefix="bot!")

#Définition des fonctions:

def conf_op(guild_name: str,mod: str):
    if not(os.path.isdir("./" + guild_name)):
        os.mkdir("./" + guild_name)
    if not(os.path.exists("./" + guild_name + "/server.json")):
        f=open("./" + guild_name + "/server.json","w")
        D={"roles":{},"commands":{}}
        json.dump(D,f)
        f.close()
    return open("./" + guild_name + "/server.json",mod)

@bot.command(aliases=["tierSR","tierSetR","tsr","tSR","tiersetrole"])
async def tierSetRole(ctx,tier):
    C=[]
    try:
        int(tier)
    except:
        await ctx.send("usage de la commande: bot!tierSetRole (int)tier @role @role  ... ")
        return
    
    if len(ctx.message.role_mentions)==0:
        await ctx.send("usage de la commande: bot!tierSetRole (int)tier @role @role  ... \nle rôle doit pouvoir être mentioner")
    else:
        with conf_op(ctx.guild.name,"r") as f:
            j_dict=json.load(f)
            f.close()
        
        for role in ctx.message.role_mentions :
            name=role.name
            C.append(name)
            j_dict["roles"][name]=tier

        with conf_op(ctx.guild.name,"w+") as f:
            json.dump(j_dict,f,sort_keys=True, indent=4)

        await ctx.send('le tier {} est associer au rôle(s): {}'.format(tier,' , '.join(C)))
        
@bot.command()
async def  tierSetCommand(ctx,tier):
    C=[]
    try:
        int(tier)
    except:
        await ctx.send("usage de la commande: bot!tierSetCommand (int)tier cmnd cmd la commande ne doit pas contenir le préfix du bot les allias ne sont pas suporter")
        return
    else:
        with conf_op(ctx.guild.name,"r") as f:
            j_dict=json.load(f)
            f.close()
        
        for cmd in bot.commands :
            if cmd.name in ctx.message.content.replace("bot!" + ctx.invoked_with,"",1) :
                C.append(cmd.name)
                j_dict["commands"][cmd.name]=tier

        with conf_op(ctx.guild.name,"w+") as f:
            json.dump(j_dict,f,sort_keys=True, indent=4)

        await ctx.send('le tier {} est associer aux command(s): {}'.format(tier,' , '.join(C)))


@bot.event
async def on_message(message):
    await bot.process_commands(message)



@bot.event
async def on_ready():
    print("My body is ready !")



bot.run("NTkwNDkxMDI3NjMxMTEyMjAy.XQ0Ccg.Y5no6DPgNboqWF7jQLvvxnQSlJA")

