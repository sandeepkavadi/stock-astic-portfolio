from schwab.auth import easy_client
from src.config import get_schwab_api_credentials
from schwab.client import Client

def get_positions():
    """
    Fetches the account positions from the Schwab API.
    """
    credentials = get_schwab_api_credentials()
    if not credentials:
        print("Schwab API credentials not found. Please run scripts/authenticate_schwab.py")
        return []

    client = easy_client(
        api_key=credentials['api_key'],
        app_secret=credentials['app_secret'],
        callback_url=credentials['redirect_uri'],
        token_path="token.json"
    )

    # Get the first account
    response = client.get_account_numbers()
    if not response.is_success:
        print("Error fetching account numbers:", response.text)
        return []
    
    account_numbers = response.json()
    if not account_numbers:
        print("No accounts found.")
        return []
    
    first_account = account_numbers[0]
    account_id = first_account['hashValue']

    # Fetch positions for the first account
    response = client.get_account(account_id, fields=[Client.Account.Fields.POSITIONS])
    if not response.is_success:
        print(f"Error fetching positions for account {account_id}:", response.text)
        return []

    account_data = response.json()
    positions = account_data.get('securitiesAccount', {}).get('positions', [])
    
    # Transform positions into a simpler format
    formatted_positions = []
    for p in positions:
        formatted_positions.append({
            'symbol': p['instrument']['symbol'],
            'quantity': p['longQuantity'] if 'longQuantity' in p else p.get('shortQuantity', 0) * -1,
            'market_value': p['marketValue'],
        })
            
    return formatted_positions