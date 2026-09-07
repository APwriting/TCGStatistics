import os
import sys
import yaml

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

#############
#Load here the path to the credentials
#TODO
#
#with open( "path_to_token.txt","r") as IN:
#   cred_path = 

cred_path = "token.json"

SCOPES = [
    "https://www.googleapis.com/auth/documents.readonly"
]


def get_google_docs_service():
    """Authenticate with Google and return the Docs API service."""

    creds = None

    if os.path.exists():
        creds = Credentials.from_authorized_user_file(
            cred_path,
            SCOPES
        )

    if not creds or not creds.valid:

        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())

        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json",
                SCOPES
            )

            creds = flow.run_local_server(port=0)

        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return build("docs", "v1", credentials=creds)


def get_document(service, document_id):

    document = service.documents().get(
        documentId=document_id
    ).execute()

    return document


def get_text_from_paragraph(paragraph):

    text = ""

    for element in paragraph.get("elements", []):

        text_run = element.get("textRun")

        if text_run:
            text += text_run.get("content", "")

    return text.rstrip("\n")


def get_paragraph_formatting(paragraph):

    formatting = {}

    for element in paragraph.get("elements", []):

        text_run = element.get("textRun")

        if not text_run:
            continue

        style = text_run.get("textStyle", {})

        if "bold" in style:
            formatting["bold"] = style["bold"]

        if "italic" in style:
            formatting["italic"] = style["italic"]

        if "underline" in style:
            formatting["underline"] = style["underline"]

        if "strikethrough" in style:
            formatting["strikethrough"] = style["strikethrough"]

        if "link" in style:
            formatting["link"] = style["link"].get("url")

    return formatting


def extract_chapter(document, chapter_title):

    body = document.get("body", {})
    content = body.get("content", [])

    chapter = []

    inside_chapter = False

    for element in content:

        paragraph = element.get("paragraph")

        if not paragraph:
            continue

        text = get_text_from_paragraph(paragraph)

        paragraph_style = paragraph.get(
            "paragraphStyle",
            {}
        )

        named_style = paragraph_style.get(
            "namedStyleType",
            ""
        )

        # Start chapter when matching heading is found
        if (
            named_style.startswith("HEADING")
            and text.strip() == chapter_title
        ):

            inside_chapter = True

            chapter.append({
                "type": "heading",
                "level": named_style.replace(
                    "HEADING_",
                    ""
                ),
                "text": text
            })

            continue

        # Stop at next heading of the same or higher level
        if inside_chapter:

            if named_style.startswith("HEADING"):

                current_level = int(
                    named_style.replace(
                        "HEADING_",
                        ""
                    )
                )

                chapter_level = 1

                for item in chapter:

                    if item["type"] == "heading":
                        chapter_level = int(item["level"])
                        break

                if current_level <= chapter_level:
                    break

            item = {
                "type": "paragraph",
                "text": text
            }

            formatting = get_paragraph_formatting(
                paragraph
            )

            if formatting:
                item["formatting"] = formatting

            # Detect lists
            if "bullet" in paragraph:

                bullet = paragraph["bullet"]

                item["type"] = "list_item"
                item["list_id"] = bullet.get("listId")
                item["nesting_level"] = bullet.get(
                    "nestingLevel",
                    0
                )

            chapter.append(item)

    return chapter


def save_yaml(chapter, filename, chapter_title):

    data = {
        "chapter": {
            "title": chapter_title,
            "content": chapter
        }
    }

    with open(
        filename,
        "w",
        encoding="utf-8"
    ) as file:

        yaml.safe_dump(
            data,
            file,
            allow_unicode=True,
            sort_keys=False
        )


def main():

    document_id = input(
        "Google Docs document ID: "
    ).strip()

    chapter_title = input(
        "Chapter heading: "
    ).strip()

    output_file = input(
        "Output YAML file [chapter.yaml]: "
    ).strip()

    if not output_file:
        output_file = "chapter.yaml"

    service = get_google_docs_service()

    print("Downloading Google Doc...")

    document = get_document(
        service,
        document_id
    )

    print(
        f"Document: {document.get('title')}"
    )

    chapter = extract_chapter(
        document,
        chapter_title
    )

    if not chapter:

        print(
            f"Could not find chapter '{chapter_title}'."
        )

        sys.exit(1)

    save_yaml(
        chapter,
        output_file,
        chapter_title
    )

    print(
        f"Chapter exported to {output_file}"
    )


if __name__ == "__main__":
    main()