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
        D={"roles":{},"commands":{},"maxOffset":0,"newsOffset":{},"welcomeMessage":{"MP":"","server":""}}
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

def get_min_member_tier(member):
    conf_dict=conf_load(member.guild.name)
    role_tier=math.inf
    for role in member.roles :
        if role.name in conf_dict["roles"].keys():
            role_tier=min((role_tier,int(conf_dict["roles"][role.name])))
    return role_tier

#remplacement de la commande d'help

bot.remove_command("help")

@bot.command(description="commande d'aide pour Botte",
            brief="commande d'aide pour Botte",
            usage="<command as String>")
async def help(ctx,command: str = ""):
    conf_dict=conf_load(ctx.guild.name)
    M=get_max_member_tier(ctx.message.author)
    if len(command)==0:
        embed_dict={}
        for cmd in bot.commands:
            if cmd.name in conf_dict["commands"].keys():
                if int(conf_dict["commands"][cmd.name])<=M or ctx.message.author.guild_permissions.administrator:
                    tier="Tier " + str(conf_dict["commands"][cmd.name])
                    if not(tier in embed_dict):
                        embed_dict[tier]={}
                    embed_dict[tier][cmd.name]=cmd.brief
            elif ctx.message.author.guild_permissions.administrator:
                tier="ADMIN"
                if not(tier in embed_dict):
                    embed_dict[tier]={}
                embed_dict[tier][cmd.name]=cmd.brief
        embed=discord.Embed(colour=discord.Colour.blue(),title="Help command for botte")
        for key in embed_dict.keys():
            for kei in embed_dict[key].keys():
                embed.add_field(name=kei,value=str(embed_dict[key][kei]) + " |" + key ,inline=False)
        await ctx.message.author.send(embed=embed)
        await ctx.send("l'aide t'as été envoyer via MP :thumbsup:")
    else:
        test = False
        tier=""
        if command in conf_dict["commands"].keys():
            if int(conf_dict["commands"][command])<=M or ctx.message.author.guild_permissions.administrator:
                test=True
                tier="Tier " + str(conf_dict["commands"][command])
            else:
                await ctx.send("commande inconnue :/ 1 {}".format(test))
        elif bot.get_command(command) in bot.commands and ctx.message.author.guild_permissions.administrator :
            test = True
            tier="ADMIN"
        else:
            await ctx.send("commande inconnue :/ 2 {}".format(command))
        if test :
            embed=discord.Embed(colour=discord.Colour.blue(),title="Help for the {} command".format(command))
            cmd=bot.get_command(command)
            embed.add_field(name="Description",value=cmd.description,inline=False)
            embed.add_field(name="alias :",value="{}".format(" ,".join(cmd.aliases)),inline=False)
            embed.add_field(name="Utilisation",value=command + " " + cmd.usage)

            embed.add_field(name="Tier",value=tier,inline=False)
            await ctx.send(embed=embed)


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
            description="définit le tier des comamndes du bot, ne suporte pas les aliases",
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

