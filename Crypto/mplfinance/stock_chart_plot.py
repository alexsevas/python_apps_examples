# Построение графиков акций
# pip install yfinance mplfinance

import yfinance as yf
import mplfinance as mpf

# Выбираем биржевой символ и диапазон дат
symbol = input("Enter the stock name: ")
start_date = '2022-01-01'
end_date = '2022-12-31'

# Получение данных
stock_data = yf.download(symbol, start=start_date, end=end_date)

# Создаем свечной график
mpf.plot(stock_data, type='candle', style='yahoo', title=f'{symbol} Candlestick Chart')

