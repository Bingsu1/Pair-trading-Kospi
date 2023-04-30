from pykrx import stock
from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.ticker as ticker

# zscore 데이터 불러오기
zscore = pd.read_csv('kzscore.csv')

# signal 컬럼 추가
signal = pd.DataFrame(0, index=zscore.index, columns=['signal'])
zscore['signal'] = signal
#buy,sell signal 설정
buy_signal = sell_signal = 0
#저장할 딕셔너리
trades = {}

for name in zscore['종목'].unique():
    # 종목별 데이터 추출
    name_data = zscore[zscore['종목'] == name]
    trades[name] = []
    # buy signal, sell signal 구하기
    for i in range(len(name_data)):
        zscore_value = name_data.loc[name_data.index[i], 'zscore']
        if zscore_value <= -1.5:
            # 이미 buy_signal이 존재하는 경우는 추가적인 buy_signal 생략
            if buy_signal == 0:
                name_data.loc[name_data.index[i], 'signal'] = 1
                buy_signal = 1
                sell_signal = 0 # sell signal 초기화
        elif zscore_value >= 0.5:
            # sell_signal 발생
            if buy_signal == 1 and sell_signal == 0:
                name_data.loc[name_data.index[i], 'signal'] = -1
                sell_signal = 1
                buy_signal = 0 # buy signal 초기화
        elif buy_signal == 1 and sell_signal == 0:
            # 스탑로스
            last_buy_trade = trades[name][-1] if len(trades[name]) > 0 else None
            if last_buy_trade is not None:
                last_buy_price = last_buy_trade['price']
                current_price = name_data.loc[name_data.index[i], '종가']
                if current_price <= last_buy_price * 0.9:
                    name_data.loc[name_data.index[i], 'signal'] = -1
                    sell_signal = 1
                    buy_signal = 0
                elif current_price>= last_buy_price *0.9:
                    continue                
        # buy_signal이 존재하는 경우, sell_signal이 나오기 전까지 signal 생략
        else:
            continue
    
    # 결과를 zscore 데이터프레임에 저장
    zscore[zscore['종목'] == name] = name_data

    for i in range(1, len(name_data)):
        # buy signal이 나온 다음날 시가에 매수
        if name_data.loc[name_data.index[i-1], 'signal'] == 1:
            buy_price = name_data.loc[name_data.index[i], '시가']
            buy_date = name_data.loc[name_data.index[i], '날짜']
            trades[name].append({'date': buy_date, 'price': buy_price})
        # sell signal이 나온 다음날 시가에 매도
        elif name_data.loc[name_data.index[i-1], 'signal'] == -1:
            # get the latest buy trade for this stock
            last_buy_trade = trades[name][-1] if len(trades[name]) > 0 else None
            if last_buy_trade is not None: # buy signal에 대한 매수가 이루어진 경우에만 매도
                sell_price = name_data.loc[name_data.index[i], '시가']
                sell_date = name_data.loc[name_data.index[i], '날짜']
                # calculate and store the profit for this trade
                profit = ((sell_price - last_buy_trade['price']) / last_buy_trade['price'])
                trades[name].append({'sell_date': sell_date, 'sell_price': sell_price, 'profit' : profit})



#trades를 리스트의 리스트 데이타프레임으로 바꾸기
trades_list = []
for name in trades:
    if trades[name]:
        for trade in trades[name]:
            trades_list.append([name, trade.get('date', None), trade.get('price', None), trade.get('sell_date', None), trade.get('sell_price', None), trade.get('profit', None)])

trades_df = pd.DataFrame(trades_list, columns=['종목', '매수일', '매수가', '매도일', '매도가', '수익률'])

trades_df['매수일'] = pd.to_datetime(trades_df['매수일'])
trades_df['매도일'] = pd.to_datetime(trades_df['매도일'])
trades_df['수익률'] = trades_df['수익률'] * 100

print(trades_df)

trades_df.to_csv('코스피결과.csv',encoding='utf-8-sig')


# 종목별 수익률
# for name in trades:
#     if 'profit' not in trades[name][-1]:
#         del trades[name][-1]

# # calculate the cumulative profit for each stock    
# cumulative_profits = {}
# for name in trades:
#     cumulative_profits[name] = 1
#     for trade in trades[name]:
#         cumulative_profits[name] *= (1 + trade.get('profit', 0))

# # print the cumulative profits for each stock
# print('Cumulative Profits')
# print('------------------')
# for name, profit in cumulative_profits.items():
#     print(f'{name}: {profit:.2f}')