@bot.command(aliases=["sdr","setDefaultR","defaulRank","defaultR","dr"],
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

@bot.command(aliases=["vtf","hset","hierach","h"],
            description="définit l'écart max de tier entre une personne mentionnant et le mentioner" + \
            "\nexpl:si définit a 1 alors si tier 1 mentione tier2 ok si tier 1 mentionne tier 3 pasok" + \
            "\nvaleur négative ou 0 pour désactiver la fonction",
            brief="définit l'écart max de mentionnement autoriser",
            usage="<offset as number>")
async def hierarchie(ctx,offset: int):
    conf_dict = conf_load(ctx.guild.name)
    conf_dict["maxOffset"]= offset or 0
    conf_write(ctx.guild.name,conf_dict)
    await ctx.send("Offset définit a {}".format(offset))

@bot.command(aliases=["welcomeMess","wm","wM","wellcomeM"],
            description="définit le message envoyer au nouveaux arrivant sur le serveur, un message vide signifie que rien ne seras envoyer",
            brief="définit le message envoyer au nouveaux arrivant",
            usage="<isMP as bool> <message as String>")
async def welcomeMessage(ctx,isMP:bool,*,message:str):
    conf_dict=conf_load(ctx.guild.name)
    if isMP:
        conf_dict["welcomeMessage"]["MP"]=message
    else:
        conf_dict["welcomeMessage"]["server"]=message
    conf_write(ctx.guild.name,conf_dict)
    await ctx.send("ce message seras envoyer a tout les nouveaux arrivants !")

@bot.command(aliases=["send"],
            description="envoie une News a tout les joueurs dont le tier associer est supérieure ou égale au tier de la news utilisé unsubNews pour configurer les news que vous souhaiter recevoir",
            brief="envoie une news au joueur",
            usage="<newsTier as int> <News as string>")
async def sendNews(ctx,news_tier:int,*,msg:str):
    conf_dict=conf_load(ctx.guild.name)
    embed=discord.Embed(colour=discord.Colour.blue(),title="News en provenance de : {} ".format(ctx.guild.name))
    title="A destination des roles :"
    for role in conf_dict["roles"].keys():
        if int(conf_dict["roles"][role])>= news_tier:
            title=title + " , " + role 
    
    embed.add_field(name=title,value=msg,inline=False)
    for member in ctx.guild.members :
        T=get_max_member_tier(member)
        if T >= news_tier :
            if member.name in conf_dict["newsOffset"].keys():
                if float(conf_dict["newsOffset"][member.name])<news_tier:
                    await member.send(embed=embed)
            else:
                await member.send(embed=embed)
    await ctx.send("la news a été envoyer ! ;)")


@bot.command(aliases=["sub","unsub","unsubNews","toggleNews"],
            description="permet au choix de toggle la totalité des news si newsTier est omis ou de bloquer les news inférieure ou équale au tier spécifier",
            brief="gère la souscription au news du serveur",
            usage="<optional: newsTier as int>")
async def subNews(ctx,news_tier:int = math.inf):
    conf_dict=conf_load(ctx.guild.name)
    name=ctx.message.author.name
    if news_tier==math.inf :
        if not(name in conf_dict["newsOffset"].keys()):
            conf_dict["newsOffset"][name]=news_tier
            await ctx.send("vous ne receverez plus de news en provenace de ce serveur")
        elif abs(conf_dict["newsOffset"][name])==math.inf:
            conf_dict["newsOffset"][name]=(-1)*conf_dict["newsOffset"][name]
            await ctx.send("vous ne receverez plus de news d'un tier inférieure as {} en provenace de ce serveur".format(conf_dict["newsOffset"][name]))
        else:
            conf_dict["newsOffset"][name]=news_tier
            await ctx.send("vous ne receverez plus de news en provenace de ce serveur")
    else:
        conf_dict["newsOffset"][name]=news_tier
        await ctx.send("vous ne receverez plus de news d'un tier inférieure as {} en provenace de ce serveur".format(news_tier))
    conf_write(ctx.guild.name,conf_dict)
    


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
    elif isinstance(error,commands.MissingRequiredArgument):
        await ctx.send("argument manquant taper bot!help {} pour voir le type des argument".format(ctx.command))
    print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
    traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

@bot.event
async def on_member_join(member):
    conf_dict=conf_load(member.guild.name)
    if "defaltRank" in conf_dict.keys():
        for role in conf_dict["defaltRank"] :
            await member.add_roles(discord.utils.get(member.guild.roles,name=role))
    if len(conf_dict["welcomMessage"]["MP"]) >0:
        await member.send(conf_dict["welcomMessage"]["MP"])
    if len(conf_dict["welcomMessage"]["server"])>0:
        await member.guild.text_channels[0].send(conf_dict["welcomMessage"]["server"])
    
@bot.check
async def checkTier(ctx):
    conf_dict=conf_load(ctx.guild.name)
    exception=("help")
    if(ctx.message.author.guild_permissions.administrator):
        return True
    elif ctx.command.name in exception:
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
    try:
        str(message.author.guild.name)
    except AttributeError:
        if not(message.author.id==bot.user.id):
            await message.channel.send("les commande via mp ne sont pas supporter par le bot :/")
        return
    await bot.process_commands(message)
    conf_dict=conf_load(message.guild.name)
    
    if not(message.author.guild_permissions.administrator) and int(conf_dict["maxOffset"])!=0 and (len(message.mentions)>=0 or len(message.role_mentions)>=0):
        author_tier=get_max_member_tier(message.author)
        test=True
        if len(message.mentions)>=0:
            for member in message.mentions:
                if author_tier + int(conf_dict["maxOffset"]) < get_min_member_tier(member):
                    test=False
        if len(message.role_mentions)>=0:
            for role in message.role_mentions:
                if role.name in conf_dict["roles"].keys():
                    if author_tier+ int(conf_dict["maxOffset"]) <int(conf_dict["roles"][role.name]):
                        test=False
        if not(test):
            await message.delete()

@bot.event
async def on_ready():
    print("bot pret a botter des gens !")

bot.run(get_token())
input()