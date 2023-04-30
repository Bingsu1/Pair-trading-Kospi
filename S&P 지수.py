import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

start_date = '2017-12-29'
yesterday= datetime.today()- timedelta(days=1)
end_date = yesterday.strftime('%Y-%m-%d')

sp500 = yf.Ticker("^GSPC")
sp500_hist = sp500.history(start=start_date, end=end_date, interval="1d")
sp500_hist.to_csv('sp500data.csv', encoding='utf-8-sig')