from datetime import datetime
from typing import List

class HourPrice:
    time: datetime
    price: float

    def __init__(self, time: datetime, price: float):
        self.time = time
        self.price = price

class HourPriceList:
    prices: List[HourPrice]

    def __init__(self):
        self.prices = []

    def addPrice(self, price: HourPrice):
        index = 0
        for index, p in self.prices:
            if p.time < price.time:
                index += 1
            else:
                break
        self.prices.insert(index, price)
