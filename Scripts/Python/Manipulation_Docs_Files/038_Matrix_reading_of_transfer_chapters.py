import os
import sys
import yaml
import json

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

#from Docbooks import Docbook
import Docbooks

#This script does a different approach to 034
#The goal is 

SCOPES = [
    "https://www.googleapis.com/auth/documents"
]


#Starts a transfer of the data from one chapter to the next.
def main():

    #Load here the path to the credentials
    print("Reading credential paths")
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
    if 0:
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

    #LOAD THE DOCBOOK
    print("Making the docbook..")
    #docbook = Docbook("Exisitng_tabs_for_each_document.txt")

    #Load the documents
    print( "Starting to load documents..")
    Documents = dict()
    for ID in Documents_IDs:
        print(f"Loading Google Doc {ID}")
        print(list( All_path[ID].keys()))
        cred_path = All_path[ID]["Credentials"]
        token_path = All_path[ID]["Token_write"]
        Document_key_number = All_path[ID]["ID"]
        print("Downloading Google Doc...")
        try:
            with open(token_path, "r") as f:
                token_data = json.load(f)
            print("Token client ID:")
            print(token_data["client_id"])
        except:
            print("NO TOKEN PRESENT.")
        with open(cred_path, "r") as f:
            credential_data = json.load(f)



        print("\nCredentials client ID:")

        # Desktop OAuth credentials are normally under "installed"
        print(credential_data["installed"]["client_id"])

        service = get_google_docs_service( doc_path = cred_path, token= token_path )
        document = get_document(
            service,
            Document_key_number
        )
        if ID == "AP_Access":
            with open("example_document.txt","w", encoding="utf-8") as OUT:
                print(document, file=OUT)
            #sys.exit("Stopping until further notice.")

        Documents[ID] =  document       #  docbook.copy()
       # Documents[ID].add_document(
        #                    ID,
        #                    document
        #                )
        #Documents[ID].digest_chapters(doc_id = ID)



    #Read which chapters to transfer.
    print("Reading Chaper structure to transfer..")

    Chapters_to_transfer = dict()
    Docs_to_load = set()
    with open("Chapters_to_transfer_over.txt", "r") as IN:
        header = IN.readline()
        for line in IN:
            Date,Original,Copy,Chapter_name,Redo = line.rstrip().split("\t")
            if int(Redo):
                Chapters_to_transfer[Chapter_name] = (Original,Copy)
                Docs_to_load.add(Original)
                Docs_to_load.add(Copy)
            else:
                #print(Original)
                if 0:
                    Original_presence = Documents[Original].get_chapter(
                                            doc_id = Original,
                                            chapter_name = Chapter_name,tab=None
                                        )            #chapter_positions[Original].get(Chapter_Header_name,0)
                    #print(Original_presence)
                    #sys.exit()
                    assert Original_presence
                    Copy_presence = Documents[Copy].get_chapter(
                                            doc_id = Copy,
                                            chapter_name = Chapter_name,tab=None
                                        )
                    #sys.exit()
                    if not ( Original_presence and Copy_presence ): #Tests if a chapter is already present in sink
                        Chapters_to_transfer[Chapter_name] = (Original,Copy)
                        Docs_to_load.add(Original)
                        Docs_to_load.add(Copy)
                    elif ( Original_presence and Copy_presence ):
                        Mind_last_chapter_position = True
                
    print("Chapters_to_transfer")
    ID = "AP_Access"
    Tabs = Documents[ID]["tabs"][1]
    #print( Tabs )
    #AP_try = Docbooks.Tab.from_google_docs(Tabs )

    AP_try = Docbooks.Document.from_google_docs( Documents[ID] )
    #print(AP_try)
    #Second_TAB = AP_try.deep_find_element(searched_name = "2-3. The Basics and History" )#"t.esursc3mx121")
    #print(Second_TAB)
    Second_TAB = AP_try.deep_find_element(searched_name = "1. Intro Parts" )#"t.esursc3mx121")
    #print(Second_TAB)
    chapters = Second_TAB.chain[1::]
    print(len(chapters))
    TAB_reconstructed = Docbooks.Tab.from_sub_element_list(elements = chapters, name="1. Intro Parts")
    print("TESTING FUNCTION FOR CREATING CLASS FROM LIST OF ELEMENTS\n\n")
    print(TAB_reconstructed)
    print("TESTING COMPLETED")
    requests = TAB_reconstructed.Create_insertion_call()
    with open("temp", "w") as IN:
        for request in requests:
            print(request, file=IN)

    sys.exit("!!!!!!!!!!!!!")
    Chapters_listed = sorted( Chapters_to_transfer.keys() )




    results = docbook.find_chapters(chapter_names = Chapters_listed)
    print(results)



#Get the chapters, and their tabs. Sort those by tabs.
#Check if tabs exist in the sink document.

#Get all the chapters already present. 
#Get the chapters to transfer over.
#Check which of these should be transfered again.
#Get the ones not in the transfer list.
#Sort them by name, both.































########################################################################################
#Functions







