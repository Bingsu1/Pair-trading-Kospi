from datetime import datetime, timedelta
import pandas as pd
from pykrx import stock
from pykrx import bond
import time


tickers = stock.get_market_ticker_list("20230419")

df_list = []

for code in tickers:
    today = datetime.today().strftime('%Y%m%d')
    df = stock.get_market_ohlcv('20180101', today, code)
    df.reset_index(inplace=True)
    df['code'] = code
    df['name'] = stock.get_market_ticker_name(code)
    df = df[['날짜', '시가', '종가', '거래량', 'code', 'name']]
    df_list.append(df)

df_result = pd.concat(df_list)
df_result.to_csv('kospidata.csv', encoding='utf-8-sig', index=False)