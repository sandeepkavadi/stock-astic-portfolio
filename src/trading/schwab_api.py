from schwab.auth import easy_client
from src.config import get_schwab_api_credentials
from schwab.client import Client
from datetime import datetime, timedelta, date # Import date
import json
import os

SCHWAB_CACHE_DIR = 'schwab_cache'

def _get_schwab_client():
    credentials = get_schwab_api_credentials()
    if not credentials:
        print("Schwab API credentials not found. Please run scripts/authenticate_schwab.py")
        return None

    client = easy_client(
        api_key=credentials['api_key'],
        app_secret=credentials['app_secret'],
        callback_url=credentials['redirect_uri'],
        token_path="token.json"
    )
    return client

def get_positions():
    """
    Fetches the account positions from the Schwab API, with caching.
    """
    if not os.path.exists(SCHWAB_CACHE_DIR):
        os.makedirs(SCHWAB_CACHE_DIR)

    cache_file = os.path.join(SCHWAB_CACHE_DIR, 'positions.json')
    
    # Try loading from cache first
    if os.path.exists(cache_file):
        file_mod_time = datetime.fromtimestamp(os.path.getmtime(cache_file))
        if datetime.now() - file_mod_time < timedelta(minutes=5): # Cache for 5 minutes
            print("Loading positions from Schwab cache.")
            with open(cache_file, 'r') as f:
                return json.load(f)

    client = _get_schwab_client()
    if not client:
        return []

    client = _get_schwab_client()
    if not client:
        return []

    account_numbers_response = client.get_account_numbers()
    if not account_numbers_response.is_success:
        print("Error fetching account numbers:", account_numbers_response.text)
        return []
    
    all_schwab_accounts = account_numbers_response.json()
    if not all_schwab_accounts:
        print("No accounts found.")
        return []

    all_formatted_positions = []
    as_of_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    for account in all_schwab_accounts:
        account_id = account['hashValue']
        print(f"Fetching positions for account: {account_id}")

        response = client.get_account(account_id, fields=[Client.Account.Fields.POSITIONS])
        if not response.is_success:
            print(f"Error fetching positions for account {account_id}:", response.text)
            continue # Continue to the next account if there's an error

        account_data = response.json()
        positions = account_data.get('securitiesAccount', {}).get('positions', [])
        
        for p in positions:
            quantity = p['longQuantity'] if 'longQuantity' in p else p.get('shortQuantity', 0) * -1
            market_value = p['marketValue']
            current_price = market_value / quantity if quantity != 0 else 0

            all_formatted_positions.append({
                'account_id': account_id, # Add account_id to each position
                'symbol': p['instrument']['symbol'],
                'quantity': quantity,
                'market_value': market_value,
                'average_price': p.get('averagePrice', 0),
                'current_price': current_price,
                'as_of_timestamp': as_of_timestamp,
            })
            
    # Save to cache
    with open(cache_file, 'w') as f:
        json.dump(all_formatted_positions, f, indent=4)

    return all_formatted_positions

