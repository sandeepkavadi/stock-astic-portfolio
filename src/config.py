import os
import json

def get_alpha_vantage_api_key():
    """
    Reads the Alpha Vantage API key from the .ALPHA_VANTAGE_KEY.txt file.
    """
    # Assuming the script is run from the root of the project
    api_key_file = os.path.join(os.getcwd(), '.ALPHA_VANTAGE_KEY.txt')
    if os.path.exists(api_key_file):
        with open(api_key_file, 'r') as f:
            return f.read().strip()
    return os.getenv('ALPHA_VANTAGE_API_KEY') # Fallback to environment variable

def get_schwab_api_credentials():
    """
    Reads the Schwab API credentials from the schwab_config.json file.
    """
    config_path = os.path.join(os.getcwd(), 'schwab_config.json')
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            return json.load(f)
    return None