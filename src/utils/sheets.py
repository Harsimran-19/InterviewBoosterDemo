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
            
            # Print keys for debugging (without exposing sensitive values)
            print(f"Credential keys found: {list(credentials_dict.keys())}")
            
            if "private_key" not in credentials_dict:
                raise ValueError(f"Missing 'private_key' in credentials. Keys found: {list(credentials_dict.keys())}")
            
            # Check private key format
            private_key = credentials_dict.get("private_key", "")
            if "..." in private_key:
                raise ValueError("Private key appears to be truncated (contains '...'). Please provide the complete private key.")
            
            if not private_key.startswith("-----BEGIN PRIVATE KEY-----"):
                print("Warning: Private key doesn't have the expected format. Attempting to fix...")
                
                # Try to fix common formatting issues
                if "PRIVATE KEY" not in private_key:
                    credentials_dict["private_key"] = f"-----BEGIN PRIVATE KEY-----\n{private_key}\n-----END PRIVATE KEY-----"
                    print("Added private key header and footer")
            
            # For Streamlit deployment, try a different approach if normal method fails
            try:
                # Use credentials from dictionary (either Streamlit secrets or local file)
                creds = Credentials.from_service_account_info(credentials_dict, scopes=scope)
            except Exception as inner_e:
                print(f"First attempt failed: {str(inner_e)}")
                
                # Try an alternative approach for Streamlit Cloud
                try:
                    import streamlit as st
                    # Try to use the raw JSON string directly if available
                    if 'google' in st.secrets and 'credentials' in st.secrets['google']:
                        raw_creds = st.secrets['google']['credentials']
                        if isinstance(raw_creds, str):
                            # Write to a temporary file and use that
                            import tempfile
                            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as temp:
                                temp.write(raw_creds)
                                temp_path = temp.name
                            
                            print(f"Using temporary credentials file: {temp_path}")
                            creds = Credentials.from_service_account_file(temp_path, scopes=scope)
                            # Clean up the temporary file
                            import os
                            os.unlink(temp_path)
                        else:
                            raise ValueError("Streamlit secrets credentials is not a string")
                    else:
                        raise ValueError("No google credentials in Streamlit secrets")
                except Exception as alt_e:
                    print(f"Alternative approach failed: {str(alt_e)}")
                    # Re-raise the original error
                    raise inner_e
            
            self.client = gspread.authorize(creds)
            print("Successfully initialized Google Sheets client")
            
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
