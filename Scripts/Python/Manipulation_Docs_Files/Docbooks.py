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

######################
########################################################################################
#
#Define Script Block as meta class. Enforces rules
#
########################################################################################

def main():
    Example_text = Text.from_google_docs(example_text_data)
    print(Example_text.name)
    print(Example_text)
    Example_text.info()
    #Example_text.print_structure()
    print("Testing paragraph now \n\n\n")
    #print(example_paragraph["paragraph"])
    Example_para = Paragraph.from_google_docs(example_paragraph)
    print(Example_para)
    print("Furhter tests\n\n\n")
    print( Example_para.goto_start, Example_para.pos )
    print( Example_para.forward, Example_para.pos)
    print( Example_para.forward, Example_para.pos)
    print( Example_para.backward, Example_para.pos)
    print( Example_para.goto_end, Example_para.pos )
    print( Example_para.paragraphstyle )
    print("\n\n\nTesting Chapter now \n\n\n")
    Example_chapter = Chapter.from_google_docs_sorted(example_chapter_data)
    print(Example_chapter)
    print("Print Test succesfull.")
    print( Example_chapter.goto_start, Example_chapter.pos )
    print( Example_chapter.forward, Example_chapter.pos)
    print( Example_chapter.forward, Example_chapter.pos)
    print( Example_chapter.backward, Example_chapter.pos)
    print( Example_chapter.goto_end, Example_chapter.pos, "Should be END" )
    print( Example_chapter.backward, Example_chapter.pos)

    Paragrapg_lower_test = Example_chapter.lower
    print( Paragrapg_lower_test, type(Paragrapg_lower_test) )

    Back_to_chapter = Paragrapg_lower_test.upper
    print( Back_to_chapter, type(Back_to_chapter) )
    print("\n\n\nTesting Chapter on Google DOC like data now \n\n\n")
    Example_chapter = Chapter.from_google_docs(second_example_chapter_data)
    print(Example_chapter)
    print("Print Test succesfull.")
    print( Example_chapter.goto_start, Example_chapter.pos )
    print( Example_chapter.forward, Example_chapter.pos)
    print( Example_chapter.lower.start, Example_chapter.lower.end, "Test the positions")
    print( Example_chapter.forward, Example_chapter.pos)
    print( Example_chapter.lower.start, Example_chapter.lower.end, "Test the positions")
    print( Example_chapter.backward, Example_chapter.pos)
    print( Example_chapter.goto_end, Example_chapter.pos, "Should be END" )
    print( Example_chapter.backward, Example_chapter.pos)

    Paragrapg_lower_test = Example_chapter.lower
    print( Paragrapg_lower_test, type(Paragrapg_lower_test) )

    Back_to_chapter = Paragrapg_lower_test.upper
    print("\n\n\nTesting TAB on Google DOC like data now \n\n\n")
    Example_Tab = Tab.from_google_docs(example_tab_data)
    print(Example_Tab)
    print("Print Test succesfull.")
    print( Example_Tab.goto_start, Example_Tab.pos )
    print( Example_Tab.forward, Example_Tab.pos)
    print( Example_Tab.lower.start, Example_Tab.lower.end, "Test the positions")
    print( Example_Tab.forward, Example_Tab.pos)
    print( Example_Tab.lower.start, Example_Tab.lower.end, "Test the positions")
    print( Example_Tab.backward, Example_Tab.pos)
    print( Example_Tab.goto_end, Example_Tab.pos, "Should be END" )
    print( Example_Tab.backward, Example_Tab.pos)

    print("-------------------------------------------------------------")
    print("\n\n\nTesting DOCUMENT Class on Google DOC like data now \n\n\n")
    Example_Doc = Document.from_google_docs(Example_document_pull)
    print(Example_Doc)
    print("Print Test succesfull.")
    print( Example_Doc.goto_start, Example_Doc.pos )
    print( Example_Doc.forward, Example_Doc.pos)
    print( Example_Doc.forward, Example_Doc.pos)
    print( Example_Doc.backward, Example_Doc.pos)
    print( Example_Doc.goto_end, Example_Doc.pos, "Should be END" )
    print( Example_Doc.backward, Example_Doc.pos)


