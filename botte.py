import discord
from discord.ext import tasks, commands
from discord.ext.commands import Bot
import asyncio
import os

bot=commands.Bot(command_prefix="bot!")

@bot.command()
async def tierSet(ctx,tier: int):
    C=[]
    print(type(tier))
    if len(ctx.message.role_mentions)==0:
        await ctx.send("commande invalide veuiller mentioner le role dans la commande")
    else:
        for r in ctx.message.role_mentions:
            C.append(r.mention)
        
        await ctx.send('le tier {} est associer au rôle(s): {}'.format(tier,' , '.join(C)))


@bot.event
async def on_message(message):
    await bot.process_commands(message)



@bot.event
async def on_ready():
    print("My body is ready !")



bot.run("NTkwNDkxMDI3NjMxMTEyMjAy.XQnYRQ.0U-M5F__kWzklClaUd2wfkjoDJ4")

