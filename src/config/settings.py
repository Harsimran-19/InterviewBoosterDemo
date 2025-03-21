from pydantic_settings import BaseSettings, SettingsConfigDict
import os
import json
from pathlib import Path

class Settings(BaseSettings):
    DEEPSEEK_API_KEY: str
    SHEET_IDS: str
    CREDENTIALS_PATH: str = 'credentials.json'
    
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8'
    )
    
    def get_credentials_dict(self):
        """
        Get credentials as a dictionary, either from Streamlit secrets or from file
        """
        try:
            # Try to get credentials from Streamlit secrets
            import streamlit as st
            if 'google' in st.secrets and 'credentials' in st.secrets['google']:
                # The credentials in Streamlit secrets might be a JSON string or already parsed
                creds = st.secrets['google']['credentials']
                
                # If it's a string, try to parse it as JSON
                if isinstance(creds, str):
                    try:
                        creds_dict = json.loads(creds)
                    except json.JSONDecodeError:
                        # If it's not valid JSON, it might be a raw string that needs cleanup
                        creds = creds.strip().replace('\n', '\\n')
                        try:
                            creds_dict = json.loads(creds)
                        except json.JSONDecodeError:
                            print("Failed to parse credentials string as JSON")
                            return {}
                elif isinstance(creds, dict):
                    creds_dict = creds
                else:
                    print(f"Unexpected credentials type: {type(creds)}")
                    return {}
                
                # Check if private_key is truncated (contains "...")
                if "private_key" in creds_dict and "..." in creds_dict["private_key"]:
                    print("Warning: private_key appears to be truncated. This will cause authentication errors.")
                    
                # Ensure private_key is properly formatted
                if "private_key" in creds_dict and not creds_dict["private_key"].startswith("-----BEGIN PRIVATE KEY-----"):
                    # Try to fix the format if it's missing the header/footer
                    if "PRIVATE KEY" not in creds_dict["private_key"]:
                        creds_dict["private_key"] = f"-----BEGIN PRIVATE KEY-----\n{creds_dict['private_key']}\n-----END PRIVATE KEY-----"
                
                return creds_dict
        except (ImportError, KeyError, json.JSONDecodeError) as e:
            print(f"Error accessing Streamlit secrets: {e}")
            pass
        
        # Fall back to file-based credentials if running locally
        creds_path = Path(self.CREDENTIALS_PATH)
        if creds_path.exists():
            try:
                with open(creds_path, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError as e:
                print(f"Error loading credentials from file: {e}")
        
        # If no credentials found, return empty dict
        return {}

# Singleton instance
settings = Settings()