class ScriptBlock(type):

    registry = {}

    def __new__(mcls, name, bases, namespace):

        # Base class itself is exempt
        if name != "DocumentBlock":

            if "block_type" not in namespace:
                raise TypeError(
                    f"{name} must define 'block_type'."
                )

            if "allowed_children" not in namespace:
                raise TypeError(
                    f"{name} must define 'allowed_children'."
                )

        cls = super().__new__(
            mcls,
            name,
            bases,
            namespace
        )

        # Register the block
        block_type = namespace.get("block_type")

        if block_type is not None:
            mcls.registry[block_type] = cls

        return cls



class DocumentBlock(metaclass=ScriptBlock):

    def __init__(
        self,
        name=None,
        start=None,
        end=None,
        value=None
    ):
        self.name = name
        self.start = start
        self.end = end
        self.value = value

        self.chain = [self.name]
        self.pos = 0

        self.next_element = None
        self.previous_element = None
        self.upper = None
        #self.lower = None

    ###Navigating the Chain

    #Necessary to define here to give the behavious I want.
    #Upper is still statically defined. 
    @property
    def lower(self):
        return self.chain[self.pos]

    @property
    def current(self):
        return self.chain[self.pos]
    @property
    def forward(self):
        if self.pos < len(self.chain)-1:
            self.pos+=1
            return( self.current )
        else:
            return(self.current)
    @property
    def backward(self):
        if self.pos > 0 :
            self.pos-=1
            return( self.current )
        else:
            return(self.current)
    def get_last(self):
        if self.pos > 0 :
            return( self.chain[self.pos-1] )
        else:
            return( self.current )
    def get_next(self):
        if self.pos <  len(self.chain)-1:
            return( self.chain[self.pos+1] )
        else:
            return( self.current )
    @property
    def goto_start(self):
        self.pos = 0
        return self.current
    @property
    def head(self):
        return self.chain[0]

    @property
    def goto_end(self):
        self.pos = len(self.chain)-1
        return self.current
    @property
    def tail(self):
        return self.chain[len(self.chain)-1]
    #Definitions for checking start and end
    def check_start_and_end_aligned(self):
        #Checks if chain is aligned by start and end. Summary
        Position_asignment_summary = self.get_start_and_end_aligned_positions()
        return sum( Position_asignment_summary ) == len( Position_asignment_summary )

    def get_start_and_end_aligned_positions(self):
        #Checks if chain is aligned by start and end
        self.goto_start()
        self.forward()
        Elements_positions_fitting = list()
        while( self.pos < len(self.chain)):
            Next_element = self.get_next()
            Elements_positions_fitting.append( self.end == Next_element.start )
            self.forward
        return Elements_positions_fitting

    def length(self):
        #Returns the length of the element based on google docs coordintaed
        return( self.end - self.start )

    def chain_length(self):
        #Gives back chain length
        if len(self.chain)>0:
            return sum( [ element.chain_length() for element in self.chain[1:] ] )
        else:
            return len(self.value)

    def check_chain_aligned(self):
        return self.length() == self.chain_length
        

    def align_chain(self):
        if self.check_chain_aligned:
            return 1
        self.goto_start
        self.forward
        chain_start = self.current.start
        current_length = chain_start
        for element in self.chain:
            element_length = element.chain_length()
            self.end = self.start + element_length
            current_length = self.end
            self.forward
            self.start = current_length


    #Printing definitions
    def print_structure(self):
        print(f"Type: {self.block_type}")
        print(f"Name: {self.name}")
        print(f"Position: {self.start} - {self.end}")
        print(f"Value: {self.value}")
        print(f"Upper: {self.upper}")
        print(f"Lower: {self.lower}")
        print(f"Previous: {self.previous}")
        print(f"Next: {self.next}")


    def info(self):
        print(f"Type: {self.block_type}")
        print(f"Name: {self.name}")
        print(f"Position: {self.start} - {self.end}")
        print(f"Value: {self.value}")

    def _get_content(self, level=0):

        # If this block has children, recursively get their content
        if self.chain:

            output = []

            for element in self.chain[1:]:
                output.append(
                    element._get_content(level + 1)
                )

            return "\n".join(output)

        # If this is a leaf element, return its value
        return str(self.value)

    def __str__(self):
        return self._get_content()

    #Adding to the structure
    def add(self, element):
        #TODO NEEDS TO BE REWORKED

        if element.block_type not in self.allowed_children:
            raise TypeError(
                f"{self.block_type} cannot contain "
                f"{element.block_type}."
            )

        self.chain.append(element)

        return 1


