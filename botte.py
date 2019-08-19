"""
    Copyright © 2019 Cyril OBRECHT
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
    You should have received a copy of the GNU General Public License
    along with this module.  If not, see <https://www.gnu.org/licenses/>.
"""
__author__ = "Cyril Obrecht"

from datetime import date
import datetime
import asyncio
import os
import json
import math
import traceback
import sys

import discord
from discord.ext import tasks, commands
from discord.ext.commands import Bot

from logger import logger
from config import config
import mc

bot = commands.Bot(command_prefix="bot!")

sys.stderr = logger()  # changement du stderr vers la class logger

####################_Définition des fonctions_####################


def get_token():

    try:

        file = open("token.txt", "r")
        token = file.read()
        file.close()
        return token

    except:

        logger.log(
            "global", "une erreur est survenue le fichier token.txt n'as pas pus être ouvert")
        return ""


def get_max_member_tier(member: discord.Member):

    conf = config(member.guild.name, "server.json")
    role_tier = -math.inf

    for role in member.roles:

        if role.name in conf.config["roles"].keys():
            role_tier = max((role_tier, int(conf.config["roles"][role.name])))

    return role_tier


def get_min_member_tier(member):

    conf = config(member.guild.name, "server.json")
    role_tier = math.inf

    for role in member.roles:

        if role.name in conf.config["roles"].keys():
            role_tier = min((role_tier, int(conf.config["roles"][role.name])))

    return role_tier

####################_remplacement de la commande d'help_####################


bot.remove_command("help")


@bot.command(description="commande d'aide pour Botte",
             brief="commande d'aide pour Botte",
             usage="<command as String>")
async def help(ctx, command: str = ""):
    
    exception = ("help", "subNews")
    conf = config(ctx.guild.name, "server.json")
    M = get_max_member_tier(ctx.message.author)
    
    if len(command) == 0:
        
        embed_dict = {}
        for cmd in bot.commands:
            
            if cmd.name in exception:
                
                tier = "ALL"
                if not(tier in embed_dict):
                    
                    embed_dict[tier] = {}
                embed_dict[tier][cmd.name] = cmd.brief
            
            elif cmd.name in conf.config["commands"].keys():
                
                if int(conf.config["commands"][cmd.name]) <= M or ctx.message.author.guild_permissions.administrator:
                    
                    tier = "Tier " + str(conf.config["commands"][cmd.name])
                    if not(tier in embed_dict):
                        
                        embed_dict[tier] = {}
                    embed_dict[tier][cmd.name] = cmd.brief
            
            elif ctx.message.author.guild_permissions.administrator:
                tier = "ADMIN"
                if not(tier in embed_dict):
                   
                    embed_dict[tier] = {}
                embed_dict[tier][cmd.name] = cmd.brief
        
        embed = discord.Embed(colour=discord.Colour.blue(),
                              title="Help command for botte")
        for key in embed_dict.keys():
            
            for kei in embed_dict[key].keys():
                
                embed.add_field(name=kei, value=str(
                    embed_dict[key][kei]) + " |" + key, inline=False)
        try:
            
            await ctx.message.author.send(embed=embed)
            await ctx.send("l'aide t'as été envoyer via MP :thumbsup:")
        
        except discord.errors.Forbidden:
            
            await ctx.send("ah bah non je peut pas t'envoyer l'help en mp débrouille toi tout seul !")
    else:
        
        test = False
        tier = ""
        cmd = discord.utils.find(lambda c: command in c.aliases, bot.commands)
        
        if cmd != None:
            
            command = cmd.name

        if command in conf.config["commands"].keys():
            
            if int(conf.config["commands"][command]) <= M or ctx.message.author.guild_permissions.administrator:
                
                test = True
                tier = "Tier " + str(conf.config["commands"][command])
            
            else:
                
                await ctx.send("commande inconnue :/ {}".format(test))
        
        elif bot.get_command(command) in bot.commands and ctx.message.author.guild_permissions.administrator:
            
            test = True
            tier = "ADMIN"
        
        else:
            
            await ctx.send("commande inconnue :/ {}".format(command))
        
        if test:
            
            embed = discord.Embed(colour=discord.Colour.blue(
            ), title="Help for the {} command".format(command))
            cmd = bot.get_command(command)
            embed.add_field(name="Description",
                            value=cmd.description, inline=False)
            embed.add_field(name="alias :", value="{}".format(
                " ,".join(cmd.aliases)), inline=False)
            embed.add_field(name="Utilisation",
                            value=command + " " + cmd.usage)

            embed.add_field(name="Tier", value=tier, inline=False)
            await ctx.send(embed=embed)

