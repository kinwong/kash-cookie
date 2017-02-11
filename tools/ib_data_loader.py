import csv
import logging
import time
from datetime import date, timedelta

import os
from swigibpy import Contract

import core.datatools
from providers.ibtws import TwsClient, BarSize

CLIENT_ID = 15
REQUEST_TIME_OUT = 5  # TIme to wait for a response.
WAIT_BETWEEN_REQUEST = 5  # Time to wait before historical data request.
RETRY_WAIT = 2  # * 60  # Time to wait before retry request.
RETRY_COUNT = 5  # Number to retry.
DATA_START = date(2010, 1, 1)
DATA_END = date.today()


class HistoricalData(object):
    def __init__(self):
        self.rows = []

'''def historicalData(self,
                       the_date: date, open_, high, low, close, volume, bar_count, wap, has_gaps):
        # print("Req[%d] Historical=> %s - Open: %s, High: %s, Low: %s, Close: %s, Volume: %d" %
        #       (request.request_id, date, open_, high, low, close, volume))
        row = core.datatools.Expando()
        row.date = the_date
        row.open = open_
        row.high = high
        row.low = low
        row.close = close
        row.volume = volume
        row.bar_count = bar_count
        row.wap = wap
        row.has_gaps = has_gaps
        self.rows.append(row)
'''

def store_file(root_dir, tws: TwsClient, the_date: date, contract: Contract):
    date_dir = "%s" % the_date
    file_name = "%s-%s-%s.csv" % (contract.exchange, contract.secType, contract.symbol)
    full_path = os.path.join(root_dir, date_dir, file_name)

    if os.path.exists(full_path):
        # The file already exists, check it if its holiday.
        # holiday_file = os.path.join(root_dir, date_dir, "holiday")
        # half_day_file = os.path.join(root_dir, date_dir, "half_day")
        # if not os.path.exists(holiday_file):
        #     with open(full_path) as csvfile:
        #         csv_reader = csv.reader(csvfile)
        #         row = next(csv_reader)  # Skips heading row.
        #         row = next(csv_reader)  # first data row
        #         if row is not None:
        #             data_date = datetime.strptime(row[0], "%Y%m%d "
        return

    # Data does not exist, fetch it from IB.
    data = HistoricalData()
    end_date = the_date + timedelta(days=1)

    retry = RETRY_COUNT
    request = None
    while retry > 0:
        request = tws.reqHistoricalData(
            data, contract, end_date.strftime("%Y%m%d 00:00:00"), bar_size=BarSize.Sec30)
        request.done.wait(timeout=REQUEST_TIME_OUT)
        if request.error is not None:
            print('Error caught from request [%d] wait %d seconds then...' % \
            (request.request_id, RETRY_WAIT))
            time.sleep(RETRY_WAIT)
            retry -= 1
            if retry == 0:
                break
            else:
                print('Retry fetching symbol "%s" again - %d try remaining...' % \
                (contract.symbol, retry))
                continue  # try again

    if request.done.is_set():
        # Historical data was fetched, creates the date dir if not exists.
        file_dir = os.path.dirname(full_path)
        if not os.path.isdir(file_dir):
            os.mkdir(file_dir)

        with open(full_path, 'w', newline='') as csvfile:
            csv_writer = csv.writer(
                csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            csv_writer.writerow(
                ['date', 'open', 'high', 'low', 'close', 'volume', 'bar_count', 'wap', 'has_gaps'])
            for row in data.rows:
                csv_writer.writerow(
                    [row.date, row.open, row.high, row.low, row.close,
                     row.volume, row.bar_count, row.wap, row.has_gaps])
        print('File "%s" has been written - wait for while...' % full_path)
        time.sleep(WAIT_BETWEEN_REQUEST)
    else:
        print('Unable to fetch "%s" as of %s ' % (contract.symbol, the_date))


def historical_from_ib(directory: str, data_range):
    directory = os.path.abspath(directory)
    if not os.path.exists(directory):
        os.makedirs(directory)
        print('Root directory "%s" has been created.' % directory)
    else:
        print('Root directory "%s" already exists.' % directory)

    tws = TwsClient(client_id=CLIENT_ID)
    with tws.connect():
        hsi = Contract()
        hsi.exchange = "HKFE"
        hsi.secType = "IND"
        hsi.symbol = "HSI"
        hsi.currency = "HKD"

        hhi = Contract()
        hhi.exchange = "HKFE"
        hhi.secType = "IND"
        hhi.symbol = "HHI.HK"
        hhi.currency = "HKD"

        for the_date in data_range:
            store_file(directory, tws, the_date, hsi)
            store_file(directory, tws, the_date, hhi)

def data_date_range():
    return filter(lambda d: d.weekday() not in [5, 6],
                  core.datatools.date_range(DATA_END, DATA_START))

if __name__ == "__name__":
    logging.basicConfig(level=logging.DEBUG)
    historical_from_ib("../market_data/hk", data_date_range())