class Document(DocumentBlock):
    block_type = "document"

    allowed_children = {
        "tab"
    }
    def __init__(self, documentId = None,  **kwargs):
        super().__init__(**kwargs)
        self.documentId = documentId
    @classmethod
    def from_google_docs(cls, data):
        tabs = data["tabs"]
        document = cls(
            name=data["title"],
            start=None,
            end=None
        )
        Total_Element_number = len(tabs)

        for i in range( Total_Element_number  ):
            element = tabs[i]
            tab = Tab.from_google_docs(element)


            document.add(tab)
            document.forward   #Goes to the next element in the chain, which is the last added
            if document.pos == 1:
                document.current.previous_element = "Start"
            elif document.pos == Total_Element_number-1:
                document.current.next_element = "End"
            else:
                previous = document.get_last()
                previous.next = document.current
                document.current.previous_element = previous

        document.goto_start
        document.start = document.get_next().start
        document.end = document.goto_end.end
        return(document)


class Tab(DocumentBlock):
    block_type = "tab"

    allowed_children = {
        "paragraph","chapter"
    }
    def __init__(self, index=None,tabId = "t.0",  **kwargs):
        super().__init__(**kwargs)
        self.index = index
        self.tabId = tabId
    @classmethod
    def from_google_docs(cls, data):
        #Creates chapters from the content list google gives.
        #{'tabProperties': {'tabId': 't.0', 'title': '1. Intro Parts', 'index': 0}
        tabproperties = data["tabProperties"]
        tab = cls(
            name=tabproperties["title"],
            start=None,
            end=None,
            index = tabproperties["index"],
            tabId = tabproperties["tabId"]
        )
        Elements = data["documentTab"]["body"]["content"]
        #    "documentTab": {   #Example of tab structure for elements.
        #"body": {
        #    "content": [

        Total_Element_number = len(Elements)
        saving_header = False
        New_chapter_ready = False
        part_elements = list()
        chapter = Chapter()
        for i in range( Total_Element_number  ):
            #print("TEST", i)
            element = Elements[i]
            if "paragraph" not in element:  #Exclude paragraphs for now
                continue
            paragraphstyle =  element["paragraph"].get("paragraphStyle",{}).get("namedStyleType", "NORMAL_TEXT")
            if "HEADING" in paragraphstyle:
                if saving_header or i == Total_Element_number-1 or (not saving_header and part_elements):
                    New_chapter_ready = True
                    Chapter_elements = part_elements[::]
                    part_elements = list()

                saving_header = True
                
                part_elements.append(element)
            elif saving_header:     #Redundancy needed for the future
                part_elements.append(element)
            else:
                part_elements.append(element)


            if New_chapter_ready:
                chapter = Chapter.from_google_docs(Chapter_elements)
                #part_elements = list()
                
                chapter.upper = tab
                tab.add(chapter)
                tab.forward   #Goes to the next element in the chain, which is the last added
                if tab.pos == 1:
                    tab.current.previous_element = "Start"
                elif tab.pos == Total_Element_number-1:
                    tab.current.next_element = "End"
                else:
                    previous = tab.get_last()
                    previous.next = tab.current
                    tab.current.previous_element = previous
                New_chapter_ready = False

        tab.goto_start
        tab.start = tab.get_next().start
        tab.end = tab.goto_end.end

        return tab



