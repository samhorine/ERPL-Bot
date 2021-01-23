import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the AUTH_FILE
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

AUTH_FILE = 'auth.bin'
SECRETS_FILE = 'secret.json'

class GoogleSheets:
    """
    Represents a small custom interface to the Google Sheets API
    """
    def __init__(self, creds):
        """
        Creates a new GoogleSheets instance with the supplied credentials
        """
        self.creds = creds
        # Creates a new Google API request service
        service = build('sheets', 'v4', credentials=self.creds)
        self.sheets = service.spreadsheets()
    
    def get_values(self, sheetId, value_range):
        """
        Sends a request to Google's API to retrieve data from the given range, from the spreadsheet with the given id
        """
        # Sets up the API request
        request = self.sheets.values().get(spreadsheetId=sheetId, range=value_range)
        # Executes the API request
        result = request.execute()
        # Extracts the values from the result
        values = result.get('values', [])

        return values
    
    def set_values(self, sheetId, value_range, new_values):
        """
        Sends a request to Google's API to set the data in the given range
        """
        # Sets up the body of the request we are going to send
        body = { 'values': new_values }
        # Sets up the API request
        request = self.sheets.values().update(spreadsheetId=sheetId,
                                              range=value_range,
                                              valueInputOption='RAW',
                                              body=body)
        # Executes the API request
        _result = request.execute()
        

def retrieve_credentials():
    """
    Retrieves credentials either from the AUTH_FILE or prompts the user for new credentials
    """

    credentials = None

    # If the authentication credentials exist, then read them from the file
    if os.path.exists(AUTH_FILE):
        with open(AUTH_FILE, 'rb') as f:
            credentials = pickle.load(f)
    
    # If the credentials were not found or are invalid
    if not credentials or not credentials.valid:
        # If they can be refreshed
        if credentials and credentials.expired and credentials.refresh_token:
            # Refresh them
            credentials.refresh(Request())
        else:
            # Attempt to create new credentials with the provided scopes
            flow = InstalledAppFlow.from_client_secrets_file(SECRETS_FILE, SCOPES)
            # This prompts the user to login to their Google account and authorize this application
            credentials = flow.run_local_server(port=0)
        
        # No matter what, the credentials have been updated, so write them
        with open(AUTH_FILE, 'wb') as f:
            pickle.dump(credentials, f)
        
    return credentials
