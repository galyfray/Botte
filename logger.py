import os
import datetime
from discord.ext import commands

def Aopen(path:str):
    if os.path.exists(path):
        fichier = open(path,"a")
    else:
        fichier=open(path,"w")
    return fichier

class logger(object):

    def __init__(self):
        pass

    @staticmethod
    def log(logType:str,logs:str,ctx:commands.Context=None):
        if logType == "global" :
            fichier=Aopen("./Bot_Errors.log")
        elif logType == "cmd" :
            fichier=Aopen("./{}/commands.log".format(ctx.guild.name))
        elif logType == "cmdError" :
            fichier = Aopen("./Commands_Errors.log")
        else:
            if ctx == None:
                cmd="none"
            else:
                cmd=ctx.command
            logger.log("global", "Erreur lors de l'écriture des Logs : \n    |Cmd:{}\n   |logType:{}\n    |logs:{}".format(cmd,logType,logs))
        logs = "[" + datetime.datetime.now().isoformat(sep=' ',timespec='seconds') + "]" + logs

        if not(logs.endswith("\n")):
            logs=logs + "\n"
        fichier.write(logs)

    def write(self,data):
        logger.log("global",data)