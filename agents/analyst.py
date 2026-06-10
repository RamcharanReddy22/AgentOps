import os
import yfinance as yf
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from groq import Groq
from config import GROQ_API_KEY, MODEL, MAX_TOKENS

client = Groq(api_key=GROQ_API_KEY)
CHARTS_DIR = "/home/ubuntu/agentops/charts"
os.makedirs(CHARTS_DIR, exist_ok=True)

_last_charts = []

def get_last_charts():
    return _last_charts.copy()

def get_ticker(company_name: str) -> str:
    response = client.chat.completions.create(
        model=MODEL,
        max_tokens=50,
        messages=[
            {"role": "system", "content": "You are a stock ticker lookup assistant. Given a company name (which may have typos), return ONLY the stock ticker symbol. For Indian companies add .NS suffix. Examples: Apple->AAPL, Tata Steel->TATASTEEL.NS, Tesla->TSLA, Reliance->RELIANCE.NS, Infosys->INFY.NS. Return ONLY the ticker, nothing else."},
            {"role": "user", "content": company_name}
        ]
    )
    ticker = response.choices[0].message.content.strip().upper().split()[0]
    ticker = ticker.replace("'","").replace('"',"")
    print(f"Ticker resolved: {company_name} -> {ticker}")
    return ticker

def fetch_financials(ticker: str):
    try:
        stock = yf.Ticker(ticker)
        income = stock.financials
        if income is None or income.empty:
            return None, None
        rows = []
        for col in income.columns:
            year = col.year
            try:
                revenue = round(income.loc["Total Revenue", col] / 1e9, 2)
                net_income = round(income.loc["Net Income", col] / 1e9, 2)
                gross = round(income.loc["Gross Profit", col] / income.loc["Total Revenue", col] * 100, 2)
                rows.append((year, revenue, net_income, gross))
            except:
                pass
        rows.sort(key=lambda x: x[0])
        hist = stock.history(period="1mo")
        stock_rows = []
        if not hist.empty:
            stock_rows = [(str(d.date()), round(r["Close"], 2)) for d, r in hist.iterrows()][-10:]
        return rows, stock_rows
    except Exception as e:
        print(f"yfinance error: {e}")
        return None, None

def generate_revenue_chart(rows, slug: str) -> str:
    years = [str(r[0]) for r in rows]
    revenues = [r[1] for r in rows]
    plt.figure(figsize=(10, 6))
    plt.style.use('dark_background')
    plt.bar(years, revenues, color='#00c47a')
    plt.title('Revenue by Year (Billions USD)')
    plt.xlabel('Year')
    plt.ylabel('Revenue ($B)')
    plt.tight_layout()
    filename = f"{slug}_revenue.png"
    plt.savefig(os.path.join(CHARTS_DIR, filename), dpi=150)
    plt.close()
    return filename

def generate_stock_chart(stock_rows, slug: str) -> str:
    dates = [r[0] for r in stock_rows]
    prices = [r[1] for r in stock_rows]
    plt.figure(figsize=(10, 6))
    plt.style.use('dark_background')
    plt.plot(dates, prices, color='#00c47a', linewidth=2, marker='o')
    plt.title('Stock Price (Last 10 Days)')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.xticks(rotation=45)
    plt.tight_layout()
    filename = f"{slug}_stock.png"
    plt.savefig(os.path.join(CHARTS_DIR, filename), dpi=150)
    plt.close()
    return filename

def run_analyst(query: str) -> str:
    global _last_charts
    _last_charts = []

    company_name = query.replace("Financial analysis for:", "").strip()
    ticker = get_ticker(company_name)
    financials, stock_prices = fetch_financials(ticker)

    if not financials:
        return (
            f"{company_name} does not appear to be a publicly listed company, "
            f"or financial data is not available. "
            f"No stock data or financial charts can be generated."
        )

    slug = ticker.lower().replace(".", "_")
    chart1 = generate_revenue_chart(financials, slug)
    chart2 = generate_stock_chart(stock_prices, slug) if stock_prices else None
    _last_charts = [c for c in [chart1, chart2] if c]
    print(f"Charts generated: {_last_charts}")

    fin_text = "\n".join([
        f"Year {r[0]}: Revenue=${r[1]}B, Net Income=${r[2]}B, Gross Margin={r[3]}%"
        for r in financials
    ])
    stock_text = "\n".join([f"{r[0]}: ${r[1]}" for r in stock_prices]) if stock_prices else "No stock data"

    response = client.chat.completions.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        messages=[
            {"role": "system", "content": "You are a financial analyst. Analyze the provided data and give insights about revenue trends, profitability, and stock performance."},
            {"role": "user", "content": f"Company: {company_name} (Ticker: {ticker})\n\nFinancials:\n{fin_text}\n\nRecent Stock:\n{stock_text}\n\nProvide financial analysis."}
        ]
    )
    return response.choices[0].message.content
