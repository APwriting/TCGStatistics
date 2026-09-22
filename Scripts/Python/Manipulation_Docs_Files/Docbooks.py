import os
import sys
import yaml
import json
import copy


from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


from pathlib import Path

import pandas as pd



SCOPES = [
    "https://www.googleapis.com/auth/documents.readonly"
]

SCOPES = [
    "https://www.googleapis.com/auth/documents"
]






########################################################################################
#Class
#Will be defined here first and later moved out
class Docbook:
    """
    Represents a collection of Google Docs documents and their
    tab/chapter structure.

    The metadata is stored internally as a pandas DataFrame.
    Google Docs document data can additionally be loaded into
    the object using load_document().
    """

    COLUMNS = [
        "Doc_ID",
        "tabID",
        "Tab_title",
        "Tab_index",
        "Header_level",
        "Header_title",
        "Start",
        "End",
        "Header_numbering",
        "Header_tab_block_number",
        "Chapter"
    ]

    def __init__(self, file_path=None):
        """
        Create a Docbook.

        Parameters
        ----------
        file_path : str or Path, optional
            Path to the tab-separated metadata file.
        """

        self.data = pd.DataFrame(columns=self.COLUMNS)

        # Actual Google Docs data
        self.documents = {}



        if file_path is not None:
            self.read_file(file_path)

    # =========================================================
    # Metadata
    # =========================================================

    def read_file(self, file_path):
        """
        Read the Docbook metadata file.

        The file is expected to be tab-separated.
        """

        self.data = pd.read_csv(
            file_path,
            sep="\t",
            dtype={
                "Doc_ID": str,
                "tabID": str,
                "Tab_title": str,
                "Tab_index": int,
                "Header_level": int,
                "Header_title": str,
                "Start": int,
                "End": int,
                "Header_numbering": str,
                "Header_tab_block_number": int,
            },
            keep_default_na=False,
        )

        return self

    def copy(self):
        return copy.deepcopy(self)


    def add_document(self, doc_id, document):
        """
        Add a Google Docs API document response to the Docbook.
        """

        self.documents[doc_id] = document


    def get_document(self, doc_id):
        """
        Return a loaded Google Docs document.
        """

        if doc_id not in self.documents:
            raise KeyError(
                f"Document '{doc_id}' has not been loaded."
            )

        return self.documents[doc_id]



    def digest_chapters(self, doc_id):
        """
        Extract all chapters from all tabs of a loaded Google Docs document.

        The resulting chapters are stored in:

            self.chapters[doc_id][tab_title][chapter_name]

        Each chapter contains the structured result returned by
        get_chapter_structured().

        The corresponding structured chapter is also stored in
        the DataFrame in the 'Chapter' column.
        """

        # ---------------------------------------------------------
        # Check document
        # ---------------------------------------------------------

        if doc_id not in self.documents:
            raise KeyError(
                f"Document '{doc_id}' has not been added."
            )

        document = self.documents[doc_id]

        # ---------------------------------------------------------
        # Create Chapter column if necessary
        # ---------------------------------------------------------

        if "Chapter" not in self.data.columns:
            self.data["Chapter"] = None

        # ---------------------------------------------------------
        # Create document entry
        # ---------------------------------------------------------

        if not hasattr(self, "chapters"):
            self.chapters = {}

        self.chapters[doc_id] = {}

        # ---------------------------------------------------------
        # Go through all tabs
        # ---------------------------------------------------------

        for tab in document.get("tabs", []):

            tab_properties = tab.get(
                "tabProperties",
                {}
            )

            tab_id = tab_properties.get("tabId")
            tab_title = tab_properties.get("title")

            # Create dictionary for this tab
            self.chapters[doc_id][tab_title] = {}

            # -----------------------------------------------------
            # Find chapters belonging to this tab in DataFrame
            # -----------------------------------------------------

            tab_rows = self.data[
                (self.data["Doc_ID"] == doc_id)
                &
                (self.data["tabID"] == tab_id)
            ]

            # -----------------------------------------------------
            # Digest every chapter
            # -----------------------------------------------------

            for row_index, row in tab_rows.iterrows():

                chapter_name = row["Header_title"]
                chapter_level = row["Header_level"]

                chapter = get_chapter_structured(
                    tab=tab,
                    chapter_name=chapter_name,
                    chapter_level=chapter_level
                )

                # Store in nested dictionary
                self.chapters[
                    doc_id
                ][
                    tab_title
                ][
                    chapter_name
                ] = chapter

                # Store same object in DataFrame
                self.data.at[
                    row_index,
                    "Chapter"
                ] = chapter

        return self.chapters[doc_id]





    # =========================================================
    # Tabs
    # =========================================================

    def get_tabs(self, doc_id):
        """
        Return all tabs belonging to a document.
        """

        document = self.get_document(doc_id)

        return document.get("tabs", [])

    def get_tab(self, doc_id, tab):
        """
        Return one document tab.

        'tab' can be:
            - tab ID
            - tab title
            - tab index
        """

        tabs = self.get_tabs(doc_id)

        # ---------------------------------------------
        # Search by tab ID
        # ---------------------------------------------

        for current_tab in tabs:

            properties = current_tab.get(
                "tabProperties", {}
            )

            if properties.get("tabId") == tab:
                return current_tab

        # ---------------------------------------------
        # Search by title
        # ---------------------------------------------

        for current_tab in tabs:

            properties = current_tab.get(
                "tabProperties", {}
            )

            if properties.get("title") == tab:
                return current_tab

        # ---------------------------------------------
        # Search by index
        # ---------------------------------------------

        if isinstance(tab, int):

            if 0 <= tab < len(tabs):
                return tabs[tab]

        raise KeyError(
            f"Tab '{tab}' not found in document '{doc_id}'."
        )

    # =========================================================
    # Chapters from digest
    # =========================================================

    def get_chapters(self, doc_id, tab = None):
        """
        Return all digested chapters belonging to a tab.

        Parameters
        ----------
        doc_id : str
            Google Docs document ID.
        tab : str or int
            Tab title, tab ID, or tab index.

        Returns
        -------
        dict
            Dictionary with chapter names as keys and structured
            chapter data as values.
        """


        if doc_id not in self.chapters:
            raise KeyError(
                f"Document '{doc_id}' has not been digested yet. Use function 'digest_chapters'. "
            )

        # Resolve the actual tab
        current_tab = self.get_tab(
            doc_id,
            tab
        )

        tab_properties = current_tab.get(
            "tabProperties",
            {}
        )

        tab_title = tab_properties.get("title")

        if tab_title not in self.chapters[doc_id]:
            raise KeyError(
                f"Tab '{tab_title}' has not been digested."
            )

        return self.chapters[doc_id][tab_title]


    # =========================================================
    # Tabs from Chapter name
    # =========================================================

    def get_tabs_of_chapter(self, chapter_name):
        """
        Return all documents and tabs containing a chapter.

        Parameters
        ----------
        chapter_name : str
            Name of the chapter to search for.

        Returns
        -------
        list or False
            List of dictionaries containing Doc_ID and tab information,
            or False if the chapter does not exist.
        """

        results = dict()

        for doc_id, tabs in self.chapters.items():

            for tab_title, chapters in tabs.items():

                if chapter_name in chapters:

                    # Get the actual tab to obtain its tabID
                    current_tab = self.get_tab(
                        doc_id,
                        tab_title
                    )

                    tab_properties = current_tab.get(
                        "tabProperties",
                        {}
                    )

                    results[doc_id] = {
                        "Doc_ID": doc_id,
                        "tabID": tab_properties.get("tabId"),
                        "tab_title": tab_title,
                        "tab":current_tab
                        }
                    

        if not results:
            return False

        return results


    # =========================================================
    # Single chapter
    # =========================================================

    def get_chapter(
        self,
        doc_id,
        chapter_name,tab=None
    ):
        """
        Return a single digested chapter from a Google Docs tab.

        Parameters
        ----------
        doc_id : str
            Google Docs document ID.
        tab : str or int
            Tab title, tab ID, or tab index.
        chapter_name : str
            Name of the chapter.

        Returns
        -------
        dict
            Structured chapter data.
        """

        #TODO Can stream line this funciton depending on state of the function and object

        if not tab:
            tab = self.get_tabs_of_chapter(chapter_name)
            #print(tab)
            #sys.exit("!!!!!!!!!!!!!!!")
            if not tab:
                try:
                    raise KeyError(
                        f"Document '{doc_id}' has the searched chapter not present. "
                    )
                except:
                    return None
            else:
                tab = tab.get(doc_id)["tab"]

        chapters = self.get_chapters(
            doc_id,
            tab
        )

        if chapter_name not in chapters:
            raise KeyError(
                f"Chapter '{chapter_name}' not found in tab."
            )

        return chapters[chapter_name]




    def load_document(self, service, doc_id):
        """
        Retrieve a Google Docs document through the Docs API
        and store it in this Docbook.
        """

        document = service.documents().get(
            documentId=doc_id,
            includeTabsContent=True
        ).execute()

        self.documents[doc_id] = document

        return document