####################_Créeation des commandes_####################


@bot.command(aliases=["srt", "setRoleT"],
             description="définit le tier des roles du serveur",
             brief="définit le tier des roles du bot",
             usage="<tier as number> <roles as role.mention list>")
async def setRoleTier(ctx, tier: int):
    
    role_list = []
    if len(ctx.message.role_mentions) == 0:
        
        await ctx.send("commande invalide taper bot!help\nle rôle doit pouvoir être mentioner")
    
    else:
        
        conf = config(ctx.guild.name, "server.json")

        for role in ctx.message.role_mentions:
            
            name = role.name
            role_list.append(name)
            conf.config["roles"][name] = tier

        conf.dump()

        await ctx.send('le tier {} est associer au rôle(s): {}'.format(tier, ' ,'.join(role_list)))

@bot.command(aliases=["sct","setCommandT","setCmdT"],
            description="définit le tier des comamndes du bot, ne suporte pas les aliases",
            brief="définit le tier des comamndes du bot",
            usage="<tier as number> <commands as string list>")
async def setCommandTier(ctx,tier: int,*commands:str):
    
    cmd_list=[]
    conf=config(ctx.guild.name,"server.json")
    for command in commands:

        cmd=bot.get_command(command)

        if cmd == None:
            
            cmd = discord.utils.find(lambda c: command in c.aliases, bot.commands)
        
        if cmd != None:
            conf.config["commands"][cmd.name]=tier
            cmd_list.append(cmd.name) 

    conf.dump()

    if len(cmd_list) !=0 :
        
        await ctx.send('le tier {} est associer aux command(s): {}'.format(tier,' , '.join(cmd_list)))
    
    else :

        await ctx.send("Aucune commande n'as été détecter, bot!help pour la liste des commandes")

@bot.command(aliases=["sdr","setDefaultR","defaulRank","defaultR","dr"],
        description="définit le role par défaut attribuer au utilisateur qui rejoingne le server",
        brief="définit le role par défaut",
        usage="<role as role.mention>")
async def setDefaultRank(ctx):

    if len(ctx.message.role_mentions)==0:
        
        await ctx.send("usage incorrecte taper bot!help pour voir la sintaxe\nle role doit pouvoir être mentioner")
    
    else:
        
        conf=config(ctx.guild.name,"server.json")
        C=[]
        
        for role in ctx.message.role_mentions:
            
            C.append(role.name)
            conf.config["defaltRank"]=C
        
        conf.dump()
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
    
    conf=config(ctx.guild.name,"server.json")
    
    for cmd in bot.commands:
        
        if not(cmd.name in conf.config["commands"].keys()):
            
            conf.config["commands"][cmd.name]=tier
    
    conf.dump()
    await ctx.send("tier par default des commande définit a: {}\n les configue existance n'on pas été écraser".format(tier))

@bot.command(aliases=["lien"],
            description="renvoie un lien définit par setLink",
            brief="renvoie un lien définit par setLink",
            usage="")
async def link(ctx):
    conf=config(ctx.guild.name,"server.json")
    if "link" in conf.config.keys():
        await ctx.send(conf.config["link"])
    else:
        await ctx.send("aucun lien n'as été définit :/")

