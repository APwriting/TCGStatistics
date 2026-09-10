import os
import sys
import yaml

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build



SCOPES = [
    "https://www.googleapis.com/auth/documents.readonly"
]


#Goes over specified Chapters
#Loads tabs and position in Chapter
#Looks up text in the chapters
#Find all texts marked by {}, these are supposed to be Magic cards
#Finds link for these cards on Scryfall
#Establishes link for cards.

def main():
    pass







########
#Functions


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


