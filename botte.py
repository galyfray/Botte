import discord
from discord.ext import tasks, commands
from discord.ext.commands import Bot
import asyncio
import os

bot=commands.Bot(command_prefix="bot!")

@bot.command()
async def tierSet(ctx,tier):
    C=[]
    if len(ctx.message.role_mentions)==0:
        await ctx.send("usage de la commande: bot!tierSet (int)tier @role @role  ... \nle rôle doit pouvoir être mentioner")
    elif type(tier) is int:
        for r in ctx.message.role_mentions:
            C.append(r.mention)
        
        await ctx.send('le tier {} est associer au rôle(s): {}'.format(tier,' , '.join(C)))
    else:
        await ctx.send("usage de la commande: bot!tierSet (int)tier @role @role  ... ")
        


@bot.event
async def on_message(message):
    await bot.process_commands(message)



@bot.event
async def on_ready():
    print("My body is ready !")



bot.run("NTkwNDkxMDI3NjMxMTEyMjAy.XQnYRQ.0U-M5F__kWzklClaUd2wfkjoDJ4")

