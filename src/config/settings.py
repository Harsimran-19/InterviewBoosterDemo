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
                if isinstance(creds, str):
                    try:
                        return json.loads(creds)
                    except json.JSONDecodeError:
                        # If it's not valid JSON, it might be a raw string that needs cleanup
                        # Remove any extra quotes, newlines, etc.
                        creds = creds.strip().replace('\n', '\\n')
                        return json.loads(creds)
                elif isinstance(creds, dict):
                    return creds
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
