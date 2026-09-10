import os
import sys
import yaml

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build



SCOPES = [
    "https://www.googleapis.com/auth/documents"
]


#Looks up a file where chapters are presented that are supposed to be transfered.

#Looks up chapters that are in between both files

#If necessary establishes the presence of the same tabs.

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
    Documents = sorted( list( All_path.keys() ) )

    #Load information about chapters
    chapter_positions = dict()
    with open( "Exisitng_tabs_for_each_document.txt","r") as IN:
        header = IN.readline()
        for line in IN:
            elements = line.rstrip().split("\t")
            Doc_ID = elements[0]
            TabID = elements[2]
            Chapter_Header_name = elements[5]
            Chapter_start = elements[6]
            Chapter_end = elements[7]
            if DOC_ID not in chapter_positions:
                chapter_positions[Doc_ID] = dict()
            chapter_positions[Doc_ID][Chapter_Header_name] = [ TabID, Chapter_start, Chapter_end ]

        #Read which chapters to transfer.
        Chapters_to_transfer = dict()
        with open("Chapters_to_transfer_over.txt", "r") as IN:
            header = IN.readline()
            for line in IN:
                Date,Original,Copy,Chapter_name,Redo = line.rstrip().split("\t")
                if int(Redo):
                    Chapters_to_transfer[Chapter_name] = (Original,Copy)
                else:
                    Original_presence = chapter_positions[Original].get(Chapter_Header_name,0)
                    assert Original_presence
                    Copy_presence = chapter_positions[Copy].get(Chapter_Header_name,0)
                    if not (Original_presence and Copy_presence ):
                        Chapters_to_transfer[Chapter_name] = (Original,Copy)














########
#Functions

def get_headings(tab):

    headings = []

    for element in tab["body"]["content"]:

        if "paragraph" not in element:
            continue

        paragraph = element["paragraph"]

        style = paragraph.get(
            "paragraphStyle", {}
        ).get(
            "namedStyleType"
        )

        if style and style.startswith("HEADING_"):

            text = ""

            for elem in paragraph.get("elements", []):

                if "textRun" in elem:
                    text += elem["textRun"].get(
                        "content", ""
                    )

            headings.append({
                "level": int(style.split("_")[1]),
                "text": text.strip(),
                "startIndex": element["startIndex"],
                "endIndex": element["endIndex"]
            })

    return headings



def get_google_docs_service( doc_path, token ):
    """Authenticate with Google and return the Docs API service."""

    creds = None

    if os.path.exists(token):
        creds = Credentials.from_authorized_user_file(
            token,
            SCOPES
        )
        print("Got Token from path...")

    if not creds or not creds.valid:

        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())

        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                doc_path,
                SCOPES
            )

            creds = flow.run_local_server(port=0)

            with open("token.json", "w") as token:
                token.write(creds.to_json())

    return build("docs", "v1", credentials=creds)


def get_document(service, document_id):

    document = service.documents().get(
        documentId=document_id,
        includeTabsContent=True
    ).execute()

    return document


#Main call
if __name__ == "__main__":
    main()


