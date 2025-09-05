from schwab.auth import easy_client
import json

def authenticate():
    """
    Guides the user through the Schwab authentication process.
    """
    print("Schwab Authentication Script")
    print("----------------------------")
    print("This script will guide you through the Schwab authentication process.")
    print("You will need your Schwab API key and secret.")
    print("\n")

    api_key = input("Enter your Schwab API Key: ")
    app_secret = input("Enter your Schwab App Secret: ")
    redirect_uri = input("Enter your Redirect URI (e.g., https://127.0.0.1): ")
    token_path = "token.json"
    config_path = "schwab_config.json"

    # Save the credentials to a config file
    with open(config_path, 'w') as f:
        json.dump({'api_key': api_key, 'app_secret': app_secret, 'redirect_uri': redirect_uri}, f)
    print(f"Credentials saved to {config_path}")

    try:
        client = easy_client(
            api_key=api_key,
            app_secret=app_secret,
            callback_url=redirect_uri,
            token_path=token_path
        )
        
        # Verify that the client is authenticated
        response = client.get_account_numbers()
        if response.is_success:
            print("\nAuthentication successful! Token saved to token.json")
            print("Successfully fetched account numbers:", response.json())
        else:
            print("\nAuthentication failed.")
            print("Error:", response.text)

    except Exception as e:
        print(f"\nAn error occurred during authentication: {e}")

if __name__ == "__main__":
    authenticate()
