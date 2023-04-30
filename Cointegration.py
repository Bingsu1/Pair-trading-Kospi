import pandas as pd
import statsmodels.api as sm
from pykrx import stock
import datetime as dt

# kospi.csv 파일 읽기
kospi_data = pd.read_csv("kospidata.csv", dtype={"code": str})

# sp500data.csv 파일 읽기
sp500_data = pd.read_csv("sp500data.csv")

# S&P500 데이터에서 필요한 컬럼만 추출
sp500_data = sp500_data[["Date", "Close"]]

# 한국 휴장일
khday= pd.read_excel('kholiday.xls')

sp500_data['Date'] = pd.to_datetime(sp500_data['Date'].astype(str).str[:10])
sp500_data['Date'] = pd.to_datetime(sp500_data['Date'], format='%Y-%m-%d')  # Date 컬럼을 datetime으로 변환
khday['날짜'] = pd.to_datetime(khday['날짜'])

for i, date in enumerate(sp500_data['Date']):
    if date.weekday() == 4:  # 금요일인 경우
        sp500_data.loc[i, 'Date'] += pd.Timedelta(days=3)
    elif date.weekday() != 4:  
        sp500_data.loc[i, 'Date'] += pd.Timedelta(days=1)


for i, date in enumerate(sp500_data['Date']):
    if date.strftime('%Y-%m-%d') in khday['날짜'].dt.strftime('%Y-%m-%d').tolist():
        sp500_data.loc[i, 'Date'] += pd.Timedelta(days=1)

for i, date in enumerate(sp500_data['Date']):
    if date.weekday() == 5:  # 토요일인 경우
        sp500_data.loc[i, 'Date'] += pd.Timedelta(days=2)


# Date 기준으로 정렬
sp500_data = sp500_data.sort_values(by="Date")

#중복이 있을경우 첫번째꺼를 제거 하는 방식 // 수익이 별로면 두번째로 바꿔보자
sp500_data = sp500_data.drop_duplicates(subset='Date', keep='last')


# 거래량이 0인 날짜를 찾아서 해당 종목의 데이터 삭제
for code in kospi_data["code"].unique():
    stock_data = kospi_data[kospi_data["code"] == code][["날짜", "종가", "거래량"]]
    zero_volume_count = (stock_data["거래량"] == 0).sum()
    if zero_volume_count >= 20:
        kospi_data = kospi_data[kospi_data["code"] != code]

# 코스피 종목별로 cointegration 검증
result = []
for code in kospi_data["code"].unique():
    # 해당 종목의 데이터 추출
    stock_data = kospi_data[kospi_data["code"] == code][["날짜", "종가"]]
    stock_data["날짜"] = pd.to_datetime(stock_data["날짜"], format='%Y-%m-%d')
    # 데이터를 날짜 기준으로 merge
    merged_data = pd.merge(sp500_data, stock_data, left_on="Date", right_on="날짜", how="inner")
    # cointegration 검증
    _, pvalue, _ = sm.tsa.coint(merged_data["Close"], merged_data["종가"])
    # p-value가 0.05보다 작으면 cointegration이 있다고 판단
    if pvalue < 0.03:
        code.astype(str)
        name = stock.get_market_ticker_name(code)
        result.append([name, code, pvalue])
        

# 결과 출력
result_df = pd.DataFrame(result, columns=["종목", "코드", "P-value"])
result_df = result_df.dropna() # NaN 값이 있는 행 제거
result_df = result_df.reset_index(drop=True) # 인덱스 재설정

result_df.to_csv('kcointegration.csv',encoding='utf-8-sig')