class Chapter(DocumentBlock):

    block_type = "chapter"

    allowed_children = {
        "paragraph"
    }
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    @classmethod
    def from_google_docs_sorted(cls, data):

        chapter = cls(
            name=data["name"],
            start=data["startIndex"],
            end=data["endIndex"]
        )
        Elements = data.get("elements", [])
        #print(Elements)
        Total_Element_number = len(Elements)
        #for element in data.get("elements", []):
        for i in range( Total_Element_number  ):
            element = Elements[i]

            if "paragraph" not in element:  #Exclude paragraphs for now
                continue

            paragraph = Paragraph.from_google_docs(element)
            paragraph.upper = chapter   #Defines the upper element.

            chapter.add(paragraph)
            chapter.forward   #Goes to the next element in the chain, which is the last added
            if chapter.pos == 1:
                chapter.current.previous_element = "Start"
            elif chapter.pos == Total_Element_number-1:
                chapter.current.next_element = "End"
            else:
                #print( "Test",paragraph )
                previous = chapter.get_last()
                #print( "Test", previous )
                previous.next = chapter.current
                chapter.current.previous_element = previous

        return chapter

    @classmethod
    def from_google_docs(cls, data):
        #Creates chapters from the content list google gives.
        assert type(data) == list
        chapter = cls(
            name=None,
            start=None,
            end=None
        )
        Heading_paragraphs = list()
        Header = None
        Header_not_saved = True
        Ongoing_Saving_Header = True
        #Adjusting code to be like other instances.
        Elements = data
        Total_Element_number = len(Elements)
        for i in range( Total_Element_number  ):
            #print("TEST", i)
            element = Elements[i]
            if "paragraph" not in element:  #Exclude paragraphs for now
                continue
            paragraph = Paragraph.from_google_docs(element)
            if Header_not_saved and "HEADING" in paragraph.paragraphstyle and Ongoing_Saving_Header:
                Heading_paragraphs.append( paragraph._get_content() )
            else:
                Header = "".join(Heading_paragraphs)
                Header_not_saved = False
                Ongoing_Saving_Header = False
            paragraph.upper = chapter   #Defines the upper element.

            chapter.add(paragraph)
            chapter.forward   #Goes to the next element in the chain, which is the last added
            if chapter.pos == 1:
                chapter.current.previous_element = "Start"
            elif chapter.pos == Total_Element_number-1:
                chapter.current.next_element = "End"
            else:
                previous = chapter.get_last()
                previous.next = chapter.current
                chapter.current.previous_element = previous
        chapter.name = Header   #Saving the Header from before
        chapter.goto_start
        chapter.start = chapter.get_next().start    #start of first elements, that is not the header
        #chapter.goto_start.get_next.start
        chapter.end = chapter.goto_end.end  #end of last element
        return chapter

        

class Paragraph(DocumentBlock):

    block_type = "paragraph"

    allowed_children = {
        "text"
    }
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.paragraphstyle = None


    @classmethod
    def from_google_docs(cls, data, paragraph_name="Paragraph"):

        paragraph_data = data["paragraph"]
        #print("To be sure",paragraph_data)
        paragraph = cls(
            name=paragraph_name,
            start=data["startIndex"],
            end=data["endIndex"]
        )

        paragraphstyle = paragraph_data.get("paragraphStyle",{}).get("namedStyleType", "NORMAL_TEXT")
        paragraph.paragraphstyle = paragraphstyle
        Elements = paragraph_data.get("elements", [])
        Total_Element_number = len(Elements)
        #for element in paragraph_data.get("elements", []):
        for i in range( Total_Element_number  ):
            element = Elements[i]

            if "textRun" not in element:
                continue
            #print(element)
            text = Text.from_google_docs(element)

            text.upper = paragraph

            paragraph.add(text) #Add text to the chain
            paragraph.forward   #Goes to the next element in the chain, which is the last added
            if paragraph.pos == 1:
                paragraph.current.previous_element = "Start"
            elif paragraph.pos == Total_Element_number-1:
                paragraph.current.next_element = "End"
            else:
                previous = paragraph.get_last()
                previous.next = paragraph.current
                paragraph.current.previous_element = previous


        return paragraph


class Text(DocumentBlock):

    block_type = "text"
    allowed_children = set()

    def __init__(self, text_style=None, **kwargs):
        super().__init__(**kwargs)
        self.text_style = text_style or {}
    
    @classmethod
    def from_google_docs(cls, data, text_name = "Text"):


        text_run = data["textRun"]

        return cls(
            name=text_name,
            start=data["startIndex"],
            end=data["endIndex"],
            value=text_run["content"],
            text_style=text_run.get("textStyle", {})
        )

    def _get_content(self, level=0):
        return(self.value)





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




if 0:
    class Chapter():


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




