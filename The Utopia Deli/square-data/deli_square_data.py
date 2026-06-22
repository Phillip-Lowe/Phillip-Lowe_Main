import requests
import pyodbc
import json
import logging
import time
from datetime import datetime

global all_payments
all_payments = []

# --- Configuration ---
ACCESS_TOKEN = "EAAAlyODFq82nkBSiZ6J3SA4VnXoXzMGFsNZQSPUbgh7jUefGGB1X3xKY7OxuCcG"
LOCATION_ID = "J4B6A3X6RYA63"
SQUARE_VERSION = "2023-07-22"
MAX_RETRIES = 5
BACKOFF_FACTOR = 2
TIMEOUT = 60  # seconds
MAX_ITERATIONS = 10000000
START_DATE = "2010-01-01T00:00:00Z"  
END_DATE = None

SQL_CONFIG = {
    'DRIVER': '{ODBC Driver 17 for SQL Server}',
    'SERVER': 'mysqlserverar.database.windows.net',
    'DATABASE': 'MyDataBase',
    'UID': 'PhillipLowe',
    'PWD': '123GreeN23!!'
}

# --- Setup Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Database Connection ---
conn_str = ';'.join([f'{key}={value}' for key, value in SQL_CONFIG.items()])
conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

headers = {
    'Square-Version': SQUARE_VERSION,
    'Authorization': f'Bearer {ACCESS_TOKEN}',
    'Content-Type': 'application/json'
}

def retry_request(method, url, **kwargs):
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = method(url, timeout=TIMEOUT, **kwargs)
            if 400 <= response.status_code < 500:  # Don't retry client errors (e.g., 404)
                logging.error(f"Permanent client error {response.status_code}: {response.text}")
                return response  # Return anyway for handling
            response.raise_for_status()
            return response
        except (requests.exceptions.RequestException, requests.exceptions.ConnectionError) as e:
            logging.error(f"Attempt {attempt} failed: {e}")
            if attempt == MAX_RETRIES:
                raise
            sleep_time = BACKOFF_FACTOR ** attempt
            logging.warning(f"Retrying in {sleep_time} seconds...")
            time.sleep(sleep_time)

def setup_dummy_item():
    dummy_square_id = 'UNKNOWN'
    cursor.execute('SELECT COUNT(*) FROM Item WHERE SquareItemID = ?', (dummy_square_id,))
    if cursor.fetchone()[0] == 0:
        try:
            cursor.execute('''
                INSERT INTO Item (UtopiaItemID, SquareItemID, Name, Description, Price, Stock_Quantity)
                VALUES (NEWID(), ?, ?, ?, ?, 0)
            ''', (dummy_square_id, 'Unknown', 'Unknown Item', 0.00))
            conn.commit()
            logging.info("Inserted dummy 'Unknown' item for defaults.")
        except pyodbc.Error as e:
            logging.error(f"Failed to insert dummy item: {e}")

def sync_customers():
    url = 'https://connect.squareup.com/v2/customers'
    params = {}
    previous_cursor = None
    iteration_count = 0

    while iteration_count < MAX_ITERATIONS:
        response = retry_request(requests.get, url, headers=headers, params=params)
        if response.status_code != 200:
            logging.info(f"Failed to sync customers: {response.json()}")
            break

        data = response.json()
        for customer in data.get('customers', []):
            square_id = customer.get('id')
            if not square_id:
                continue

            name = customer.get('given_name') or "Unknown"
            email = customer.get('email_address') or "Unknown"
            phone = customer.get('phone_number') or "Unknown"

            cursor.execute('SELECT COUNT(*) FROM Customer WHERE SquareCustomerID = ?', (square_id,))
            if cursor.fetchone()[0] == 0:
                try:
                    cursor.execute('''
                        INSERT INTO Customer (SquareCustomerID, Name, Email, Phone, Anonymous)
                        VALUES (?, ?, ?, ?, 0)
                    ''', (square_id, name, email, phone))
                except pyodbc.Error as e:
                    logging.error(f"Customer insert failed for ID {square_id}: {e}")

        conn.commit()  # Batch commit

        cursor_token = data.get('cursor')
        if cursor_token == previous_cursor or not cursor_token:
            logging.info("No more customers to process.")
            break

        params['cursor'] = cursor_token
        previous_cursor = cursor_token
        iteration_count += 1

