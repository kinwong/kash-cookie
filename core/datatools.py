""" contains tools for reading various data.
"""
from datetime import date
from datetime import timedelta

def date_range(start: date, end: date):
    """ Gets a range of dates.
    """
    delta = timedelta(days=1)
    the_date = start
    if start < end:
        while the_date <= end:
            yield the_date
            the_date += delta
    else:
        while the_date >= end:
            yield the_date
            the_date -= delta

"""Class
"""
class Expando(object):
    pass
