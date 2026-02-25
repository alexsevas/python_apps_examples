# Построение графиков акций
# pip install yfinance mplfinance

import yfinance as yf
import mplfinance as mpf
import pandas as pd

# 1. Ввод тикера
symbol = input("Enter the stock symbol (e.g., AAPL, MSFT, RUBUSD=X): ")

# Если пользователь ввел просто RUB, подсказываем про валюты
if symbol.upper() == 'RUB':
    print("Hint: 'RUB' is a currency. Try 'RUBUSD=X' for exchange rate or a stock like 'AAPL'.")
    symbol = 'RUBUSD=X'  # Исправляем на валютную пару для примера

start_date = '2022-01-01'
end_date = '2022-12-31'

print(f"Downloading data for {symbol}...")

# 2. Получение данных
stock_data = yf.download(symbol, start=start_date, end=end_date)

# 3. Проверка: пустые ли данные?
if stock_data.empty:
    print(f"Error: No data found for '{symbol}'. Check the symbol name.")
else:
    # 4. Исправление для новых версий yfinance (MultiIndex колонок)
    # В новых версиях yfinance колонки могут быть вида ('Close', 'Price')
    # mplfinance ожидает простые названия: 'Open', 'High', 'Low', 'Close', 'Volume'
    if isinstance(stock_data.columns, pd.MultiIndex):
        stock_data.columns = stock_data.columns.droplevel(1)

    # 5. Дополнительная проверка на наличие NaN в основных колонках
    required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
    if all(col in stock_data.columns for col in required_columns):
        if stock_data[required_columns].isnull().any().any():
            print("Warning: Data contains missing values. Cleaning...")
            stock_data = stock_data.dropna()

        if not stock_data.empty:
            # 6. Построение графика
            mpf.plot(stock_data,
                     type='candle',
                     style='yahoo',
                     title=f'{symbol} Candlestick Chart',
                     volume=True)  # Добавил объем для наглядности
        else:
            print("Error: No valid data left after cleaning NaNs.")
    else:
        print(f"Error: Downloaded data does not have required columns. Columns found: {stock_data.columns}")