def sync_items():
    url = 'https://connect.squareup.com/v2/catalog/list?types=ITEM'
    params = {}
    previous_cursor = None
    iteration_count = 0

    while iteration_count < MAX_ITERATIONS:
        response = retry_request(requests.get, url, headers=headers, params=params)
        if response.status_code != 200:
            logging.info(f"Failed to sync items: {response.json()}")
            break

        data = response.json()
        for obj in data.get('objects', []):
            item_data = obj.get('item_data', {})
            square_item_id = obj.get('id')
            if not square_item_id:
                continue

            name = item_data.get('name') or "Unknown"
            description = item_data.get('description') or "Unknown"
            price = 0.00
            if 'variations' in item_data and item_data['variations']:
                variation = item_data['variations'][0].get('item_variation_data', {})
                if 'price_money' in variation:
                    price = variation['price_money'].get('amount', 0) / 100.0

            cursor.execute('SELECT COUNT(*) FROM Item WHERE SquareItemID = ?', (square_item_id,))
            if cursor.fetchone()[0] == 0:
                try:
                    cursor.execute('''
                        INSERT INTO Item (UtopiaItemID, SquareItemID, Name, Description, Price, Stock_Quantity)
                        VALUES (NEWID(), ?, ?, ?, ?, 0)
                    ''', (square_item_id, name, description, price))
                except pyodbc.Error as e:
                    logging.error(f"Item insert failed for ID {square_item_id}: {e}")

        conn.commit()  # Batch commit

        cursor_token = data.get('cursor')
        if cursor_token == previous_cursor or not cursor_token:
            logging.info("No more items to process.")
            break

        params['cursor'] = cursor_token
        previous_cursor = cursor_token
        iteration_count += 1

def backfill_item(square_item_id):
    url = f"https://connect.squareup.com/v2/catalog/object/{square_item_id}"
    try:
        response = retry_request(requests.get, url, headers=headers)
        if response.status_code == 200:
            obj = response.json().get('object', {})
            item_data = obj.get('item_data', {})
            name = item_data.get('name', 'Unknown')
            description = item_data.get('description', 'Unknown')
            price = 0.00
            if 'variations' in item_data and item_data['variations']:
                variation = item_data['variations'][0].get('item_variation_data', {})
                if 'price_money' in variation:
                    price = variation['price_money'].get('amount', 0) / 100.0
            cursor.execute("SELECT COUNT(*) FROM Item WHERE SquareItemID = ?", (square_item_id,))
            if cursor.fetchone()[0] == 0:
                cursor.execute(
                    "INSERT INTO Item (UtopiaItemID, SquareItemID, Name, Description, Price, Stock_Quantity) VALUES (NEWID(), ?, ?, ?, ?, 0)",
                    (square_item_id, name, description, price)
                )
                conn.commit()
    except Exception as e:
        logging.error(f"Failed to backfill item {square_item_id}: {e}")

def get_utopia_item_info(square_item_id):
    cursor.execute("SELECT Name, Description, UtopiaItemID, Price FROM Item WHERE SquareItemID = ?", (square_item_id,))
    item_info = cursor.fetchone()
    if not item_info:
        backfill_item(square_item_id)
        cursor.execute("SELECT Name, Description, UtopiaItemID, Price FROM Item WHERE SquareItemID = ?", (square_item_id,))
        item_info = cursor.fetchone()
    if item_info:
        return item_info
    # Default to dummy item
    cursor.execute("SELECT Name, Description, UtopiaItemID, Price FROM Item WHERE SquareItemID = 'UNKNOWN'")
    return cursor.fetchone() or ("Unknown", "Unknown", '00000000-0000-0000-0000-000000000000', 0.00)

def sync_orders():
    url = 'https://connect.squareup.com/v2/orders/search'
    body = {
        "location_ids": [LOCATION_ID],
        "query": {}  # Add filters if needed, e.g., date ranges
    }
    previous_cursor = None
    iteration_count = 0

    while iteration_count < MAX_ITERATIONS:
        if previous_cursor:
            body["cursor"] = previous_cursor

        response = retry_request(requests.post, url, headers=headers, json=body)
        if response.status_code != 200:
            logging.info(f"Failed to sync orders: {response.json()}")
            break

        data = response.json()
        for order in data.get('orders', []):
            square_order_id = order.get('id')
            if not square_order_id:
                continue

            utopia_id = None
            square_customer_id = order.get('customer_id')
            if square_customer_id:
                cursor.execute('SELECT UtopiaID FROM Customer WHERE SquareCustomerID = ?', (square_customer_id,))
                result = cursor.fetchone()
                utopia_id = result[0] if result else None

            # Process line items
            for line_item in order.get('line_items', []):
                square_item_id = line_item.get('catalog_object_id')
                if not square_item_id:
                    continue

                name, description, utopia_item_id, price = get_utopia_item_info(square_item_id)
                quantity = int(line_item.get('quantity', 1))
                item_price = float(line_item.get('base_price_money', {}).get('amount', 0)) / 100.0
                price = item_price if item_price > 0 else price  # Use line item price if available

                cursor.execute('SELECT COUNT(*) FROM [Order] WHERE OrderID = ? AND UtopiaItemID = ?', (square_order_id, utopia_item_id))
                if cursor.fetchone()[0] == 0:
                    try:
                        cursor.execute('''
                            INSERT INTO [Order] (OrderID, UtopiaOrderID, UtopiaPaymentID, UtopiaID, UtopiaItemID, Quantity, Price, Name, Description)
                            VALUES (?, NEWID(), NULL, ?, ?, ?, ?, ?, ?)  -- Use NULL for UtopiaPaymentID initially
                        ''', (square_order_id, utopia_id, utopia_item_id, quantity, price, name, description))
                    except pyodbc.Error as e:
                        logging.error(f"Order insert failed for ID {square_order_id}: {e}")

        conn.commit()  # Batch commit

        cursor_token = data.get('cursor')
        if cursor_token == previous_cursor or not cursor_token:
            logging.info("No more orders to process.")
            break

        previous_cursor = cursor_token
        iteration_count += 1

