import sqlite3
import yfinance as yf

db_path = "/home/ubuntu/agentops/financial.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS financials (
    id INTEGER PRIMARY KEY,
    company TEXT,
    year INTEGER,
    revenue_billion REAL,
    net_income_billion REAL,
    gross_margin_pct REAL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS stock_prices (
    id INTEGER PRIMARY KEY,
    company TEXT,
    date TEXT,
    close_price REAL,
    volume INTEGER
)
""")

# Pull real Tesla data
print("Fetching real Tesla data from Yahoo Finance...")
ticker = yf.Ticker("TSLA")

# Real financials
income = ticker.financials
for col in income.columns:
    year = col.year
    try:
        revenue = round(income.loc["Total Revenue", col] / 1e9, 2)
        net_income = round(income.loc["Net Income", col] / 1e9, 2)
        gross = round(income.loc["Gross Profit", col] / income.loc["Total Revenue", col] * 100, 2)
        cursor.execute("INSERT INTO financials VALUES (NULL,?,?,?,?,?)",
                      ("Tesla", year, revenue, net_income, gross))
        print(f"  Added {year}: revenue=${revenue}B, net_income=${net_income}B")
    except Exception as e:
        print(f"  Skipped {year}: {e}")

# Real stock prices (last 1 year)
print("Fetching real stock prices...")
hist = ticker.history(period="1y")
for date, row in hist.iterrows():
    cursor.execute("INSERT INTO stock_prices VALUES (NULL,?,?,?,?)",
                  ("Tesla", str(date.date()), round(row["Close"], 2), int(row["Volume"])))

print(f"  Added {len(hist)} days of stock prices")

conn.commit()
conn.close()
print("\nDatabase created with REAL data from Yahoo Finance!")
