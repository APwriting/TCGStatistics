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
    pass







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