google_paragraph = {
    "startIndex": 10,
    "endIndex": 42,
    "paragraph": {
        "paragraphStyle": {
            "namedStyleType": "NORMAL_TEXT"
        },
        "elements": [
            {
                "startIndex": 10,
                "endIndex": 25,
                "textRun": {
                    "content": "This is some text",
                    "textStyle": {}
                }
            },
            {
                "startIndex": 25,
                "endIndex": 42,
                "textRun": {
                    "content": " in Google Docs.\n",
                    "textStyle": {}
                }
            }
        ]
    }
}

example_text_data = {
    "startIndex": 10,
    "endIndex": 95,
    "textRun": {
        "content": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.\n",
        "textStyle": {
            "bold": True,
            "italic": False,
            "underline": False,
            "fontSize": {
                "magnitude": 12,
                "unit": "PT"
            },
            "foregroundColor": {
                "color": {
                    "rgbColor": {
                        "red": 0.2,
                        "green": 0.3,
                        "blue": 0.8
                    }
                }
            }
        }
    }
}

example_paragraph = {
    "startIndex": 10,
    "endIndex": 115,
    "paragraph": {
        "paragraphStyle": {
            "namedStyleType": "NORMAL_TEXT"
        },
        "elements": [
            {
                "startIndex": 10,
                "endIndex": 23,
                "textRun": {
                    "content": "Lorem ipsum ",
                    "textStyle": {
                        "bold": True
                    }
                }
            },
            {
                "startIndex": 23,
                "endIndex": 42,
                "textRun": {
                    "content": "dolor sit amet, ",
                    "textStyle": {
                        "italic": True
                    }
                }
            },
            {
                "startIndex": 42,
                "endIndex": 76,
                "textRun": {
                    "content": "consectetur adipiscing elit. ",
                    "textStyle": {
                        "underline": True
                    }
                }
            },
            {
                "startIndex": 76,
                "endIndex": 115,
                "textRun": {
                    "content": "Sed do eiusmod tempor incididunt.\n",
                    "textStyle": {}
                }
            }
        ]
    }
}

example_chapter_data = {
    "name": "Example Chapter",
    "startIndex": 1,
    "endIndex": 250,
    "elements": [
        {
            "startIndex": 1,
            "endIndex": 70,
            "paragraph": {
                "elements": [
                    {
                        "startIndex": 1,
                        "endIndex": 35,
                        "textRun": {
                            "content": "Lorem ipsum dolor sit amet, ",
                            "textStyle": {
                                "bold": True
                            }
                        }
                    },
                    {
                        "startIndex": 35,
                        "endIndex": 70,
                        "textRun": {
                            "content": "consectetur adipiscing elit.\n",
                            "textStyle": {}
                        }
                    }
                ]
            }
        },
        {
            "startIndex": 70,
            "endIndex": 140,
            "paragraph": {
                "elements": [
                    {
                        "startIndex": 70,
                        "endIndex": 140,
                        "textRun": {
                            "content": "Sed do eiusmod tempor incididunt ut labore.\n",
                            "textStyle": {
                                "italic": True
                            }
                        }
                    }
                ]
            }
        }
    ]
}

tab_data = {
    "tabProperties": {
        "tabId": "t.0",
        "title": "1. Intro Parts",
        "index": 0,
        "nestingLevel": 0,
        "isLocked": False
    },

    "documentTab": {
        "body": {
            "content": [
                {
                    "startIndex": 0,
                    "endIndex": 31,
                    "sectionBreak": {
                        "sectionStyle": {}
                    }
                },
                {
                    "startIndex": 31,
                    "endIndex": 60,
                    "paragraph": {
                        "elements": [
                            {
                                "startIndex": 31,
                                "endIndex": 45,
                                "textRun": {
                                    "content": "My first paragraph.\n",
                                    "textStyle": {}
                                }
                            },
                            {
                                "startIndex": 45,
                                "endIndex": 60,
                                "textRun": {
                                    "content": "More text here.\n",
                                    "textStyle": {
                                        "bold": True
                                    }
                                }
                            }
                        ],
                        "paragraphStyle": {
                            "namedStyleType": "NORMAL_TEXT"
                        }
                    }
                },
                {
                    "startIndex": 60,
                    "endIndex": 100,
                    "paragraph": {
                        "elements": [
                            {
                                "startIndex": 60,
                                "endIndex": 100,
                                "textRun": {
                                    "content": "1. General Stuff\n",
                                    "textStyle": {}
                                }
                            }
                        ],
                        "paragraphStyle": {
                            "namedStyleType": "HEADING_1"
                        }
                    }
                }
            ]
        }
    }
}

