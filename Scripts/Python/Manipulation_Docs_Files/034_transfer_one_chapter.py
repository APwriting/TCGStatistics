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
                Copy_presence = chapter_positions[Copy].get(Chapter_name,0)
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

        TABID_mapping = get_tab_id_mapping(source_document = Documents[Orig_ID], destination_document = Documents[Sink_ID])

        print(TABID_mapping)
        #sys.exit()

        print( "Chapter_data:\t", chapter_positions[Orig_ID][ Chapter ] )
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
        #print("Before")
        #print(Chapter_text)
        Chapter_text = clean_text_style(text_style = Chapter_text, tab_id_mapping = TABID_mapping)
        Chapter_text["elements"] = clean_internal_links(
            elements=Chapter_text["elements"]
        )
        #print("After")
        #print(Chapter_text)
        #sys.exit()
        #TABID_mapping

        print(Chapter_text)
        #tab_ID = get_tab_id_by_name(document =  Documents[Orig_ID], tab_name = tabs_orig)
        if Chapters_to_transfer:
            #Tab = get_tab_by_name(document = Documents[Sink_ID], tab_name = tabs_orig)
            #properties = Tab.get("tabProperties", {})
            tabID = get_tab_id_by_name(document = Documents[Sink_ID], tab_name = tabs_orig)
            #print(properties)
            print(tabID)
            #sys.exit()
            #tabID = properties.get("tabId")
            Chapter_insert = chapter_positions[Orig_ID][ Chapter ][1]
            insert_chapter_into_document( service = service,
                document_id = All_path[Sink_ID]["ID"],
                tab_id = tabID,
                chapter = Chapter_text,
                insert_index = int(Chapter_insert)
            )













########
#Functions

def clean_internal_links(elements):
    """
    Remove all internal links from the extracted chapter.

    For every run containing an internal link (a link with 'tabId'),
    the link is removed and ' ADD LINK HERE' is appended to the
    linked text.

    External URL links are left unchanged.
    """

    for element in elements:

        if element["type"] not in ["paragraph", "heading"]:
            continue

        runs = element.get("runs", [])

        for run in runs:
            text_style = run.get("textStyle", {})

            if "link" not in text_style:
                continue

            link = text_style["link"]

            # Only treat links containing tabId as internal links
            if "tabId" in link:

                # Remove the internal link
                del text_style["link"]

                # Add replacement text to the same run
                run["text"] = run.get("text", "").rstrip("\n") \
                    + " ADD LINK HERE\n"

        # Recalculate paragraph text
        element["text"] = "".join(
            run.get("text", "")
            for run in runs
        ).rstrip("\n")

    return elements

def clean_text_style(text_style, tab_id_mapping):

    text_style = text_style.copy()

    if "link" in text_style:

        link = text_style["link"].copy()

        if "tabId" in link:

            source_tab_id = link["tabId"]

            if source_tab_id in tab_id_mapping:

                # Replace source tab ID
                link["tabId"] = tab_id_mapping[
                    source_tab_id
                ]

                text_style["link"] = link

            else:

                # No corresponding destination tab
                del text_style["link"]

    return text_style

def get_tab_id_mapping(source_document, destination_document):
    """
    Create a mapping from source tab IDs to destination tab IDs
    based on matching tab names.
    """

    mapping = {}

    def collect_tabs(document):

        result = {}

        def recurse(tabs):

            for tab in tabs:

                properties = tab.get(
                    "tabProperties",
                    {}
                )

                tab_id = properties.get("tabId")
                tab_name = properties.get("title")

                if tab_id and tab_name:
                    result[tab_name] = tab_id

                recurse(
                    tab.get("childTabs", [])
                )

        recurse(
            document.get("tabs", [])
        )

        return result

    source_tabs = collect_tabs(source_document)
    destination_tabs = collect_tabs(destination_document)

    for tab_name, source_tab_id in source_tabs.items():

        if tab_name in destination_tabs:

            mapping[source_tab_id] = (
                destination_tabs[tab_name]
            )

    return mapping

def get_tab_id_by_name(document, tab_name):
    """
    Find the Google Docs tab ID from its tab title.
    """

    for tab in document.get("tabs", []):

        properties = tab.get("tabProperties", {})

        if properties.get("title") == tab_name:
            return properties.get("tabId")

        # Check nested tabs
        child_id = get_tab_id_by_name(
            {"tabs": tab.get("childTabs", [])},
            tab_name
        )

        if child_id is not None:
            return child_id

    return None
