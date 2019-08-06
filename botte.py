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


import discord
from discord.ext import tasks, commands
from discord.ext.commands import Bot
from datetime import date
import datetime
import asyncio
import os
import json
import math
import traceback
import sys
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
    if len(conf.config["welcomMessage"]["MP"]) > 0:
        await member.send(conf.config["welcomMessage"]["MP"])
    if len(conf.config["welcomMessage"]["server"]) > 0:
        await member.guild.text_channels[0].send(conf.config["welcomMessage"]["server"])


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
