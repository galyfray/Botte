import discord
from discord.ext import tasks, commands
from discord.ext.commands import Bot
import asyncio
import os
import json
import math
import traceback
import sys

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

def conf_load(guild_name: str):
    with conf_op(guild_name,"r") as f:
        D=json.load(f)
        f.close()
    return D

def conf_write(guild_name:str,conf:dict):
    with conf_op(guild_name,"w+") as f:
        json.dump(conf,f,sort_keys=True, indent=4)
        f.close()



#Créeation des commandes:

@bot.command(aliases=["tierSR","tierSetR","tsr","tSR","tiersetrole"],
            description="définit le tier des roles du serveur",
            brief="définit le tier des roles du bot",
            usage="<tier as number> <roles as role.mention list>")
async def tierSetRole(ctx,tier):
    C=[]
    try:
        int(tier)
    except:
        await ctx.send("commande invalide taper bot!help")
        return
    
    if len(ctx.message.role_mentions)==0:
        await ctx.send("commande invalide taper bot!help\nle rôle doit pouvoir être mentioner")
    else:
        conf_dict=conf_load(ctx.guild.name)
        
        for role in ctx.message.role_mentions :
            name=role.name
            C.append(name)
            conf_dict["roles"][name]=tier

        conf_write(ctx.guild.name,conf_dict)

        await ctx.send('le tier {} est associer au rôle(s): {}'.format(tier,' , '.join(C)))
        
@bot.command(aliases=["tierSC","tierSetC","tsc","tSC","tiersetcommand"],
            description="définit le tier des comamndes du bot",
            brief="définit le tier des comamndes du bot",
            usage="<tier as number> <commands as string list>")
async def tierSetCommand(ctx,tier,*,command):
    C=[]
    try:
        int(tier)
    except:
        await ctx.send("commande invalide taper bot!help")
        return
    else:
        conf_dict=conf_load(ctx.guild.name)
        
        for cmd in bot.commands :
            if cmd.name in command :
                C.append(cmd.name)
                conf_dict["commands"][cmd.name]=tier

        conf_write(ctx.guild.name,conf_dict)

        await ctx.send('le tier {} est associer aux command(s): {}'.format(tier,' , '.join(C)))

@bot.command(aliases=["sdr","setDefaultR","defaulRank","defaultR"],
            description="définit le role par défaut attribuer au utilisateur qui rejoingne le server",
            brief="définit le role par défaut",
            usage="<role as role.mention>")
async def setDefaultRank(ctx):
    if len(ctx.message.role_mentions)==0:
        await ctx.send("usage incorrecte taper bot!help pour voir la sintaxe\nle role doit pouvoir être mentioner")
    else:
        conf_dict=conf_load(ctx.guild.name)
        C=[]
        for role in ctx.message.role_mentions:
            C.append(role.name)
        conf_dict["defaltRank"]=C
        conf_write(ctx.guild.name,conf_dict)
        await ctx.send("roles par défault :{}".format(' , '.join(C)))

#Event du bot

@bot.event
async def on_command_error(ctx,error):

    if hasattr(ctx.command, 'on_error'):
            return
    elif isinstance(error,commands.CheckFailure) :
        await ctx.send("vous n'avez pas les doits pour effectuer cette commande")
        return
    elif isinstance(error,commands.CommandNotFound):
        await ctx.send("commande inexistante taper bot!help pour voir la liste des commandes")
        return
    print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
    traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

@bot.event
async def on_member_join(member):
    conf_dict=conf_load(member.guild.name)
    if "defaltRank" in conf_dict:
        for role in conf_dict["defaltRank"] :
            member.add_roles(discord.utils.get(member.guild.roles,name=role))
    
@bot.check
async def checkTier(ctx):
    conf_dict=conf_load(ctx.guild.name)
    if(ctx.message.author.guild_permissions.administrator):
        return True
    elif ctx.command.name in conf_dict["commands"].keys():
        test=False
        for role in ctx.message.author.roles :
            if role.name in conf_dict["roles"].keys():
                if int(conf_dict["roles"][role.name])>=int(conf_dict["commands"][ctx.command.name]):
                    test = True 
        return test
    else:
        return False

@bot.event
async def on_message(message):
    await bot.process_commands(message)

@bot.event
async def on_ready():
    print("bot pret a botter des gens !")

bot.run("NTkwNDkxMDI3NjMxMTEyMjAy.XQ0Ccg.Y5no6DPgNboqWF7jQLvvxnQSlJA")