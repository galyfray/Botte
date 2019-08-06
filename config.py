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

import json
import os


def f_open(path:str,mod:str="a"):
    if os.path.exists(path):
        fichier = open(path,mod)
    else:
        fichier=open(path,"w")
    return fichier

class config(object):
    
    def __init__(self,guild_name:str,conf_name:str):
        
        self.dir_name=guild_name
        self.name=conf_name
        
        if not(os.path.isdir("./" + guild_name)):
            os.mkdir("./" + guild_name)
        
        if not(os.path.exists("./" + guild_name + "/" + conf_name)):
            f=open("./" + guild_name + "/" + conf_name,"w")
            D={}
            json.dump(D,f)
        
        with f_open("./" + guild_name + "/" + conf_name,"r") as f:
            self.config=json.load(f)
            f.close()
    
    def dump(self):

        with f_open("./" + self.dir_name + "/" + self.name,"w+") as f:
            json.dump(self.config,f,sort_keys=True, indent=4)
            f.close()