def insert_chapter_into_document(
    service,
    document_id,
    tab_id,
    chapter,
    insert_index
):
    """
    Insert a structured chapter into a Google Docs tab while
    preserving paragraph and text-run formatting.

    Parameters
    ----------
    service : Google Docs API service
    document : destination document returned by documents.get()
    document_id : ID of destination document
    tab_id : ID of tab
    chapter : structured chapter returned by get_chapter_structured()
    insert_index : Google Docs index where the chapter should be inserted
    """

    requests = []

    current_index = insert_index

    # ---------------------------------------------------------
    # Process chapter elements
    # ---------------------------------------------------------

    for element in chapter["elements"]:

        # =====================================================
        # Paragraph / Heading
        # =====================================================

        if element["type"] in ["paragraph", "heading"]:

            paragraph_start = current_index

            # -------------------------------------------------
            # Insert each text run separately
            # -------------------------------------------------

            for run in element["runs"]:

                text = run.get("text", "")

                if not text:
                    continue

                start_index = current_index
                end_index = current_index + len(text)

                # Insert text
                requests.append({
                    "insertText": {
                        "location": {
                            "index": current_index,
                            "tabId": tab_id
                        },
                        "text": text
                    }
                })

                # -------------------------------------------------
                # Apply text formatting
                # -------------------------------------------------

                text_style = run.get(
                    "textStyle",
                    {}
                )

                if text_style:

                    requests.append({
                        "updateTextStyle": {
                            "range": {
                                "startIndex": start_index,
                                "endIndex": end_index,
                                "tabId": tab_id
                            },
                            "textStyle": text_style,
                            "fields": ",".join(
                                text_style.keys()
                            )
                        }
                    })

                current_index = end_index

            # -------------------------------------------------
            # Add paragraph newline
            # -------------------------------------------------

            requests.append({
                "insertText": {
                    "location": {
                        "index": current_index,
                        "tabId": tab_id
                    },
                    "text": "\n"
                }
            })

            current_index += 1

            paragraph_end = current_index

            # -------------------------------------------------
            # Apply paragraph formatting
            # -------------------------------------------------

            paragraph_style = element.get(
                "paragraphStyle",
                {}
            )

            if paragraph_style:

                # Don't send read-only fields back to the API
                allowed_fields = [
                    "namedStyleType",
                    "alignment",
                    "lineSpacing",
                    "direction",
                    "spacingMode",
                    "spaceAbove",
                    "spaceBelow",
                    "indentFirstLine",
                    "indentStart",
                    "indentEnd",
                    "keepLinesTogether",
                    "keepWithNext",
                    "avoidWidowAndOrphan",
                ]

                writable_style = {
                    key: value
                    for key, value in paragraph_style.items()
                    if key in allowed_fields
                }

                if writable_style:

                    requests.append({
                        "updateParagraphStyle": {
                            "range": {
                                "startIndex": paragraph_start,
                                "endIndex": paragraph_end,
                                "tabId": tab_id
                            },
                            "paragraphStyle": writable_style,
                            "fields": ",".join(
                                writable_style.keys()
                            )
                        }
                    })

        # =====================================================
        # Table
        # =====================================================

        elif element["type"] == "table":

            # Tables need to be created using insertTable.
            # The text/style of the cells then needs to be
            # inserted separately.

            rows = element["rows"]

            if not rows:
                continue

            num_rows = len(rows)
            num_columns = max(
                len(row)
                for row in rows
            )

            # Create table
            requests.append({
                "insertTable": {
                    "location": {
                        "index": current_index,
                        "tabId": tab_id
                    },
                    "rows": num_rows,
                    "columns": num_columns
                }
            })

            # -------------------------------------------------
            # IMPORTANT:
            # Google Docs assigns the internal table/cell
            # indices after the batch update.
            #
            # Therefore, cell contents cannot reliably be
            # formatted using the indices calculated here.
            # -------------------------------------------------

            raise NotImplementedError(
                "Table insertion currently requires a separate "
                "second pass after the table has been created."
            )

    # ---------------------------------------------------------
    # Execute requests
    # ---------------------------------------------------------
    print("TAB ID:", tab_id)
    print("NUMBER OF REQUESTS:", len(requests))
    print("REQUEST 35:")
    print(requests[35])
    return service.documents().batchUpdate(
        documentId=document_id,
        body={
            "requests": requests
        }
    ).execute()

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


