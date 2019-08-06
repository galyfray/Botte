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

from config import config
from logger import logger

class Item(object):
    """creation de la class item contien de quoi definir un stack minecraft:
       -nom
       -id
       -qte
       -mod
       -meta
       -stacksize
       """
    
    def __init__(self,name:str = "Air",id:int = 0,meta:int = 0,mod:str = "minecraft",qte:int = 0,stacksize:int = 64):
        self.name=name
        self.id=id
        self.meta=meta
        self.mod=mod
        self.qte=qte
        self.stacksize=stacksize
    
    def __add__(self,add):
        item=self
        if type(add) == type(self):
            if ((item.name == add.name and (item.id == add.id  or item.id == 0 or add.id == 0)) or (add.id == item.id and (item.name == "Air" or add.name == "Air"))) and item.meta == add.meta:
                item.qte+=add.qte
                if item.name=="Air":
                    item.name=add.name
                if item.id==0:
                    item.id=add.id
        elif type(add)==type(0):
            item.qte+=add
        return item
    
    def to_dict(self):
        D=dict()
        D["name"]=self.name
        D["id"]=self.id
        D["meta"]=self.meta
        D["mod"]=self.mod
        D["qte"]=self.qte
        D["stacksize"]=self.stacksize
        return D
    
    @staticmethod
    def from_dict(item_dict:dict):
        I=Item()
        I.name=item_dict["name"]
        I.id=item_dict["id"]
        I.meta=item_dict["meta"]
        I.mod=item_dict["mod"]
        I.qte=item_dict["qte"]
        I.stacksize=item_dict["stacksize"]
        return I




class Shop(object):
    """creation de la class shop elle seras definit par :
       -nom du proprio
       -item vendu
       -item acheter
       -tag
       """

    def __init__(self,name:str = "",sell:Item=Item(),buy:Item=Item(),tag:list = list()):
        self.name=name
        self.sell=sell
        self.buy=buy
        tag.append(sell.name)
        tag.append(buy.name)
        self.tag=[x.upper() for x in tag]
    
    def __contains__(self,obj):
        if type(obj) == type(""):
            test=False
            for tag in self.tag:
                if obj.upper() in tag :
                    test=True
            return test
        else:
            return False
    
    def to_dict(self):
        D=dict()
        D["name"]=self.name
        D["sell"]=self.sell.to_dict()
        D["buy"]=self.buy.to_dict()
        D["tag"]=self.tag
        return D
    
    @staticmethod
    def from_dict(shop_dict:dict):
        S=Shop()
        S.name=shop_dict["name"]
        S.sell=Item.from_dict(shop_dict["sell"])
        S.buy=Item.from_dict(shop_dict["buy"])
        S.tag=shop_dict["tag"]
        return S

class Shops(object):
    """shops représente tout les shop du serv discord
    -guild_name ou _dict est obligatoire
    -_dict est un dictionnaire de la forme: {"shop group name":[{shop_dict},{shop_dict}],"shop group name 2 ":[{shop_dict},{shop_dict}] ... }"""
    def __init__(self,guild_name:str="",_dict:dict={}):
        
        self.shops=[]
        
        if len(_dict) == 0 :
            if len(guild_name) == 0:
                raise AttributeError("no guild name")
            else:
                self._config=config(guild_name,"shops.json")
                self._dict=self._config.config
        else:
            self._dict=_dict
        for key in self._dict:
            for shop in self._dict[key]:
                if not type(shop)==type({}):
                    logger.log("cmdError","format du dict reçus : " + str(self._dict))
                    raise ValueError("format de l'argument _dict non valide {} est attendu {} a été trouver".format(type({}),type(shop)))
                else:
                    self.shops.append(Shop.from_dict(shop))
    
    def __getitem__(self,index):
        return self.shops[index]
    
    def __delitem__(self,index):
        dico=self.shops[index].to_dict()
        del self.shops[index]
        for key in self._dict:
            for c,shop in enumerate(self._dict[key]):
                if dico == shop :
                    del self._dict[key][c]

    def __iter__(self):
        return iter(self.shops)

    def _get_dict(self):
        return self._dict
    
    def dump(self,guild_name:str):
        self._config.config=self._dict
        self._config.dump()

    def with_tags(self,tag:str):
        D={tag:[]}
        tags=tag.split()
        for shop in self.shops:
            test=True
            for tag in tags: 
                if not(tag in shop):
                    test=False
            if test:  
                D[tag].append(shop.to_dict())
        return Shops(_dict=D)
    
    def append(self,shop:Shop,cat:str):
        self.shops.append(shop)
        self._dict[cat].append(shop.to_dict())

    def suppr(self,shopRM:Shop):
        RMdict=shopRM.to_dict()
        for c,shop in enumerate(self.shops):
            if shop.to_dict()==RMdict:
                del self[c]

    dictionary=property(_get_dict)