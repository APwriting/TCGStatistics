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
            if Doc_ID not in chapter_positions:
                chapter_positions[Doc_ID] = dict()
            chapter_positions[Doc_ID][Chapter_Header_name] = [ TabID, Chapter_start, Chapter_end ]

    #Read which chapters to transfer.
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
                Original_presence = chapter_positions[Original].get(Chapter_Header_name,0)
                assert Original_presence
                Copy_presence = chapter_positions[Copy].get(Chapter_Header_name,0)
                if not (Original_presence and Copy_presence ):
                    Chapters_to_transfer[Chapter_name] = (Original,Copy)
                    Docs_to_load.add(Original)
                    Docs_to_load.add(Copy)
    print(Chapters_to_transfer)
    Chapters_listed = sorted( Chapters_to_transfer.keys() )

    #Load the documents
    Documents = dict()
    for ID in Docs_to_load:
        print(f"Loading Google Doc {ID}")
        print(list( All_path[ID].keys()))
        cred_path = All_path[ID]["Credentials"]
        token_path = All_path[ID]["Token_write"]
        Document_key_number = All_path[ID]["ID"]
        print("Downloading Google Doc...")
        service = get_google_docs_service( doc_path = cred_path, token= token_path )
        document = get_document(
            service,
            Document_key_number
        )
        Documents[ID] = document
    #Transfer tabs over in chapter
    Tabs_and_header_infos = dict()
    for ID in Docs_to_load:
        Tabs_and_header_infos[ID] = get_tabs_and_headings(document = Documents[ID])



    for Chapter in Chapters_listed:
        Orig_ID = Chapters_to_transfer[ Chapter ][0]
        Sink_ID = Chapters_to_transfer[ Chapter ][1]
        print( chapter_positions[Orig_ID][ Chapter ] )
        tabs_and_headers_Sink = Tabs_and_header_infos[Sink_ID]
        tabs_and_headers_Orig = Tabs_and_header_infos[Orig_ID]
        tabs_orig = get_tabs_for_chapter(tabs_dict = tabs_and_headers_Orig, Chapter = Chapter)
        if not tabs_orig or len(tabs_orig)>1:
            print(f"Tabs are {tabs_orig}")
            sys.exit(f"Something went wrong when sorting tabs for new chapters.{Chapter}")
        tabs_orig = tabs_orig[0]
        tabs_sink = get_tabs_for_chapter(tabs_dict = tabs_and_headers_Sink, Chapter = Chapter)
        print(tabs_sink)
        if not tabs_sink:
            Chapter_not_present = True
            tab_to_create = tabs_orig[0]
            #create_tab_if_not_exists( service = service, document = Documents[Sink_ID], document_id = All_path[Sink_ID]["ID"], tab_name = tab_to_create)
        else:
            Chapter_not_present = False
        #Get the chapter text
        #print( list(Documents[Orig_ID].keys()) )
        Tab = get_tab_by_name(document = Documents[Orig_ID], tab_name = tabs_orig)
        Chapter_text = get_chapter_structured(tab = Tab, chapter_name = Chapter, chapter_level=1)
        print(Chapter_text)













########
#Functions

def get_tab_by_name(document, tab_name):
    """
    Return the documentTab corresponding to a tab title.
    """

    for tab in document.get("tabs", []):

        properties = tab.get("tabProperties", {})

        if properties.get("title") == tab_name:
            return tab.get("documentTab")

    return None

def get_chapter_structured(tab, chapter_name, chapter_level=1):

    content = tab["body"]["content"]

    # Find chapter
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

    # Find next heading of same level
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

    # Extract elements
    elements = []

    for element in content[chapter_start:chapter_end]:

        if "paragraph" in element:

            paragraph = element["paragraph"]

            style = paragraph.get(
                "paragraphStyle", {}
            ).get(
                "namedStyleType"
            )

            text = ""

            for part in paragraph.get("elements", []):

                if "textRun" in part:
                    text += part["textRun"].get(
                        "content", ""
                    )

            text = text.rstrip("\n")

            if style and style.startswith("HEADING_"):

                elements.append({
                    "type": "heading",
                    "level": int(style.split("_")[1]),
                    "text": text
                })

            else:

                elements.append({
                    "type": "paragraph",
                    "text": text
                })

        elif "table" in element:

            table_data = []

            for row in element["table"].get("tableRows", []):

                row_data = []

                for cell in row.get("tableCells", []):

                    cell_text = ""

                    for cell_element in cell.get("content", []):

                        if "paragraph" in cell_element:

                            for part in cell_element[
                                "paragraph"
                            ].get("elements", []):

                                if "textRun" in part:
                                    cell_text += part[
                                        "textRun"
                                    ].get("content", "")

                    row_data.append(
                        cell_text.rstrip("\n")
                    )

                table_data.append(row_data)

            elements.append({
                "type": "table",
                "rows": table_data
            })

    return {
        "chapter": chapter_name,
        "elements": elements
    }


def create_tab_if_not_exists( service, document,document_id, tab_name):
    """
    Create a Google Docs tab if a tab with the same name
    does not already exist.

    Returns:
        True  - tab was created
        False - tab already existed
    """

    #To be extra sure.
    existing_tab_names = []

    for tab in document.get("tabs", []):
        tab_properties = tab.get("tabProperties", {})
        existing_tab_names.append(
            tab_properties.get("title", "")
        )

    # Check whether the tab already exists
    if tab_name in existing_tab_names:
        print(f"Tab '{tab_name}' already exists.")
        return False

    # Create the tab
    requests = [
        {
            "insertTab": {
                "tabProperties": {
                    "title": tab_name
                }
            }
        }
    ]

    service.documents().batchUpdate(
        documentId=document_id,
        body={"requests": requests}
    ).execute()

    print(f"Tab '{tab_name}' created.")
    return True



def get_tabs_for_chapter(tabs_dict, Chapter):
    """
    Find all tabs containing a given chapter heading.
    tabs_dict from get_tabs_and_headings

    Returns: List of tab names containing the chapter.
    """
    matching_tabs = []

    for tab_name, headings in tabs_dict.items():

        for heading in headings:

            if heading["text"] == Chapter:
                matching_tabs.append(tab_name)
                break

    return matching_tabs




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


def get_tabs_and_headings(document):
    """
    Return all tabs in a Google Doc and all headings within each tab.
    """

    result = {}

    def process_tab(tab):
        tab_properties = tab.get("tabProperties", {})
        tab_name = tab_properties.get("title", "Unnamed tab")

        headings = []

        # Content of this tab
        body = tab.get("documentTab", {}).get("body", {})

        for element in body.get("content", []):

            if "paragraph" not in element:
                continue

            paragraph = element["paragraph"]

            style = paragraph.get(
                "paragraphStyle", {}
            ).get(
                "namedStyleType"
            )

            if style and style.startswith("HEADING_"):

                # Extract text from all text runs
                text = ""

                for elem in paragraph.get("elements", []):

                    if "textRun" in elem:
                        text += elem["textRun"].get(
                            "content", ""
                        )

                headings.append({
                    "level": int(style.split("_")[1]),
                    "text": text.strip(),
                    "startIndex": element.get("startIndex"),
                    "endIndex": element.get("endIndex")
                })

        result[tab_name] = headings

        # Process child tabs recursively
        for child_tab in tab.get("childTabs", []):
            process_tab(child_tab)



    # Process all top-level tabs
    for tab in document.get("tabs", []):
        process_tab(tab)

    return result



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


