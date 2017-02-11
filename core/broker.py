from abc import ABCMeta, abstractmethod


class Broker(object):
    """ Abstract broker that place orders in the market. """
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_orders(self):
        """ ffewff """
        pass


