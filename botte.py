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
def get_token():
    try:
        file=open("token.txt","r")
        token=file.read()
        file.close()
        return token
    except:
        print("une erreur est survenue le fichier token.txt n'as pas pus être ouvert")
        input()
        return ""


def conf_op(guild_name: str,mod: str):
    if not(os.path.isdir("./" + guild_name)):
        os.mkdir("./" + guild_name)
    if not(os.path.exists("./" + guild_name + "/server.json")):
        f=open("./" + guild_name + "/server.json","w")
        D={"roles":{},"commands":{},"maxOffset":0}
        json.dump(D,f)
        f.close()
    return open("./" + guild_name + "/server.json",mod)

def conf_load(guild_name: str) -> dict:
    with conf_op(guild_name,"r") as f:
        D=json.load(f)
        f.close()
    return D

def conf_write(guild_name:str,conf:dict):
    with conf_op(guild_name,"w+") as f:
        json.dump(conf,f,sort_keys=True, indent=4)
        f.close()

def get_max_member_tier(member:discord.Member):
    conf_dict=conf_load(member.guild.name)
    role_tier=-math.inf
    for role in member.roles :
        if role.name in conf_dict["roles"].keys():
            role_tier=max((role_tier,int(conf_dict["roles"][role.name])))
    return role_tier

def get_min_menber_tier(member):
    conf_dict=conf_load(member.guild.name)
    role_tier=math.inf
    for role in member.roles :
        if role.name in conf_dict["roles"].keys():
            role_tier=min((role_tier,int(conf_dict["roles"][role.name])))
    return role_tier


#Créeation des commandes:

@bot.command(aliases=["tierSR","tierSetR","tsr","tSR","tiersetrole"],
            description="définit le tier des roles du serveur",
            brief="définit le tier des roles du bot",
            usage="<tier as number> <roles as role.mention list>")
async def tierSetRole(ctx,tier:int):
    C=[]
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
async def tierSetCommand(ctx,tier: int,*,command:str):
    C=[]
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

@bot.command(aliases=["sdt","setDefaultT","defaultT","defaultTier"],
            description="définit le tier par défault des commandes",
            brief="définit le tier par défault des commandes",
            usage="<tier as number>")
async def setDefaultTier(ctx,tier):
    try:
        int(tier)
    except:
        await ctx.send("commande invalide taper bot!help pour voir les commandes")
        return
    conf_dict=conf_load(ctx.guild.name)
    for cmd in bot.commands:
        if not(cmd.name in conf_dict["commands"].keys()):
            conf_dict["commands"][cmd.name]=tier
    conf_write(ctx.guild.name,conf_dict)
    await ctx.send("tier par default des commande définit a: {}\n les configue existance n'on pas été écraser".format(tier))

@bot.command(aliases=["lien"],
            description="renvoie un lien définit par setLink",
            brief="renvoie un lien définit par setLink",
            usage="")
async def link(ctx):
    conf_dict=conf_load(ctx.guild.name)
    if "link" in conf_dict.keys():
        await ctx.send(conf_dict["link"])
    else:
        await ctx.send("aucun lien n'as été définit :/")

@bot.command(aliases=["sl","setL","setLien"],
            description="définit le lien de la commande link, un message peut être ajouter",
            brief="définit le lien pour link",
            usage="<link as string>")
async def setLink(ctx,*,link):
    conf_dict=conf_load(ctx.guild.name)
    conf_dict["link"]=link
    conf_write(ctx.guild.name,conf_dict)
    await ctx.send("lien sauvegarder :)")

@bot.command(aliases=["vtf","hset","hiérach","h"],
            description="définit l'écart max de tier entre une personne mentionnant et le mentioner" + \
            "\nexpl:si définit a 1 alors si tier 1 mentione tier2 ok si tier 1 mentionne tier 3 pasok" + \
            "\nvaleur négative ou 0 pour désactiver la fonction",
            brief="définit l'écart max de mentionnement autoriser",
            usage="<offset as number>")
async def hiérarchie(ctx,offset: int):
    conf_dict = conf_load(ctx.guild.name)
    conf_dict["maxOffset"]=offset or 0
    await ctx.send("Offset définit a {}".format(offset))

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
    elif isinstance(error,commands.BadArgument):
        await ctx.send("argument invalide taper bot!help {} pour voir le type des argument".format(ctx.command))
        return
    print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
    traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

@bot.event
async def on_member_join(member):
    conf_dict=conf_load(member.guild.name)
    if "defaltRank" in conf_dict:
        for role in conf_dict["defaltRank"] :
            await member.add_roles(discord.utils.get(member.guild.roles,name=role))
    
@bot.check
async def checkTier(ctx):
    conf_dict=conf_load(ctx.guild.name)
    if(ctx.message.author.guild_permissions.administrator):
        return True
    elif ctx.command.name in conf_dict["commands"].keys():
        if get_max_member_tier(ctx.message.author)>=int(conf_dict["commands"][ctx.command.name]):
            return True
        else:
            return False
    else:
        return False

@bot.event
async def on_message(message):
    await bot.process_commands(message)
    conf_dict=conf_load(message.guild.name)
    if not(message.author.guild_permissions.administrator) and int(conf_dict["maxOffset"])!=0 and (len(message.mentions)>=0 or len(message.role_mentions)>=0):
        author_tier=get_max_member_tier(message.author)
        test=True
        if len(message.mentions)>=0:
            for member in message.mention:
                if author_tier < get_min_menber_tier(member):
                    test=False
        if len(message.role_mention)>=0:
            for role in message.role_mention:
                if role.name in conf_dict["roles"].key():
                    if author_tier<int(conf_dict["roles"][role.name]):
                        test=False
    if not(test):
        message.delete

        
        
        


@bot.event
async def on_ready():
    print("bot pret a botter des gens !")

bot.run(get_token())
input()