import os
import sys
import yaml
import json

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

#This script does a different approach to 034
#The goal is 

SCOPES = [
    "https://www.googleapis.com/auth/documents"
]


#Starts a transfer of the data from one chapter to the next.
def main():

    #Load here the path to the credentials
    cred_path = ""
    All_path = dict()
    with open( "path_to_token.txt","r") as IN:
        header = IN.readline()
        for line in IN:
            cred_path_parts = line.rstrip().split("\t")
            Purpose, Type, Path = cred_path_parts
            if Purpose != "Purpose":
                if Purpose not in All_path:
                    All_path[Purpose] = dict()
                All_path[Purpose][Type] = Path
    Documents_IDs = sorted( list( All_path.keys() ) )

    #Load information about chapters
    chapter_positions = dict()
    Chapter_rel_numbering = dict() #Gives chaptes relative to each chapter in each tab
    with open( "Exisitng_tabs_for_each_document.txt","r") as IN:
        header = IN.readline()
        for line in IN:
            elements = line.rstrip().split("\t")
            Doc_ID = elements[0]
            TabID = elements[2]
            Chapter_Header_name = elements[5]
            Chapter_start = elements[6]
            Chapter_end = elements[7]
            Chapter_Numbering = elements[8]
            Chapter_tab_rel_pos = elements[9]
            if Doc_ID not in chapter_positions:
                chapter_positions[Doc_ID] = dict()
            chapter_positions[Doc_ID][Chapter_Header_name] = [ TabID, Chapter_start, Chapter_end ]
            if Doc_ID not in Chapter_rel_numbering:
                Chapter_rel_numbering[Doc_ID] = dict()
            if TabID not in Chapter_rel_numbering[Doc_ID]:
                Chapter_rel_numbering[Doc_ID][TabID] = dict()
            Chapter_rel_numbering[Doc_ID][TabID][ Chapter_tab_rel_pos ] = (Chapter_Numbering, Chapter_Header_name)
            Chapter_rel_numbering[Doc_ID][TabID][ Chapter_Header_name ] =  Chapter_tab_rel_pos