def get_chapter_structured(
    tab,
    chapter_name,
    chapter_level=1
):

    content = tab["documentTab"]["body"]["content"]

    # ---------------------------------------------------------
    # Find chapter
    # ---------------------------------------------------------

    chapter_start = None

    for i, element in enumerate(content):

        if "paragraph" not in element:
            continue

        paragraph = element["paragraph"]

        style = paragraph.get(
            "paragraphStyle",
            {}
        ).get(
            "namedStyleType"
        )

        if style != f"HEADING_{chapter_level}":
            continue

        text = ""

        for part in paragraph.get(
            "elements",
            []
        ):

            if "textRun" in part:

                text += part[
                    "textRun"
                ].get(
                    "content",
                    ""
                )

        if text.strip() == chapter_name:

            chapter_start = i
            break

    if chapter_start is None:

        print(
            f"Chapter '{chapter_name}' not found."
        )

        return None

    # ---------------------------------------------------------
    # Find next heading of same level
    # ---------------------------------------------------------

    chapter_end = len(content)

    for i in range(
        chapter_start + 1,
        len(content)
    ):

        if "paragraph" not in content[i]:
            continue

        paragraph = content[i]["paragraph"]

        style = paragraph.get(
            "paragraphStyle",
            {}
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

    for element in content[
        chapter_start:chapter_end
    ]:

        # =====================================================
        # Paragraph
        # =====================================================

        if "paragraph" in element:

            paragraph = element["paragraph"]

            paragraph_style = paragraph.get(
                "paragraphStyle",
                {}
            ).copy()

            named_style = paragraph_style.get(
                "namedStyleType"
            )

            runs = []

            for part in paragraph.get(
                "elements",
                []
            ):

                if "textRun" not in part:
                    continue

                text_run = part["textRun"]

                runs.append({
                    "text": text_run.get(
                        "content",
                        ""
                    ),
                    "textStyle": text_run.get(
                        "textStyle",
                        {}
                    ).copy()
                })

            text = "".join(
                run["text"]
                for run in runs
            ).rstrip("\n")

            if (
                named_style
                and named_style.startswith(
                    "HEADING_"
                )
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
                "tableRows",
                []
            ):

                row_data = []

                for cell in row.get(
                    "tableCells",
                    []
                ):

                    cell_data = []

                    for cell_element in cell.get(
                        "content",
                        []
                    ):

                        if "paragraph" not in cell_element:
                            continue

                        paragraph = cell_element[
                            "paragraph"
                        ]

                        paragraph_style = paragraph.get(
                            "paragraphStyle",
                            {}
                        ).copy()

                        runs = []

                        for part in paragraph.get(
                            "elements",
                            []
                        ):

                            if "textRun" not in part:
                                continue

                            text_run = part["textRun"]

                            runs.append({
                                "text": text_run.get(
                                    "content",
                                    ""
                                ),
                                "textStyle": text_run.get(
                                    "textStyle",
                                    {}
                                ).copy()
                            })

                        cell_data.append({
                            "paragraphStyle":
                                paragraph_style,
                            "runs":
                                runs
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





class Chapter()


    def __init__(self, file_path=None):
        """
        Create a Docbook.

        Parameters
        ----------
        file_path : str or Path, optional
            Path to the tab-separated metadata file.
        """

        self.data = pd.DataFrame(columns=self.COLUMNS)

        # Actual Google Docs data
        self.documents = {}





def get_raw_chapters_from_tab(self, doc_id, tab):
    """
    Extract the raw Google Docs API content belonging to each chapter
    in a tab.

    Parameters
    ----------
    doc_id : str
        Google Docs document ID.
    tab : str or int
        Tab title, tab ID, or tab index.

    Returns
    -------
    dict
        Dictionary with chapter names as keys and their raw Google
        Docs API content as values.
    """

    current_tab = self.get_tab(
        doc_id,
        tab
    )

    content = current_tab["documentTab"]["body"]["content"]

    chapters = {}

    # Get chapter metadata for this tab
    chapter_metadata = self.get_chapters(
        doc_id,
        tab
    )

    for chapter_name, chapter_data in chapter_metadata.items():

        # Find the start and end indices from the digested chapter
        start_index = None
        end_index = None

        for element in content:

            if (
                "paragraph" in element
                and element["paragraph"]
                .get("paragraphStyle", {})
                .get("namedStyleType", "")
                .startswith("HEADING_")
            ):

                text = ""

                for run in element["paragraph"].get("elements", []):
                    if "textRun" in run:
                        text += run["textRun"].get("content", "")

                if text.rstrip("\n") == chapter_name:
                    start_index = element["startIndex"]
                    break

        if start_index is None:
            continue

        # Find the next heading of the same or higher level
        chapter_level = chapter_data.get(
            "chapter_level",
            1
        )

        for element in content:

            if element["startIndex"] <= start_index:
                continue

            if "paragraph" not in element:
                continue

            style = element["paragraph"].get(
                "paragraphStyle",
                {}
            ).get(
                "namedStyleType",
                ""
            )

            if not style.startswith("HEADING_"):
                continue

            level = int(style.split("_")[1])

            if level <= chapter_level:
                end_index = element["startIndex"]
                break

        if end_index is None:
            end_index = content[-1]["endIndex"]

        # Extract the actual API elements
        chapter_elements = [
            element
            for element in content
            if (
                element["startIndex"] >= start_index
                and element["endIndex"] <= end_index
            )
        ]

        chapters[chapter_name] = {
            "startIndex": start_index,
            "endIndex": end_index,
            "elements": chapter_elements
        }

    return chapters




    