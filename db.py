import sqlite3
import pandas as pd
import requests
import io

DB_NAME = "stocks.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stocks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT UNIQUE NOT NULL,
            company_name TEXT
        )
    ''')
    conn.commit()
    conn.close()

def load_nifty500_to_db():
    url = "https://archives.nseindia.com/content/indices/ind_nifty500list.csv"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        df = pd.read_csv(io.StringIO(response.text))
        
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        for index, row in df.iterrows():
            # Add .NS to the symbol for Yahoo Finance compatibility
            symbol = row['Symbol'] + ".NS"
            company_name = row['Company Name']
            
            cursor.execute("INSERT OR IGNORE INTO stocks (symbol, company_name) VALUES (?, ?)", (symbol, company_name))
            
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error fetching Nifty 500 list: {e}")
        
        # Fallback to some major Nifty 50 stocks if fetching fails
        fallback_stocks = [
            ("RELIANCE.NS", "Reliance Industries Limited"),
            ("TCS.NS", "Tata Consultancy Services Limited"),
            ("HDFCBANK.NS", "HDFC Bank Limited"),
            ("INFY.NS", "Infosys Limited"),
            ("ICICIBANK.NS", "ICICI Bank Limited"),
            ("HINDUNILVR.NS", "Hindustan Unilever Limited"),
            ("ITC.NS", "ITC Limited"),
            ("SBIN.NS", "State Bank of India"),
            ("BHARTIARTL.NS", "Bharti Airtel Limited"),
            ("KOTAKBANK.NS", "Kotak Mahindra Bank Limited")
        ]
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        for symbol, name in fallback_stocks:
            cursor.execute("INSERT OR IGNORE INTO stocks (symbol, company_name) VALUES (?, ?)", (symbol, name))
        conn.commit()
        conn.close()
        
        return False

def get_all_stocks():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT symbol, company_name FROM stocks ORDER BY symbol")
    stocks = cursor.fetchall()
    conn.close()
    return stocks

if __name__ == "__main__":
    print("Initializing Database...")
    init_db()
    print("Loading Nifty 500 list...")
    success = load_nifty500_to_db()
    if success:
        print("Successfully loaded Nifty 500 list from NSE.")
    else:
        print("Failed to load full list. Loaded fallback stocks.")