second_example_chapter_data = [

                # Chapter 1
                {
                    "startIndex": 1,
                    "endIndex": 31,
                    "paragraph": {
                        "elements": [
                            {
                                "startIndex": 1,
                                "endIndex": 31,
                                "textRun": {
                                    "content": "Commander Deck Building Bible\n",
                                    "textStyle": {}
                                }
                            }
                        ],
                        "paragraphStyle": {
                            "namedStyleType": "HEADING_1"
                        }
                    }
                },

                # Paragraph inside Chapter 1
                {
                    "startIndex": 31,
                    "endIndex": 150,
                    "paragraph": {
                        "elements": [
                            {
                                "startIndex": 31,
                                "endIndex": 150,
                                "textRun": {
                                    "content": "This section explains the general principles of Commander deck building.\n",
                                    "textStyle": {}
                                }
                            }
                        ],
                        "paragraphStyle": {
                            "namedStyleType": "NORMAL_TEXT"
                        }
                    }
                },

                # Paragraph inside Chapter 1
                {
                    "startIndex": 150,
                    "endIndex": 280,
                    "paragraph": {
                        "elements": [
                            {
                                "startIndex": 150,
                                "endIndex": 280,
                                "textRun": {
                                    "content": "There are several important concepts to understand before building a deck.\n",
                                    "textStyle": {}
                                }
                            }
                        ],
                        "paragraphStyle": {
                            "namedStyleType": "NORMAL_TEXT"
                        }
                    }
                }
]

example_tab_data = {
    "tabProperties": {
        "tabId": "t.0",
        "title": "1. Intro Parts",
        "index": 0
    },

    "documentTab": {
        "body": {
            "content": [

                # Chapter 1
                {
                    "startIndex": 1,
                    "endIndex": 31,
                    "paragraph": {
                        "elements": [
                            {
                                "startIndex": 1,
                                "endIndex": 31,
                                "textRun": {
                                    "content": "Commander Deck Building Bible\n",
                                    "textStyle": {}
                                }
                            }
                        ],
                        "paragraphStyle": {
                            "namedStyleType": "HEADING_1"
                        }
                    }
                },

                # Paragraph inside Chapter 1
                {
                    "startIndex": 31,
                    "endIndex": 150,
                    "paragraph": {
                        "elements": [
                            {
                                "startIndex": 31,
                                "endIndex": 150,
                                "textRun": {
                                    "content": "This section explains the general principles of Commander deck building.\n",
                                    "textStyle": {}
                                }
                            }
                        ],
                        "paragraphStyle": {
                            "namedStyleType": "NORMAL_TEXT"
                        }
                    }
                },

                # Paragraph inside Chapter 1
                {
                    "startIndex": 150,
                    "endIndex": 280,
                    "paragraph": {
                        "elements": [
                            {
                                "startIndex": 150,
                                "endIndex": 280,
                                "textRun": {
                                    "content": "There are several important concepts to understand before building a deck.\n",
                                    "textStyle": {}
                                }
                            }
                        ],
                        "paragraphStyle": {
                            "namedStyleType": "NORMAL_TEXT"
                        }
                    }
                },

                # Chapter 2
                {
                    "startIndex": 280,
                    "endIndex": 330,
                    "paragraph": {
                        "elements": [
                            {
                                "startIndex": 280,
                                "endIndex": 330,
                                "textRun": {
                                    "content": "1. General Stuff\n",
                                    "textStyle": {}
                                }
                            }
                        ],
                        "paragraphStyle": {
                            "namedStyleType": "HEADING_1"
                        }
                    }
                },

                # Paragraph inside Chapter 2
                {
                    "startIndex": 330,
                    "endIndex": 450,
                    "paragraph": {
                        "elements": [
                            {
                                "startIndex": 330,
                                "endIndex": 450,
                                "textRun": {
                                    "content": "General information about the construction of a Commander deck.\n",
                                    "textStyle": {}
                                }
                            }
                        ],
                        "paragraphStyle": {
                            "namedStyleType": "NORMAL_TEXT"
                        }
                    }
                },

                # Chapter 3
                {
                    "startIndex": 450,
                    "endIndex": 510,
                    "paragraph": {
                        "elements": [
                            {
                                "startIndex": 450,
                                "endIndex": 510,
                                "textRun": {
                                    "content": "1.1. How to use this guide\n",
                                    "textStyle": {}
                                }
                            }
                        ],
                        "paragraphStyle": {
                            "namedStyleType": "HEADING_2"
                        }
                    }
                },

                # Paragraph inside Chapter 3
                {
                    "startIndex": 510,
                    "endIndex": 650,
                    "paragraph": {
                        "elements": [
                            {
                                "startIndex": 510,
                                "endIndex": 650,
                                "textRun": {
                                    "content": "This guide can be used as a reference when constructing or analysing a deck.\n",
                                    "textStyle": {}
                                }
                            }
                        ],
                        "paragraphStyle": {
                            "namedStyleType": "NORMAL_TEXT"
                        }
                    }
                }
            ]
        }
    }
}

