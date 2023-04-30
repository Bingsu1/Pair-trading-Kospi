import yfinance as yf
from pykrx import stock
from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

#high cointegration 코스피, S&P 데이터
kospi=pd.read_csv('kcointegration.csv')
Sp500=pd.read_csv('sp500modify.csv')
Sp500['Date'] = pd.to_datetime(Sp500['Date'], format='%Y-%m-%d')
tickers = stock.get_market_ticker_list("20230225", market="KOSDAQ")
kospi['코드']=kospi['코드'].astype(str)

result = []
for code in kospi['코드']:
    code = str(code).zfill(6)
    kospi_data = stock.get_market_ohlcv('20180102', '20230419', code)
    kospi_data = kospi_data.reset_index()
    kospi_data['종목'] = stock.get_market_ticker_name(code)
    # S&P500 데이터와 합치기
    kospi_data = pd.merge(kospi_data, Sp500, how='inner', left_on='날짜', right_on='Date')
    
    # 등락률 계산
    kospi_data['kosdaq_rtn'] = kospi_data['종가'].pct_change()
    kospi_data['sp500_rtn'] = kospi_data['Close'].pct_change()
    
    # spread 계산
    kospi_data['spread'] = kospi_data['kosdaq_rtn'] - kospi_data['sp500_rtn']
    
    # z-score 계산
    kospi_data['zscore'] = (kospi_data['spread'] - np.mean(kospi_data['spread'])) / np.std(kospi_data['spread'])
    
    result.append(kospi_data)
    
# 종목별 결과 합치기
df = pd.concat(result, axis=0)
df = df[['날짜', '시가', '종가', '거래량', '종목', 'kosdaq_rtn', 'sp500_rtn', 'spread', 'zscore']]

df.to_csv('kzscore.csv', encoding='utf-8-sig')