def sync_payments():
    url = 'https://connect.squareup.com/v2/payments'
    params = {}
    previous_cursor = None
    iteration_count = 0

    while iteration_count < MAX_ITERATIONS:
        response = retry_request(requests.get, url, headers=headers, params=params)
        if response.status_code != 200:
            logging.info(f"Failed to sync payments: {response.json()}")
            break

        data = response.json()
        for payment in data.get('payments', []):
            payment_id = payment['id']
            amount = payment.get('amount_money', {}).get('amount', 0) / 100.0
            status = payment.get('status') or "Unknown"
            square_customer_id = payment.get('customer_id')
            square_order_id = payment.get('order_id')  # Link to order

            utopia_id = None
            if square_customer_id:
                cursor.execute('SELECT UtopiaID FROM Customer WHERE SquareCustomerID = ?', (square_customer_id,))
                result = cursor.fetchone()
                utopia_id = result[0] if result else None

            created_at = payment.get('created_at')
            created_at_dt = datetime.fromisoformat(created_at.replace("Z", "+00:00")) if created_at else None
            source_type = payment.get('source_type', 'Unknown')
            refunds = json.dumps(payment.get('refunds', []))
            disputes = json.dumps(payment.get('disputes', []))

            # Default item info; override if order linked
            name, description, utopia_item_id, price = get_utopia_item_info('UNKNOWN')  # Use dummy
            quantity = 1

            utopia_order_id = None
            if square_order_id:
                cursor.execute('SELECT UtopiaOrderID, UtopiaItemID, Name, Description, Quantity, Price FROM [Order] WHERE OrderID = ?', (square_order_id,))
                order_info = cursor.fetchone()
                if order_info:
                    utopia_order_id, utopia_item_id, name, description, quantity, price = order_info

            cursor.execute('SELECT COUNT(*) FROM Payments WHERE PaymentID = ?', (payment_id,))
            if cursor.fetchone()[0] == 0:
                try:
                    cursor.execute('''
                        INSERT INTO Payments (PaymentID, UtopiaPaymentID, UtopiaOrderID, UtopiaID, UtopiaItemID, Name, Description, Quantity, Price, Amount, Status, SourceType, Created_At, Refunds, Disputes)
                        VALUES (?, NEWID(), ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (payment_id, utopia_order_id, utopia_id, utopia_item_id, name, description, quantity, price, amount, status, source_type, created_at_dt, refunds, disputes))

                    # Update ALL linked order rows with the new UtopiaPaymentID (since one payment can have multiple line items/orders)
                    if utopia_order_id:
                        cursor.execute('''
                            UPDATE [Order] 
                            SET UtopiaPaymentID = (SELECT UtopiaPaymentID FROM Payments WHERE PaymentID = ?) 
                            WHERE UtopiaOrderID = ?
                        ''', (payment_id, utopia_order_id))
                        updated_rows = cursor.rowcount
                        logging.info(f"Updated {updated_rows} order rows with UtopiaPaymentID for PaymentID {payment_id}")

                    all_payments.append({
                        "payment_id": payment_id,
                        "utopia_order_id": str(utopia_order_id) if utopia_order_id else None,
                        "amount": amount,
                        "status": status,
                        "created_at": created_at_dt,
                        "utopia_id": utopia_id
                    })
                except pyodbc.Error as e:
                    logging.error(f"Payment insert failed for ID {payment_id}: {e}")

        conn.commit()  # Batch commit

        cursor_token = data.get('cursor')
        if cursor_token == previous_cursor or not cursor_token:
            logging.info("No more payments to process.")
            break

        params['cursor'] = cursor_token
        previous_cursor = cursor_token
        iteration_count += 1

def main():
    setup_dummy_item()  # Ensure dummy item exists for defaults
    sync_customers()
    sync_items()
    sync_orders()
    sync_payments()

    with open('all_payments.json', 'w') as f:
        json.dump(all_payments, f, default=str, indent=4)

    cursor.close()
    conn.close()

if __name__ == "__main__":
    main()
