from typing import TextIO
from .abstract_parser import AbstractParser
from .mesh import Mesh

class EntitiesParser(AbstractParser):

    @staticmethod
    def get_section_name():
        return "$Entities"

    @staticmethod
    def parse(mesh: Mesh, io: TextIO) -> None:
        
        physdict1 = dict()
        physdict2 = dict()
        
        # First: num of entiies
        line = io.readline()
        s = line.strip().split(" ")
        np = int(s[0]) # nb Points
        nc = int(s[1]) # Curves
        ns = int(s[2]) # Surfaces
        nv = int(s[3]) # Volumes
        
        cstart = np
        sstart = np+nc
        
        index = 0
        
        for count in range(10000): # Safety
           line = io.readline()
           if line.startswith("$EndEntities"):
               break
           
           s = line.strip().split(" ")
           
           #if len(s) >= 20: # 2D elements
               #entilist2.append(s[0])
               #physlist2.append(s[8]) # TODO: smething that actually works
               #physdict2[int(s[0])] = int(s[8])# Append to docitonary
           
           if index >= cstart and index < sstart:  # 1D elements
           #elif len(s) >= 8:
               #entilist1.append(s[0])
               #physlist1.append(s[8])
               physdict1[int(s[0])] = int(s[8]) # TODO: case with more than 1 tag
               
           index += 1
               
        mesh.physdict1 = physdict1
        #mesh.physdict2 = physdict2
