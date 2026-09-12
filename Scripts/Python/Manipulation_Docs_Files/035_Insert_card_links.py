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


#Goes over specified Chapters
#Loads tabs and position in Chapter
#Looks up text in the chapters
#Find all texts marked by {}, these are supposed to be Magic cards
#Finds link for these cards on Scryfall
#Establishes link for cards.

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
    Document_IDs = sorted( list( All_path.keys() ) )

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
    with open( "Chapters_to_update_card_links.txt","r") as IN:
        header = IN.readline()
        for line in IN:
            Date,Access,Chapter_name,Redo = line.rstrip().split("\t")
            if int(Redo):
                Chapters_to_transfer[Chapter_name] = Access
                Docs_to_load.add(Access)
            else:
                print( chapter_positions[Access] )
                print( Chapter_Header_name)
                print( "\n\n")
                Original_presence = chapter_positions[Access].get(Chapter_name,0)
                assert Original_presence
                Chapters_to_transfer[Chapter_name] = Access
                Docs_to_load.add(Access)
    print(Chapters_to_transfer)
    Chapters_listed = sorted( Chapters_to_transfer.keys() )


    #Load the documents
    #Later update to include different Documents
    Access = "AP_Access"
    print(f"Loading Google Doc {Access}")
    print(list( All_path["AP_Access"].keys()))
    cred_path = All_path["AP_Access"]["Credentials"]
    token_path = All_path["AP_Access"]["Token_write"]
    Document_key_number = All_path["AP_Access"]["ID"]
    print( Document_key_number )
    print("Downloading Google Doc...")
    #sys.exit()
    service = get_google_docs_service( doc_path = cred_path, token= token_path )
    Document = get_document(
        service,
        Document_key_number
    )
    print( f"Finished reading Document {Access}")
    Tabs_and_header_infos = dict()
    print( Docs_to_load )
    for ID in Docs_to_load:
        Tabs_and_header_infos[ID] = get_tabs_and_headings(document = Document)
        print( "Loaded all the Tabs.")


    #Go through chapters
    for Chapter in Chapters_listed:
        print( f"Going through {Chapter}...")
        Orig_ID = Chapters_to_transfer[ Chapter ]


        print( "Chapter_data:\t", chapter_positions[Orig_ID][ Chapter ] )
        tabs_and_headers_Orig = Tabs_and_header_infos[Orig_ID]
        tabs_orig = get_tabs_for_chapter(tabs_dict = tabs_and_headers_Orig, Chapter = Chapter)
        if not tabs_orig or len(tabs_orig)>1:
            print(f"Tabs are {tabs_orig}")
            sys.exit(f"Something went wrong when sorting tabs for new chapters.{Chapter}")
        tabs_orig = tabs_orig[0]

        #Get the chapter text

        Tab = get_tab_by_name(document = Document, tab_name = tabs_orig)

        Chapter_text = get_chapter_structured(tab = Tab, chapter_name = Chapter, chapter_level=1)
        print(Chapter_text)

        #Get all parts with {}
        #Look inside if they already have a link
        #Get the card
        #Get scryfall picture link
        #Open document for failed searches
        #insert link



########
#Functions


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


def get_tab_by_name(document, tab_name):
    """
    Return the documentTab corresponding to a tab title.
    """

    for tab in document.get("tabs", []):

        properties = tab.get("tabProperties", {})

        if properties.get("title") == tab_name:
            return tab.get("documentTab")

    return None


def get_google_docs_service(doc_path, token):
    """Authenticate with Google and return the Docs API service."""

    creds = None

    # ---------------------------------------------------------
    # Load existing token
    # ---------------------------------------------------------

    if os.path.exists(token):

        creds = Credentials.from_authorized_user_file(
            token,
            SCOPES
        )

        print("Got token from path:", token)

    # ---------------------------------------------------------
    # Check / refresh / obtain credentials
    # ---------------------------------------------------------

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

        # -----------------------------------------------------
        # Save the credentials to the requested token path
        # -----------------------------------------------------

        with open(token, "w") as token_file:

            token_file.write(
                creds.to_json()
            )

        print("Saved token to:", token)

    # ---------------------------------------------------------
    # Return Google Docs service
    # ---------------------------------------------------------

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


#Main call
if __name__ == "__main__":
    main()



