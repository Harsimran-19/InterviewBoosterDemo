import gspread
import json
import os
from google.oauth2.service_account import Credentials
from typing import Dict, List

class SheetsClient:
    def __init__(self, credentials_path: str):
        from ..config.settings import settings
        import traceback
        
        scope = ['https://www.googleapis.com/auth/spreadsheets.readonly']
        
        try:
            # Get credentials from settings
            credentials_dict = settings.get_credentials_dict()
            
            if not credentials_dict:
                raise ValueError("No credentials found in Streamlit secrets or local file")
                
            if "private_key" not in credentials_dict:
                raise ValueError(f"Missing 'private_key' in credentials. Keys found: {list(credentials_dict.keys())}")
                
            # Use credentials from dictionary (either Streamlit secrets or local file)
            creds = Credentials.from_service_account_info(credentials_dict, scopes=scope)
            self.client = gspread.authorize(creds)
        except Exception as e:
            error_msg = f"Error initializing SheetsClient: {str(e)}\n{traceback.format_exc()}"
            print(error_msg)
            # Re-raise with more context
            raise RuntimeError(f"Failed to initialize Google Sheets client: {str(e)}") from e

    def get_sheet_data(self, sheet_id: str) -> List[Dict]:
        sheet = self.client.open_by_key(sheet_id)
        
        # Get raw data with possible duplicate headers
        list_of_lists = sheet.sheet1.get_all_values()
        headers = list_of_lists[0]
        data = list_of_lists[1:]

        # Make headers unique
        seen = {}
        unique_headers = []
        for h in headers:
            if h in seen:
                seen[h] += 1
                unique_h = f"{h}_{seen[h]}"
            else:
                seen[h] = 0
                unique_h = f"{h}_0" if h in unique_headers else h
            unique_headers.append(unique_h)

        # Convert to records
        return [dict(zip(unique_headers, row)) for row in data]
