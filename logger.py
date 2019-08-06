# -*- coding: utf-8 -*-
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

__author__="Cyril Obrecht"

import os
import datetime
from discord.ext import commands

def f_open(path:str):
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
        """enregistre le string logs dans le types de log spécifé via logtype, les types supporter sont:
        -global:erreur global du bot généralement réserver au stderr
        -cmd:information sur la progression du process des cmd ne contiend pas d'erreur
        -cmdError:erreur survenue lors du process d'une commande
        """
        if logType == "global" :
            fichier=f_open("./Bot_Errors.log")
        elif logType == "cmd" :
            fichier=f_open("./{}/commands.log".format(ctx.guild.name))
        elif logType == "cmdError" :
            fichier = f_open("./Commands_Errors.log")
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