def get_trade_history(start_date: str = None, end_date: str = None, account_id: str = None):
    """
    Fetches the trade history from the Schwab API, with incremental fetching and caching.

    Args:
        start_date (str): Start date in YYYY-MM-DD format. Defaults to 1 year ago.
        end_date (str): End date in YYYY-MM-DD format. Defaults to today.

    Returns:
        A list of dictionaries, where each dictionary represents a transaction.
    """
    if not os.path.exists(SCHWAB_CACHE_DIR):
        os.makedirs(SCHWAB_CACHE_DIR)

    cache_file = os.path.join(SCHWAB_CACHE_DIR, 'trade_history.json')
    all_transactions = []
    latest_cached_date = None

    # Try loading existing trade history from cache
    if os.path.exists(cache_file):
        with open(cache_file, 'r') as f:
            all_transactions = json.load(f)
        if all_transactions:
            # Find the latest date in cached transactions
            latest_cached_date = max(datetime.strptime(t['trade_date'].split('T')[0], '%Y-%m-%d').date() for t in all_transactions if 'trade_date' in t and t['trade_date'])
            print(f"Loaded {len(all_transactions)} transactions from cache. Latest date: {latest_cached_date}")

    client = _get_schwab_client()
    if not client:
        return []

    client = _get_schwab_client()
    if not client:
        return []

    account_numbers_response = client.get_account_numbers()
    if not account_numbers_response.is_success:
        print("Error fetching account numbers:", account_numbers_response.text)
        return []
    
    all_schwab_accounts = account_numbers_response.json()
    if not all_schwab_accounts:
        print("No accounts found.")
        return []

    accounts_to_fetch = []
    if account_id:
        # If a specific account_id is provided, find it in the list of all accounts
        found_account = next((acc for acc in all_schwab_accounts if acc['hashValue'] == account_id), None)
        if found_account:
            accounts_to_fetch.append(found_account)
        else:
            print(f"Account ID {account_id} not found among Schwab accounts.")
            return all_transactions # Return cached data if specified account not found
    else:
        # If no account_id is provided, fetch for all accounts
        accounts_to_fetch = all_schwab_accounts

    newly_fetched_transactions = []

    for account in accounts_to_fetch:
        current_account_id = account['hashValue']
        print(f"Fetching transactions for account: {current_account_id}")

        # Filter cached transactions for the current account
        cached_transactions_for_account = [t for t in all_transactions if t.get('account_id') == current_account_id]
        latest_cached_date_for_account = None
        if cached_transactions_for_account:
            latest_cached_date_for_account = max(datetime.strptime(t['trade_date'].split('T')[0], '%Y-%m-%d').date() for t in cached_transactions_for_account if 'trade_date' in t and t['trade_date'])

        # Determine fetch date range
        fetch_start_date_obj = None
        if latest_cached_date_for_account:
            fetch_start_date_obj = latest_cached_date_for_account + timedelta(days=1) # Fetch from day after latest cached
        elif not start_date:
            fetch_start_date_obj = (datetime.now() - timedelta(days=365)).date() # Default to 1 year if no cache
        else:
            fetch_start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()

        if not end_date:
            fetch_end_date_obj = datetime.now().date()
        else:
            fetch_end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()

        # Ensure fetch_start_date_obj is not in the future and within 1 year of end_date
        if fetch_start_date_obj > fetch_end_date_obj:
            print(f"Fetch start date is after end date for account {current_account_id}. No new data to fetch.")
            continue # Move to the next account

        # Schwab API limit: date range must not be more than a year
        if (fetch_end_date_obj - fetch_start_date_obj).days > 365:
            print(f"Adjusting fetch range for Schwab API limit for account {current_account_id}: {fetch_start_date_obj} to {fetch_end_date_obj}. Max 1 year.")
            # For simplicity, fetch only the last year if range is too wide
            fetch_start_date_obj = fetch_end_date_obj - timedelta(days=365)

        print(f"Fetching incremental transactions from Schwab API for account {current_account_id} from {fetch_start_date_obj} to {fetch_end_date_obj}.")
        response = client.get_transactions(current_account_id, start_date=fetch_start_date_obj, end_date=fetch_end_date_obj)
        if not response.is_success:
            print(f"Error fetching transactions for account {current_account_id}:", response.text)
            continue # Move to the next account

        new_transactions_for_account = response.json()
        
        # Process new transactions
        processed_new_transactions_for_account = []
        for t in new_transactions_for_account:
            transaction_type = t.get('type')
            description = t.get('description', '')
            symbol = t.get('transactionItem', {}).get('instrument', {}).get('symbol')
            quantity = t.get('transactionItem', {}).get('amount')
            price = t.get('transactionItem', {}).get('price')
            trade_date = t.get('tradeDate')
            net_amount = t.get('netAmount')

            processed_new_transactions_for_account.append({
                'account_id': current_account_id, # Add account_id to each transaction
                'type': transaction_type,
                'description': description,
                'symbol': symbol,
                'quantity': quantity,
                'price': price,
                'trade_date': trade_date,
                'net_amount': net_amount
            })
        newly_fetched_transactions.extend(processed_new_transactions_for_account)
    
    # Combine existing cached transactions with newly fetched ones, avoiding duplicates
    # This assumes 'trade_date' and 'account_id' can uniquely identify a transaction for de-duplication
    # A more robust solution might involve a unique transaction ID from Schwab API if available
    
    # Create a set of existing transaction identifiers (e.g., tuple of (account_id, trade_date, symbol, quantity))
    existing_transaction_ids = set()
    for t in all_transactions:
        if 'account_id' in t and 'trade_date' in t and 'symbol' in t and 'quantity' in t:
            existing_transaction_ids.add((t['account_id'], t['trade_date'], t['symbol'], t['quantity']))

    for new_t in newly_fetched_transactions:
        if 'account_id' in new_t and 'trade_date' in new_t and 'symbol' in new_t and 'quantity' in new_t:
            new_transaction_id = (new_t['account_id'], new_t['trade_date'], new_t['symbol'], new_t['quantity'])
            if new_transaction_id not in existing_transaction_ids:
                all_transactions.append(new_t)
                existing_transaction_ids.add(new_transaction_id) # Add to set to prevent future duplicates in this run
        else:
            # If critical fields are missing, just append to avoid data loss, but log a warning
            print(f"Warning: Transaction missing critical fields for de-duplication: {new_t}")
            all_transactions.append(new_t)

    # Sort all transactions by trade_date and then by account_id for consistent caching
    all_transactions.sort(key=lambda x: (x.get('trade_date', ''), x.get('account_id', '')))

    with open(cache_file, 'w') as f:
        json.dump(all_transactions, f, indent=4) # Use indent for readability

    return all_transactions

