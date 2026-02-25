# Построение графиков акций
# pip install yfinance mplfinance


import yfinance as yf
import mplfinance as mpf
import pandas as pd

symbol = input("Enter the stock symbol (e.g., AAPL, MSFT, ): ").strip().upper()

if symbol == 'RUB':
    symbol = 'RUBUSD=X'
    print(f"Hint: Using currency pair '{symbol}'")

start_date = '2025-03-01'
end_date = '2025-12-31'

print(f"Downloading data for {symbol}...")
stock_data = yf.download(symbol, start=start_date, end=end_date)

if stock_data.empty:
    print(f"❌ Error: No data found for '{symbol}'.")
else:
    # Исправление MultiIndex для новых версий yfinance
    if isinstance(stock_data.columns, pd.MultiIndex):
        stock_data.columns = stock_data.columns.droplevel(1)

    required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
    if all(col in stock_data.columns for col in required_cols):
        stock_data = stock_data.dropna(subset=required_cols)

        if stock_data.empty:
            print("❌ Error: No valid data left after cleaning.")
        else:
            print(f"\n✅ Data loaded: {len(stock_data)} rows")
            print(f"📊 Price range (Close): {stock_data['Close'].min():.6f} — {stock_data['Close'].max():.6f}")

            # === ПОДГОТОВКА ПАРАМЕТРОВ ГРАФИКА ===
            plot_kwargs = {
                'type': 'candle',
                'style': 'yahoo',
                'title': f'{symbol} Candlestick Chart',
                'volume': True
            }

            # Добавляем ylim только если волатильность очень низкая
            price_range = stock_data['Close'].max() - stock_data['Close'].min()
            if price_range < 0.0001:
                print("⚠️ Warning: Very low price variation. Adding manual padding to Y-axis...")
                mid_price = stock_data['Close'].mean()
                padding = mid_price * 0.05
                plot_kwargs['ylim'] = (mid_price - padding, mid_price + padding)

            # === ПОСТРОЕНИЕ ГРАФИКА ===
            # Передаем параметры через распаковку словаря, чтобы не передавать ylim=None
            mpf.plot(stock_data, **plot_kwargs)

    else:
        print(f"❌ Error: Missing required columns. Found: {list(stock_data.columns)}")