Example_document_pull = {'title': 'Commander deck building guide', 
                         'revisionId': 'ANLCKQnHDtX9M27O2VjbkZHtR3aNf2P5B_fcer1jI_rkBwKYE6bFHEtWpZMKixh7X_wYG07GCiXH4UjiIE-ySDpCqJ', 
                         'suggestionsViewMode': 'SUGGESTIONS_INLINE', 
                         'documentId': '1NqFswFlo4GzQWm7jQnHdfdE5XQMJhsadftsgUEKbMUiM07w', 
                         'tabs': [
        # ============================================================
        # TAB 1
        # ============================================================
        {
            "tabProperties": {
                "tabId": "t.0",
                "title": "1. Intro Parts",
                "index": 0
            },
            "documentTab": {
                "body": {
                    "content": [

                        # Chapter / Heading
                        {
                            "startIndex": 1,
                            "endIndex": 35,
                            "paragraph": {
                                "elements": [
                                    {
                                        "startIndex": 1,
                                        "endIndex": 35,
                                        "textRun": {
                                            "content": "Commander Deck Building Bible\n",
                                            "textStyle": {}
                                        }
                                    }
                                ],
                                "paragraphStyle": {
                                    "namedStyleType": "HEADING_1"
                                }
                            }
                        },

                        # Paragraph
                        {
                            "startIndex": 35,
                            "endIndex": 120,
                            "paragraph": {
                                "elements": [
                                    {
                                        "startIndex": 35,
                                        "endIndex": 120,
                                        "textRun": {
                                            "content": "This guide explains the basic principles of Commander deck building.\n",
                                            "textStyle": {}
                                        }
                                    }
                                ],
                                "paragraphStyle": {
                                    "namedStyleType": "NORMAL_TEXT"
                                }
                            }
                        },

                        # Chapter / Heading
                        {
                            "startIndex": 120,
                            "endIndex": 150,
                            "paragraph": {
                                "elements": [
                                    {
                                        "startIndex": 120,
                                        "endIndex": 150,
                                        "textRun": {
                                            "content": "1. General Stuff\n",
                                            "textStyle": {
                                                "bold": True
                                            }
                                        }
                                    }
                                ],
                                "paragraphStyle": {
                                    "namedStyleType": "HEADING_1"
                                }
                            }
                        },

                        # Paragraph
                        {
                            "startIndex": 150,
                            "endIndex": 240,
                            "paragraph": {
                                "elements": [
                                    {
                                        "startIndex": 150,
                                        "endIndex": 240,
                                        "textRun": {
                                            "content": "There are several important concepts to understand before building a deck.\n",
                                            "textStyle": {}
                                        }
                                    }
                                ],
                                "paragraphStyle": {
                                    "namedStyleType": "NORMAL_TEXT"
                                }
                            }
                        }
                    ]
                }
            }
        },

        # ============================================================
        # TAB 2
        # ============================================================
        {
            "tabProperties": {
                "tabId": "t.esursc3mx121",
                "title": "2-3. The Basics and History",
                "index": 1
            },
            "documentTab": {
                "body": {
                    "content": [

                        # Chapter
                        {
                            "startIndex": 1,
                            "endIndex": 70,
                            "paragraph": {
                                "elements": [
                                    {
                                        "startIndex": 1,
                                        "endIndex": 70,
                                        "textRun": {
                                            "content": "2. The Basics of Commander Deckbuilding\n",
                                            "textStyle": {}
                                        }
                                    }
                                ],
                                "paragraphStyle": {
                                    "namedStyleType": "HEADING_1"
                                }
                            }
                        },

                        # Paragraph
                        {
                            "startIndex": 70,
                            "endIndex": 180,
                            "paragraph": {
                                "elements": [
                                    {
                                        "startIndex": 70,
                                        "endIndex": 180,
                                        "textRun": {
                                            "content": "Commander is a multiplayer format with a unique deck construction system.\n",
                                            "textStyle": {}
                                        }
                                    }
                                ],
                                "paragraphStyle": {
                                    "namedStyleType": "NORMAL_TEXT"
                                }
                            }
                        },

                        # Subchapter
                        {
                            "startIndex": 180,
                            "endIndex": 230,
                            "paragraph": {
                                "elements": [
                                    {
                                        "startIndex": 180,
                                        "endIndex": 230,
                                        "textRun": {
                                            "content": "2.1. What is a Commander?\n",
                                            "textStyle": {}
                                        }
                                    }
                                ],
                                "paragraphStyle": {
                                    "namedStyleType": "HEADING_2"
                                }
                            }
                        },

                        # Paragraph
                        {
                            "startIndex": 230,
                            "endIndex": 340,
                            "paragraph": {
                                "elements": [
                                    {
                                        "startIndex": 230,
                                        "endIndex": 340,
                                        "textRun": {
                                            "content": "The commander determines the colour identity and often the strategy of the deck.\n",
                                            "textStyle": {}
                                        }
                                    }
                                ],
                                "paragraphStyle": {
                                    "namedStyleType": "NORMAL_TEXT"
                                }
                            }
                        }
                    ]
                }
            }
        },

        # ============================================================
        # TAB 3
        # ============================================================
        {
            "tabProperties": {
                "tabId": "t.xyz789",
                "title": "4. Mana",
                "index": 2
            },
            "documentTab": {
                "body": {
                    "content": [

                        # Chapter
                        {
                            "startIndex": 1,
                            "endIndex": 25,
                            "paragraph": {
                                "elements": [
                                    {
                                        "startIndex": 1,
                                        "endIndex": 25,
                                        "textRun": {
                                            "content": "4. Mana\n",
                                            "textStyle": {}
                                        }
                                    }
                                ],
                                "paragraphStyle": {
                                    "namedStyleType": "HEADING_1"
                                }
                            }
                        },

                        # Paragraph
                        {
                            "startIndex": 25,
                            "endIndex": 100,
                            "paragraph": {
                                "elements": [
                                    {
                                        "startIndex": 25,
                                        "endIndex": 100,
                                        "textRun": {
                                            "content": "Mana is one of the most important resources when constructing a deck.\n",
                                            "textStyle": {}
                                        }
                                    }
                                ],
                                "paragraphStyle": {
                                    "namedStyleType": "NORMAL_TEXT"
                                }
                            }
                        },

                        # Subchapter
                        {
                            "startIndex": 100,
                            "endIndex": 140,
                            "paragraph": {
                                "elements": [
                                    {
                                        "startIndex": 100,
                                        "endIndex": 140,
                                        "textRun": {
                                            "content": "4.1. Lands\n",
                                            "textStyle": {}
                                        }
                                    }
                                ],
                                "paragraphStyle": {
                                    "namedStyleType": "HEADING_2"
                                }
                            }
                        },

                        # Paragraph with two text runs
                        {
                            "startIndex": 140,
                            "endIndex": 260,
                            "paragraph": {
                                "elements": [
                                    {
                                        "startIndex": 140,
                                        "endIndex": 200,
                                        "textRun": {
                                            "content": "A typical deck contains ",
                                            "textStyle": {}
                                        }
                                    },
                                    {
                                        "startIndex": 200,
                                        "endIndex": 260,
                                        "textRun": {
                                            "content": "around 35–40 lands.\n",
                                            "textStyle": {
                                                "bold": True
                                            }
                                        }
                                    }
                                ],
                                "paragraphStyle": {
                                    "namedStyleType": "NORMAL_TEXT"
                                }
                            }
                        }
                    ]
                }
            }
        }
    ]
}


#Main call
if __name__ == "__main__":
    main()










































    