"""Example Google style docstrings.

This module demonstrates documentation as specified by the `Google Python
Style Guide`_. Docstrings may extend over multiple lines. Sections are created
with a section header and a colon followed by a block of indented text.

Example:
    Examples can be given using either the ``Example`` or ``Examples``
    sections. Sections support any reStructuredText formatting, including
    literal blocks::

        $ python example_google.py

Section breaks are created by resuming unindented text. Section breaks
are also implicitly created anytime a new section starts.

Attributes:
    module_level_variable1 (int): Module level variables may be documented in
        either the ``Attributes`` section of the module docstring, or in an
        inline docstring immediately following the variable.

        Either form is acceptable, but the two should not be mixed. Choose
        one convention to document module level variables and be consistent
        with it.

Todo:
    * For module TODOs
    * You have to also use ``sphinx.ext.todo`` extension

.. _Google Python Style Guide:
   http://google.github.io/styleguide/pyguide.html

"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from enum import Enum

import logging
import threading

from threading import Event, Lock
from swigibpy import EWrapper, EPosixClientSocket, Contract


class Disconnecting(object):
    """Represents context manager that disconnects the TWS socket."""
    def __init__(self, tws):
        self._tws = tws

    def __enter__(self):
        pass

    # noinspection PyUnusedLocal
    def __exit__(self, exc_type, exc_val, exc_tb):
        self._tws.eDisconnect()


class BarSize(Enum):
    """Specifies the size of the bars that will be returned (within IB/TWS limits)."""
    Sec1 = "1 sec"
    Sec5 = "5 secs"
    Sec10 = "10 secs"
    Sec15 = "15 secs"
    Sec30 = "30 secs"
    Min1 = "1 min"
    Min2 = "2 mins"
    Min3 = "3 mins"
    Min5 = "5 mins"
    Min10 = "10 mins"
    Min15 = "15 mins"
    Min20 = "20 mins"
    Min30 = "30 mins"
    Hour1 = "1 hour"
    Hour2 = "2 hours"
    Hour3 = "3 hours"
    Hour4 = "4 hours"
    Hour8 = "8 hours"
    Day1 = "1 day"
    Week1 = "1 week"
    Month1 = "1 month"


class WhatToShow(Enum):
    """Represents historical data types.
    All different kinds of historical data are returned in the form of candlesticks and as such the
    values return represent the state of the market during the period covered by the candlestick. 
    For instance, it might appear
    obvious but a TRADES day bar's 'close' value does NOT represent the product's closing price but rather the last
    traded price registered.
    """
    Trades = "TRADES"
    MidPoint = "MIDPOINT"
    Bid = "BID"
    Ask = "ASK"
    BidAsk = "BID_ASK"
    HistoricalVolatility = "HISTORICAL_VOLATILITY"
    OptionImpliedVolatility = "OPTION_IMPLIED_VOLATILITY"


class UseRth(Enum):
    """Determines whether to return all data available during the requested time span, or only data that falls within
    regular trading hours."""
    OutsideTradingHour = 0
    """All data is returned even where the market in question was outside of its regular trading hours."""
    WithinTradingHour = 1
    """Only data within the regular trading hours is returned, even if the requested time span falls partially or
    completely outside of the RTH."""


class FormatDate(Enum):
    """Determines the date format applied to returned bars."""
    InString = 1
    """dates applying to bars returned in the format: yyyymmdd{space}{space}hh:mm:dd"""
    InLong = 2
    """dates are returned as a long integer specifying the number of seconds since 1/1/1970 GMT."""


class RequestType(Enum):
    """Represents the request types."""
    HistoricalData = "HistoricalData"
    """Request of historical data."""
    MarketData = "MarketData"
    """Request of live market data."""


class Request(object):
    """Represents a pending request."""
    def __init__(self, client, request_type: RequestType, request_id: int, handler):
        self._client = client
        self._request_type = request_type
        self._request_id = request_id
        self._handler = handler
        self._done = Event()
        self._error = None

    @property
    def request_id(self):
        return self._request_id

    @property
    def request_type(self):
        return self._request_type

    @property
    def handler(self):
        return self._handler

    @property
    def done(self):
        return self._done

    @property
    def error(self):
        return self._error

    def cancel(self, error=None):
        """Cancels the pending request"""
        self._error = error
        return self._client.cancelRequest(self)

""" Represents a IB event wrapper that multicasts"""


class _MulticastWrapper(EWrapper):
    def __init__(self, requests: dict, lock: Lock):
        super().__init__()

        self._requests = requests
        self._lock = lock

    def orderStatus(self, id_, status, filled, remaining, avg_fill_price, perm_id,
                    parent_id, last_filled_price, client_id, why_held):
        pass

    def openOrder(self, order_id, contract, order, order_state):
        pass

    def nextValidId(self, order_id):
        """Always called by TWS but not relevant for our example"""
        pass

    def openOrderEnd(self):
        """Always called by TWS but not relevant for our example"""
        pass

    def managedAccounts(self, open_order_end):
        """Called by TWS but not relevant for our example"""
        pass

    def historicalData(self, req_id: int, date, open_, high, low, close, volume, bar_count, wap, has_gaps):
        """historicalData(EWrapper self, TickerId reqId, IBString const & date, double open, double high, double low,
        double close, int volume, int barCount, double WAP, int hasGaps)"""
        with self._lock:
            request = self._requests.get(req_id)
            if request is None:
                logging.warning("historicalData[req_id= %d] with no associated request - ignored.." % req_id)
                return
            elif date[:8] == 'finished':
                del self._requests[req_id]
                request.done.set()
                return
            request.handler.historicalData(request, date, open_, high, low, close, volume, bar_count, wap, has_gaps)

    def tickPrice(self, req_id: int, field: int, price: float, can_auto_execute: int):
        """tickPrice(EWrapper self, TickerId tickerId, TickType field, double price, int canAutoExecute)"""
        with self._lock:
            request = self._requests.get(req_id)
            if request is None:
                logging.warning("tickPrice[req_id= %d] with no associated request - ignored." % req_id)
        request.handler.tickPrice(request, field, price, can_auto_execute)

    def tickSize(self, req_id: int, field: int, size: int):
        """tickSize(EWrapper self, TickerId tickerId, TickType field, int size)"""
        with self._lock:
            request = self._requests.get(req_id)
            if request is None:
                logging.warning("tickSize[req_id= %d] with no associated request - ignored." % req_id)
                return

        request.handler.tickSize(request, field, size)

    def tickGeneric(self, req_id: int, tick_type: int, value: float):
        """tickGeneric(EWrapper self, TickerId tickerId, TickType tickType, double value)"""
        with self._lock:
            request = self._requests.get(req_id)
            if request is None:
                logging.warning("tickGeneric[req_id=" + str(req_id) + "] with no associated request - ignored.")
                return

        request.handler.tickGeneric(request, tick_type, value)

    def tickString(self, req_id: int, tick_type: int, value: str):
        """tickString(EWrapper self, TickerId tickerId, TickType tickType, IBString const & value)"""
        with self._lock:
            request = self._requests.get(req_id)
            if request is None:
                logging.warning("tickGeneric[req_id=" + str(req_id) + "] with no associated request - ignored.")
                return
        request.handler.tickString(request, tick_type, value)

    def error(self, req_id: int, error_code: int, error_string: str):
        import sys
        if error_code == 165:  # Historical data sevice message
            sys.stderr.write("TWS Warning - %s: %s\n" % (error_code, error_string))
        elif 501 <= error_code < 600:  # Socket read failed
            sys.stderr.write("TWS Client Error - %s: %s\n" % (error_code, error_string))

        elif 100 <= error_code < 1100:
            sys.stderr.write("TWS Error - %s: %s\n" % (error_code, error_string))
            request = self._requests.get(req_id)
            if request is not None:
                request.cancel(error_string)
                return

        elif 1100 <= error_code < 2100:
            sys.stderr.write("TWS System Error - %s: %s\n" % (error_code, error_string))
        elif 2100 <= error_code <= 2110:
            sys.stderr.write("TWS Warning - %s: %s\n" % (error_code, error_string))
        else:
            sys.stderr.write("TWS Error - %s: %s\n" % (error_code, error_string))


class TwsClient(object):
    logger = logging.getLogger(__name__)
    """Represents Interactive Broker's TWS."""
    _next_request_id = 0

    def __init__(self, client_id: int):
        """Initialises an instance for the specified client id."""
        self._client_id = client_id
        self._requests_lock = threading.Lock()
        self._requests = {}
        self._wrapper = _MulticastWrapper(self._requests, self._requests_lock)
        self._socket = EPosixClientSocket(self._wrapper)

    @property
    def client_id(self):
        return self._client_id

    def connect(self, host: str="", port: int=7496)->Disconnecting:
        """Connects to TWS."""
        if not self._socket.eConnect(host, port, self.client_id):
            raise RuntimeError("Client[%d] Failed to connect at Host: %s, Port: %d" % \
            (self._client_id, host, port))
        TwsClient.logger.info("Client[%d] connected at Host: %s, Port: %d" % (self._client_id, host, port))
        return Disconnecting(self._socket)

    def reqHistoricalData(self, handler, contract: Contract, end_datetime: str, duration: str = "1 D",
                          bar_size: BarSize = BarSize.Min1, what_to_show: WhatToShow = WhatToShow.Trades,
                          use_rth: UseRth = UseRth.WithinTradingHour, format_date: FormatDate = FormatDate.InString):
        """"""
        request = self._createRequest(RequestType.HistoricalData, handler)
        self._socket.reqHistoricalData(request.request_id, contract, end_datetime, duration, bar_size.value,
                                       what_to_show.value, use_rth.value, format_date.value)
        return request

    def reqMarketData(self, handler, contract: Contract, generic_tick: str, snapshot: bool = False):
        """"""
        request = self._createRequest(RequestType.MarketData, handler)
        self._socket.reqMktData(request.request_id, contract, generic_tick, snapshot)
        return request

    def reqOpenOrders(self):
        return self._socket.reqOpenOrders()

    def cancelRequest(self, request: Request):
        """"""
        req_id = request.request_id
        with self._requests_lock:
            if self._requests.get(req_id) != request:
                return False
            del self._requests[req_id]
            try:
                {
                    RequestType.HistoricalData: lambda:
                        self._socket.cancelHistoricalData(req_id),
                    RequestType.MarketData: lambda:
                        self.cancelMktData(req_id)
                }[request.request_type]()
            except KeyError:
                raise LookupError("Client[%d] Reqest: %d - Unable to cancel unknown request type [%s]." %
                                  (self._client_id, req_id, request.request_type.value))

    def cancelMktData(self, req_id):
        TwsClient.logger.info('MarketData request[%d] is cancelled.' % req_id)
        self._socket.cancelMktData(req_id)

    def _createRequest(self, req_type: RequestType, handler) -> Request:
        TwsClient._next_request_id += 1
        req_id = TwsClient._next_request_id
        request = Request(self, req_type, req_id, handler)
        with self._requests_lock:
            self._requests[req_id] = request
        return request