def get_google_docs_service(doc_path, token):
    """Authenticate with Google and return the Docs API service."""
    creds = None
    # ---------------------------------------------------------
    # Load existing token

    if os.path.exists(token):

        creds = Credentials.from_authorized_user_file(
            token,
            SCOPES
        )
        print("Got token from path:", token)

    # Check / refresh / obtain credentials
    if creds:

        print("Credentials valid:", creds.valid)
        print("Credentials expired:", creds.expired)
        print(
            "Has refresh token:",
            creds.refresh_token is not None
        )
        print("Scopes:", creds.scopes)

    if not creds or not creds.valid:

        if creds and creds.expired and creds.refresh_token:
            print("Refreshing credentials...")
            creds.refresh(Request())
            print(
                "Credentials valid after refresh:",
                creds.valid
            )
        else:
            print("Starting new OAuth authentication...")
            flow = InstalledAppFlow.from_client_secrets_file(
                doc_path,
                SCOPES
            )
            creds = flow.run_local_server(
                port=0
            )
        # Save the credentials to the requested token path
        with open(token, "w") as token_file:

            token_file.write(
                creds.to_json()
            )

        print("Saved token to:", token)
    # ---------------------------------------------------------
    # Return Google Docs service

    print(creds.scopes)
    print(creds.valid)
    print(creds.expired)
    
    return build(
        "docs",
        "v1",
        credentials=creds
    )


def get_document(service, document_id):

    document = service.documents().get(
        documentId=document_id,
        includeTabsContent=True
    ).execute()

    return document





def get_chapter_structured(tab, chapter_name, chapter_level=1):

    content = tab["body"]["content"]

    # ---------------------------------------------------------
    # Find chapter
    # ---------------------------------------------------------

    chapter_start = None

    for i, element in enumerate(content):

        if "paragraph" not in element:
            continue

        paragraph = element["paragraph"]

        style = paragraph.get(
            "paragraphStyle", {}
        ).get(
            "namedStyleType"
        )

        if style != f"HEADING_{chapter_level}":
            continue

        text = ""

        for part in paragraph.get("elements", []):

            if "textRun" in part:
                text += part["textRun"].get(
                    "content", ""
                )

        if text.strip() == chapter_name:
            chapter_start = i
            break

    if chapter_start is None:
        print(f"Chapter '{chapter_name}' not found.")
        return None

    # ---------------------------------------------------------
    # Find next heading of same level
    # ---------------------------------------------------------

    chapter_end = len(content)

    for i in range(chapter_start + 1, len(content)):

        if "paragraph" not in content[i]:
            continue

        paragraph = content[i]["paragraph"]

        style = paragraph.get(
            "paragraphStyle", {}
        ).get(
            "namedStyleType"
        )

        if style == f"HEADING_{chapter_level}":
            chapter_end = i
            break

    # ---------------------------------------------------------
    # Extract elements
    # ---------------------------------------------------------

    elements = []

    for element in content[chapter_start:chapter_end]:

        # =====================================================
        # Paragraph
        # =====================================================

        if "paragraph" in element:

            paragraph = element["paragraph"]

            # ---------------------------------------------
            # Paragraph formatting
            # ---------------------------------------------

            paragraph_style = paragraph.get(
                "paragraphStyle", {}
            ).copy()

            named_style = paragraph_style.get(
                "namedStyleType"
            )

            # ---------------------------------------------
            # Text runs
            # ---------------------------------------------

            runs = []

            for part in paragraph.get("elements", []):

                if "textRun" not in part:
                    continue

                text_run = part["textRun"]

                runs.append({
                    "text": text_run.get(
                        "content", ""
                    ),
                    "textStyle": text_run.get(
                        "textStyle", {}
                    ).copy()
                })

            # ---------------------------------------------
            # Combine text for identifying headings
            # ---------------------------------------------

            text = "".join(
                run["text"]
                for run in runs
            ).rstrip("\n")

            # ---------------------------------------------
            # Heading
            # ---------------------------------------------

            if (
                named_style
                and named_style.startswith("HEADING_")
            ):

                elements.append({
                    "type": "heading",
                    "level": int(
                        named_style.split("_")[1]
                    ),
                    "text": text,
                    "paragraphStyle": paragraph_style,
                    "runs": runs
                })

            # ---------------------------------------------
            # Normal paragraph
            # ---------------------------------------------

            else:

                elements.append({
                    "type": "paragraph",
                    "text": text,
                    "paragraphStyle": paragraph_style,
                    "runs": runs
                })

        # =====================================================
        # Table
        # =====================================================

        elif "table" in element:

            table_data = []

            for row in element["table"].get(
                "tableRows", []
            ):

                row_data = []

                for cell in row.get(
                    "tableCells", []
                ):

                    cell_data = []

                    for cell_element in cell.get(
                        "content", []
                    ):

                        if "paragraph" not in cell_element:
                            continue

                        paragraph = cell_element[
                            "paragraph"
                        ]

                        paragraph_style = paragraph.get(
                            "paragraphStyle", {}
                        ).copy()

                        runs = []

                        for part in paragraph.get(
                            "elements", []
                        ):

                            if "textRun" not in part:
                                continue

                            text_run = part["textRun"]

                            runs.append({
                                "text": text_run.get(
                                    "content", ""
                                ),
                                "textStyle": text_run.get(
                                    "textStyle", {}
                                ).copy()
                            })

                        cell_data.append({
                            "paragraphStyle": paragraph_style,
                            "runs": runs
                        })

                    row_data.append(cell_data)

                table_data.append(row_data)

            elements.append({
                "type": "table",
                "rows": table_data
            })

    return {
        "chapter": chapter_name,
        "elements": elements
    }



#Main call
if __name__ == "__main__":
    main()


