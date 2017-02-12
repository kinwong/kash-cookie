# A method which obtains stock data from Yahoo finance
# Requires that you have an internet connection to retreive stock data from Yahoo finance
import time
import datetime
from pandas_datareader import data

def get_stock_data(contract, s_year, s_month, s_day, e_year, e_month, e_day):
    """
    Args:
        contract (str): the name of the stock/etf
        s_year (int): start year for data
        s_month (int): start month
        s_day (int): start day
        e_year (int): end year
        e_month (int): end month
        e_day (int): end day
    Returns:
        Pandas Dataframe: Daily OHLCV bars
    """
    start = datetime.datetime(s_year, s_month, s_day)
    end = datetime.datetime(e_year, e_month, e_day)
    retry_cnt, max_num_retry = 0, 3

    while retry_cnt < max_num_retry:
        try:
            bars = data.get_data_yahoo(contract, start, end)
            return bars
        except:
            retry_cnt += 1
            time.sleep(np.random.randint(1, 10)) 
            
    print("Yahoo Finance is not reachable")
    return None