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
                return json.loads(st.secrets['google']['credentials'])
        except (ImportError, KeyError):
            pass
        
        # Fall back to file-based credentials if running locally
        creds_path = Path(self.CREDENTIALS_PATH)
        if creds_path.exists():
            with open(creds_path, 'r') as f:
                return json.load(f)
        
        # If no credentials found, return empty dict
        return {}

# Singleton instance
settings = Settings()