@bot.command(aliases=["sl","setL","setLien"],
            description="définit le lien de la commande link, un message peut être ajouter",
            brief="définit le lien pour link",
            usage="<link as string>")
async def setLink(ctx,*,link):
    
    conf=config(ctx.guild.name,"server.json")
    conf.config["link"]=link
    conf.dump()
    
    await ctx.send("lien sauvegarder :)",delete_after = 30)
    await ctx.message.delete(delay = 20)    

@bot.command(aliases=["vtf","hset","hierach","h"],
            description="définit l'écart max de tier entre une personne mentionnant et le mentioner" + \
            "\nexpl:si définit a 1 alors si tier 1 mentione tier2 ok si tier 1 mentionne tier 3 pasok" + \
            "\nvaleur négative ou 0 pour désactiver la fonction",
            brief="définit l'écart max de mentionnement autoriser",
            usage="<offset as number>")
async def hierarchie(ctx,offset: int):
    
    conf=config(ctx.guild.name,"server.json")
    conf.config["maxOffset"]= offset or 0
    conf.dump()
    await ctx.send("Offset définit a {}".format(offset))

@bot.command(aliases=["welcomeMess","wm","wM","wellcomeM"],
            description="définit le message envoyer au nouveaux arrivant sur le serveur, un message vide signifie que rien ne seras envoyer",
            brief="définit le message envoyer au nouveaux arrivant",
            usage="<isMP as bool> <message as String>")
async def welcomeMessage(ctx,isMP:bool,*,message:str):
    
    conf=config(ctx.guild.name)
    if isMP:
        conf.config["welcomeMessage"]["MP"]=message
    else:
        conf.config["welcomeMessage"]["server"]=message
    conf.dump()
    await ctx.send("ce message seras envoyer a tout les nouveaux arrivants !")

@bot.command(aliases=["send"],
    description="envoie une News a tout les joueurs dont le tier associer est supérieure ou égale au tier de la news utilisé unsubNews pour configurer les news que vous souhaiter recevoir",
    brief="envoie une news au joueur",
    usage="<newsTier as int> <News as string>")
async def sendNews(ctx,news_tier:int,*,msg:str):
    
    logger.log("cmd","envoi du message \"{}\" ".format(msg),ctx)
    conf=config(ctx.guild.name)
    embed=discord.Embed(colour=discord.Colour.blue(),title="News en provenance de : {} ".format(ctx.guild.name))
    role_list=[]
    
    for role in conf.config["roles"].keys():
        
        if int(conf.config["roles"][role])>= news_tier:
            role_list.append(role)
    
    title="A destination des roles : {}".format(", ".join(role_list))
    logger.log("cmd", "titre : \"{}\"".format(title),ctx)
    embed.add_field(name=title,value=msg,inline=False)
    
    async with ctx.channel.typing():
        for member in ctx.guild.members :
        
            logger.log("cmd", "\t évaluation du menbre " + member.name,ctx)
            T=get_max_member_tier(member)
        
            if T >= news_tier :
            
                if member.name in conf.config["newsOffset"].keys():
                
                    logger.log("cmd","membre définit dans les configs")
                    if float(conf.config["newsOffset"][member.name])<news_tier:
                    
                        try:
                        
                            await member.send(embed=embed)
                            logger.log("cmd","\t\tmessage envoyer",ctx)
                    
                        except discord.errors.Forbidden :
                        
                            logger.log("cmd","\t\tmessage non envoyer : discord.errors.Forbidden",ctx)
                            pass
                
                    else:
                    
                        logger.log("cmd","\t\tmessage non envoyer : offset supérieur  au tier ({})".format(conf.config["newsOffset"][member.name]),ctx)

                else:
                
                    try:
                    
                        await member.send(embed=embed)
                        logger.log("cmd","\t\tmessage envoyer",ctx)
                
                    except discord.errors.Forbidden :
                    
                        logger.log("cmd","\t\tmessage non envoyer : discord.errors.Forbidden",ctx)
                        pass
            else:
            
                logger.log("cmd","\t\tmessage non envoyer : tier trop faible ({})".format(T),ctx)
    
        await ctx.send("la news a été envoyer ! ;)")
        
