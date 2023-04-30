from pykrx import stock
from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.ticker as ticker

result=pd.read_csv('코스피결과.csv')

# 매도일 기준으로 정렬
result_sorted = result.sort_values(by='매도일')
result_sorted = result_sorted.dropna(subset=['매도일'])

# 중복 없는 매도일 데이터 가져오기
dates = result_sorted['매도일'].unique().astype(str)
# str에서 날짜로 변환
dates = [datetime.strptime(date, '%Y-%m-%d') for date in dates]
# 날짜순으로 정렬
dates.sort()

# 각 날짜별 수익률 합산하기
cumulative_profit = []
grouped = result_sorted.groupby('매도일')
for date, group in grouped:
    profit_sum = group['수익률'].sum()
    profit = profit_sum / 100.0 / 15.0
    cumulative_profit.append(cumulative_profit[-1] * (1 + profit) if cumulative_profit else 1.0 + profit)
print(cumulative_profit[-1])

#MDD
max_profit = 0.0
drawdown = 0.0
max_drawdown = 0.0
mdd_start_date = None
mdd_end_date = None
for date, profit in zip(dates, cumulative_profit):
    if profit > max_profit:
        max_profit = profit
        drawdown = 0.0
    else:
        drawdown = max(drawdown, max_profit - profit)
        if drawdown > max_drawdown:
            max_drawdown = drawdown
            mdd_start_date = dates[cumulative_profit.index(max_profit)]
            mdd_end_date = date
mdd_text = f'MDD: {max_drawdown:.2%}, start date: {mdd_start_date}, end date: {mdd_end_date}'
print(f'MDD: {max_drawdown:.2%}, start date: {mdd_start_date}, end date: {mdd_end_date}')
cumpro_text = f'Cumulative Profit: {cumulative_profit[-1]}'

#Sharpe ratio
profits = pd.DataFrame({'date': dates, 'profit': cumulative_profit})
profits['daily_return'] = profits['profit'].pct_change()
volatility = profits['daily_return'].std()

#변동성
annual_volatility = volatility * np.sqrt(252)

annual_return = (cumulative_profit[-1] ** (252/len(dates))) - 1

risk_free_rate = 0.03

sharpe_ratio = (annual_return - risk_free_rate) / annual_volatility

sharpe_text = f'Sharpe Ratio: {sharpe_ratio:.2f}'
print(sharpe_text)

# 그래프 그리기
plt.rc('font', family='NanumGothic')
plt.plot(dates, cumulative_profit, label='profit and loss')
plt.legend(loc='lower right')
plt.xlabel('매도일')
plt.ylabel('수익률 %')
plt.xticks(rotation=45)
plt.text(0.5, 1.05, mdd_text, transform=plt.gca().transAxes, ha='center', va='bottom', color='r', fontsize=10)
plt.text(0.5,1.1,cumpro_text + ' / '+ sharpe_text, transform=plt.gca().transAxes, ha='center', va='bottom', color='r', fontsize=10)
plt.title('zscore -1.5 : 0.5', fontsize=10)
plt.show()