def get_long_term_holdings():
    """
    Identifies stock units held for more than 1 year based on transaction history.
    NOTE: This is a simplified approach and does not implement full FIFO/LIFO accounting.
    It identifies buy transactions older than 1 year for currently held symbols.
    """
    print("--- Debugging get_long_term_holdings ---")
    transactions = get_trade_history(account_id=None) # Get all transactions
    print("Transactions for long-term holdings:", transactions)
    current_positions = get_positions() # Get current positions to filter relevant symbols
    print("Current positions for long-term holdings:", current_positions)

    long_term_holdings = {}
    one_year_ago = datetime.now() - timedelta(days=365)
    print("One year ago:", one_year_ago.date())

    # Create a dictionary to track current holdings by symbol and account
    current_holdings_by_symbol_account = {}
    for p in current_positions:
        symbol = p['symbol']
        account_id = p['account_id'] # Assuming account_id is now in positions
        if symbol not in current_holdings_by_symbol_account:
            current_holdings_by_symbol_account[symbol] = {}
        current_holdings_by_symbol_account[symbol][account_id] = p['quantity']
    print("Current holdings by symbol and account:", current_holdings_by_symbol_account)

    # Filter transactions for 'TRADE' type and process them
    for t in transactions:
        transaction_type = t.get('type')
        symbol = t.get('symbol')
        quantity = t.get('quantity')
        trade_date_str = t.get('tradeDate')
        net_amount = t.get('netAmount') # Use net_amount to determine buy/sell direction

        if transaction_type != 'TRADE' or not symbol or quantity is None or not trade_date_str or net_amount is None:
            continue # Skip non-trade transactions or incomplete data

        try:
            trade_date = datetime.strptime(trade_date_str.split('T')[0], '%Y-%m-%d').date()
        except ValueError:
            print(f"Error parsing trade date '{trade_date_str}' for transaction: {t}")
            continue

        # Determine if it's a buy or sell based on net_amount
        # Positive net_amount usually indicates a buy (cash out of account)
        # Negative net_amount usually indicates a sell (cash into account)
        # Note: This might need refinement based on actual Schwab API transaction data specifics.
        is_buy = net_amount < 0 # Assuming negative net_amount for buy (cash outflow)
        is_sell = net_amount > 0 # Assuming positive net_amount for sell (cash inflow)

        # For long-term holdings, we are interested in shares bought more than a year ago
        # and still held. This simplified logic aggregates quantities.
        if is_buy and trade_date < one_year_ago.date():
            # Add to long-term holdings if it's a long-term buy
            long_term_holdings[symbol] = long_term_holdings.get(symbol, 0) + abs(quantity)
        elif is_sell:
            # Deduct from long-term holdings if it's a sell
            # Ensure we don't go below zero for long-term quantity
            current_long_term_qty = long_term_holdings.get(symbol, 0)
            long_term_holdings[symbol] = max(0, current_long_term_qty - abs(quantity))

    # After processing all trades, filter out symbols that are no longer held or have zero long-term quantity
    # And ensure that the calculated long-term quantity does not exceed the currently held quantity
    final_long_term_holdings = {}
    for symbol, lt_quantity in long_term_holdings.items():
        current_total_held_quantity = sum(current_holdings_by_symbol_account.get(symbol, {}).values())
        if lt_quantity > 0 and current_total_held_quantity > 0:
            # The long-term quantity should not exceed the total currently held quantity for that symbol
            final_long_term_holdings[symbol] = min(lt_quantity, current_total_held_quantity)
    
    long_term_holdings = final_long_term_holdings