@bot.command(aliases=["sub","unsub","unsubNews","toggleNews"],
            description="permet au choix de toggle la totalité des news si newsTier est omis ou de bloquer les news inférieure ou équale au tier spécifier",
            brief="gère la souscription au news du serveur",
            usage="<optional: newsTier as int>")
async def subNews(ctx,news_tier:int = math.inf):
    
    conf=config(ctx.guild.name)
    name=ctx.message.author.name
    
    if news_tier==math.inf :
        
        if not(name in conf.config["newsOffset"].keys()):
            
            conf.config["newsOffset"][name]=news_tier
            await ctx.send("vous ne receverez plus de news en provenace de ce serveur")
        
        elif abs(conf.config["newsOffset"][name])==math.inf:
            
            conf.config["newsOffset"][name]=(-1)*conf.config["newsOffset"][name]
            await ctx.send("vous ne receverez plus de news d'un tier inférieure as {} en provenace de ce serveur".format(conf.config["newsOffset"][name]))
        
        else:
            
            conf.config["newsOffset"][name]=news_tier
            await ctx.send("vous ne receverez plus de news en provenace de ce serveur")
    else:
        
        conf.config["newsOffset"][name]=news_tier
        await ctx.send("vous ne receverez plus de news d'un tier inférieure as {} en provenace de ce serveur".format(news_tier))
    
    conf.dump()

@bot.command(aliases=["shop","shoplist","shl"],
            description="liste tout les shops trouvés répondant aux critères donné, les tags sont à séparer avec des espaces aucun tag liste tout les shops ",
            brief="effectue une recherche dans les shops",
            usage="<optional: keyword as string>")
async def shopList(ctx,*keyword:str):
    
    try :
        
        shops=mc.Shops(ctx.guild.name)
    
    except json.JSONDecodeError : 
        
        await ctx.send("aucun shop n'as été trouver on dirais bien !")
    
    else:
        msg="liste des shops trouvé :\n"
    
        if len(keyword)!=0:
            
            keyword=" ".join(keyword)
            shops=shops.with_tags(keyword)
        
        else:
            
            logger.log("cmd","aucun argument trouver",ctx)

        for c,shop in enumerate(shops) :
            
            msg+="{}: Vend :{} {} contre :{} {} |{}\n".format(c,shop.sell.qte,shop.sell.name,shop.buy.qte,shop.buy.name,shop.name)
        
        await ctx.send(msg)
        
@bot.command(aliases=["shopadd","shopA"],
            description="créer un nouveaux shop",
            brief="créer un nouveaux shop",
            usage="<Nom_item_vendu as string list> <qte_item_vendu as int> <Nom_item_acheter as string list> <qte_item_acheter as int> <tags as string list>")
async def shopAdd(ctx,*arg):
    
    sell=mc.Item("")
    test=True
    c=0
    
    logger.log("cmd","\trécupération du nom du premier item et de sa quantité",ctx)

    while test:
        
        elem=arg[c]
        
        try:
            
            elem=int(elem)
            test=False
        
        except ValueError:
            
            sell.name += " " + elem
        
        c +=1
        
    sell.qte=int(arg[c-1])
    logger.log("cmd","\trécupération du nom du deuxième item et de sa quantité",ctx)
    buy=mc.Item("")
    test=True
    
    while test:
        
        elem=arg[c]
        
        try:
            
            elem=int(elem)
            test=False
        
        except ValueError:
            
            buy.name += " " + elem
        
        c +=1
        
    buy.qte=int(arg[c-1])
    shop=mc.Shop(ctx.message.author.name,sell,buy,[arg[x].upper() for x in range(c,len(arg,)-1)])
    logger.log("cmd","\trécupération des shops existant et ajout",ctx)
    
    try :
        
        shops=mc.Shops(ctx.guild.name)
        shops.append(shop,shop.name)
    
    except json.JSONDecodeError:
        
        logger.log("cmd","/!\\WARNING/!\\ fichier de shops illisible, ingnorer cette ligne si la commande créais le 1er shop sinon le fichier a été coromput ",ctx)
        shops=mc.Shops(_dict={shop.name:[shop.to_dict()]})
    
    logger.log("cmd","\técriture des shops",ctx)
    shops.dump(ctx.guild.name)

    await ctx.send("le shop a été ajouter a la liste !")

