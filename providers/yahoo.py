# A method which obtains stock data from Yahoo finance
# Requires that you have an internet connection to retreive stock data from Yahoo finance
import time
import datetime
from datetime import date
import random

from pandas_datareader import data

def download_with_dates(contract: str, start_date: date, end_date: date):
    return download(contract, start_date.year, start_date.month, start_date.day,
                    end_date.year, end_date.month, end_date.day)

def download(contract: str, start_year: int, s_month: int,
             s_day: int, e_year: int, e_month: int, e_day: int):
    """
    Args:
        contract (str): the name of the stock/etf
        start_year (int): start year for data
        s_month (int): start month
        s_day (int): start day
        e_year (int): end year
        e_month (int): end month
        e_day (int): end day
    Returns:
        Pandas Dataframe: Daily OHLCV bars
    """
    start = datetime.datetime(start_year, s_month, s_day)
    end = datetime.datetime(e_year, e_month, e_day)
    retry_cnt, max_num_retry = 0, 3
    while retry_cnt < max_num_retry:
        try:
            bars = data.get_data_yahoo(contract, start, end)
            return bars
        except:
            retry_cnt += 1
            time.sleep(random.randint(1, 10))

    print("Yahoo Finance is not reachable.")
    return None

if __name__ == "__main__":
    TODAY = date.today()
    SERIES = download("^HSI", 2010, 1, 1, TODAY.year, TODAY.month, TODAY.day)
    SERIES.to_csv("./data-market/daily/hk/HSI.csv")