@bot.command(aliases=["shoprm","shopRm","shopRM","shop_rm"],
            description="permet de supprimer un shop via sont numéraux dans la liste donné lors de l'appelle de la commande avec l'argument 'l' la commande accepte '*' comme argument pour indiquer tous",
            brief="permet de suprimer un shop via sont numéraux dans la list bot!help shopRemove pour plus d'information",
            usage="<shop number or '*'>")
async def shopRemove(ctx,nb:str):
    
    logger.log("cmd","\trécupération des shops existant",ctx)
    shops=mc.Shops(ctx.guild.name)
    
    if ctx.message.author.name in shops.dictionary.keys():
        
        logger.log("cmd","\trécupération des shops du joueur",ctx)
        playerShops=mc.Shops(_dict={ctx.message.author.name:shops.dictionary[ctx.message.author.name]})
        
        if nb != "l":
            
            try:
                
                nb=int(nb)
            
            except ValueError:
                
                if "*" != nb :
                    
                    commands.BadArgument()
                
                else:
                    
                    logger.log("cmd","\tsuppression de tout les shops du joueur",ctx)
                    
                    for shop in playerShops.shops:
                        
                        shops.suppr(shop)
                    
                    shops.dump(ctx.guild.name)
                    await ctx.send("tout vos shop on été supprimé !")
                    return
            
            logger.log("cmd","\tsuppression du shop demander par le joueur",ctx)
            shops.suppr(playerShops[nb])
            shops.dump(ctx.guild.name)
            await ctx.send("le shop n° {} a été suprimer".format(nb))
        
        else:
            
            logger.log("cmd","\taffichage des shops du joueur",ctx)
            msg="Vos shops :\n"
            
            for c,shop in enumerate(playerShops):
                
                msg+="{}: Vend :{} {} contre :{} {} \n".format(c,shop.sell.qte,shop.sell.name,shop.buy.qte,shop.buy.name)
            
            await ctx.send(msg)
    
    else:
        
        await ctx.send("vous n'avez encore aucun shop O.o")

@bot.command(aliases=["setRT","srt"],
    description="Définit le tier a partir duquel les reports sont envoyés au utilisateur, les report ignore la configuration des news, laisser le tier vide désactive l'envoie par tier, par defaut ils sont envoyés automatiquement au administrateur du server, toggleAdminReport pour desactivé l'envoie au admin, toggleWarning pour desactivé les message d'allerte",
    brief="definit le tier a partir duquel les report sont envoyer, laisser vide pour désactiver l'envoie par tier",
    usage="<tier as int>")
async def setReportTier(ctx,tier:str):
    
    conf=config(ctx.guild.name,"report")
    
    if len(tier)==0:
        
        if "tier" in conf.config.keys():
            
            del conf.config["tier"]
    
    else:
            
            try : 
                
                tier=int(tier)
                conf.config["tier"]=tier
            
            except ValueError :
                
                await ctx.send("Le tier spécifier n'est pas valide")
                return
    
    conf.dump()

@bot.command()
async def toggleAdminReport(ctx):
    
    conf=config(ctx.guild.name,"report")

    if "admin" in conf.config.keys():
        
        conf.config["admin"]= not(conf.config["admin"])
    
    else:
        
        conf.config["admin"]=False
    
    conf.dump()

    if conf.config["admin"]:
        
        await ctx.send("l'envoie des report au admin a été reactivé :)")
    
    else:
        
        await ctx.send("l'envoie des report au admin a été desactivée")

@bot.command()
async def toggleWarning(ctx):
    
    conf=config(ctx.guild.name,"report")

    if "warning" in conf.config.keys():
        
        conf.config["warning"]= not(conf.config["warning"])
    
    else:
        
        conf.config["warning"]=False
    
    conf.dump()

    if conf.config["warning"]:
        
        await ctx.send("l'envoie des warning a été reactivé :)")
    
    else:
        
        await ctx.send("l'envoie des warning a été desactivée")

@bot.command()
async def report(ctx,*,msg:str)

####################_Event du bot_####################


@bot.event
async def on_command_error(ctx, error):

    if hasattr(ctx.command, 'on_error'):
        return
    elif isinstance(error, commands.CheckFailure):
        await ctx.send("vous n'avez pas les doits pour effectuer cette commande")
        return
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send("commande inexistante taper bot!help pour voir la liste des commandes")
        return
    elif isinstance(error, commands.BadArgument):
        await ctx.send("argument invalide taper bot!help {} pour voir le type des argument".format(ctx.command))
        return
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("argument manquant taper bot!help {} pour voir le type des argument".format(ctx.command))
        return
    logger.log("cmdError", 'Ignoring exception in command :' + ctx.command.name +
               ' with argument {} :\n\t\t\t{}\n\t\t\t{}'.format(" ,".join([str(x) for x in ctx.args]), type(error), error))
    for lines in traceback.format_exception(type(error), error, error.__traceback__):
        logger.log("cmdError", lines)


@bot.event
async def on_member_join(member):
    conf = config(member.guild.name, "server.json")
    if "defaltRank" in conf.config.keys():
        for role in conf.config["defaltRank"]:
            await member.add_roles(discord.utils.get(member.guild.roles, name=role))
    if len(conf.config["welcomeMessage"]["MP"]) > 0:
        await member.send(conf.config["welcomeMessage"]["MP"])
    if len(conf.config["welcomeMessage"]["server"]) > 0:
        await member.guild.text_channels[0].send(conf.config["welcomeMessage"]["server"])


@bot.check
async def checkTier(ctx):
    conf = config(ctx.guild.name, "server.json")
    exception = ("help", "subNews")
    if(ctx.message.author.guild_permissions.administrator):
        return True
    elif ctx.command.name in exception:
        return True
    elif ctx.command.name in conf.config["commands"].keys():
        if get_max_member_tier(ctx.message.author) >= int(conf.config["commands"][ctx.command.name]):
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
        if not(message.author.id == bot.user.id):
            await message.channel.send("les commande via mp ne sont pas supporter par le bot :/")
        return
    if message.content.startswith("bot!"):
        ctx = await bot.get_context(message)
        logger.log("cmd", "Lancement du process de :\"" + message.content +
                   "\" par : {} \n".format(message.author.name), ctx)
        await bot.process_commands(message)
        logger.log("cmd", "=====Process Termier=====", ctx)
    conf = config(message.guild.name, "server.json")

    if not(message.author.guild_permissions.administrator) and int(conf.config["maxOffset"]) != 0 and (len(message.mentions) >= 0 or len(message.role_mentions) >= 0):
        author_tier = get_max_member_tier(message.author)
        test = True
        if len(message.mentions) >= 0:
            for member in message.mentions:
                if author_tier + int(conf.config["maxOffset"]) < get_min_member_tier(member):
                    test = False
        if len(message.role_mentions) >= 0:
            for role in message.role_mentions:
                if role.name in conf.config["roles"].keys():
                    if author_tier + int(conf.config["maxOffset"]) < int(conf.config["roles"][role.name]):
                        test = False
        if not(test):
            await message.delete()


@bot.event
async def on_ready():
    print("bot pret a botter des gens !")

bot.run(get_token())