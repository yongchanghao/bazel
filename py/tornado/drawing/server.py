"""
Homework 1
"""
import threading
import time
from abc import ABC

import numpy as np
from tornado import ioloop
from tornado import web

lucky_person = []
first = []
second = []
third = []
set_prize_page = "templates/set_prize.html"
get_prize_page = "templates/get_prize.html"
count = 0


class PrizeInfo:
    def __init__(self):
        self.namelist = []
        self.number = [0, 0, 0]


prize = PrizeInfo()


class SetPrizeHandler(web.RequestHandler, ABC):
    def get(self):
        """
        override Request Handler
        """
        self.render(set_prize_page)

        for i in range(100000000):
            output = str(time.time())

        print(output, threading.current_thread(), flush=True)
        print(threading.active_count(), flush=True)

    def post(self):
        args = self.request.arguments
        number1 = int(args['number-1'][0].decode())
        number2 = int(args['number-2'][0].decode())
        number3 = int(args['number-3'][0].decode())
        namelist = list(set([name.decode() for name in args['name']]))

        global lucky_person, first, second, third

        if number1 + number2 + number3 > len(namelist):
            self.write("<script>alert('Invalid');window.history.back(-1);</script>")
            self.flush()
        else:
            prize.namelist = namelist
            prize.number = [number1, number2, number3]
            lucky_person = np.random.choice(prize.namelist, sum(prize.number), replace=False)
            first = lucky_person[: number1]
            second = lucky_person[number1: number1 + number2]
            third = lucky_person[number1 + number2:]
            self.redirect("/")


class MainPageHandler(web.RequestHandler, ABC):
    """
    main handler for home page
    """

    def get(self):

        self.render(get_prize_page)

    def post(self):
        global first, second, third

        args = self.request.arguments
        number1 = int(args['number-1'][0].decode())
        number2 = int(args['number-2'][0].decode())
        number3 = int(args['number-3'][0].decode())
        if len(first) < number1 or len(second) < number2 or len(third) < number3:
            self.write("<script>alert('Invalid');window.history.back(-1);</script>")
            self.flush()

        self.write('<table border="1">')
        self.write("<tr><th>First Prize</th></tr>")
        for name in first[:number1]:
            self.write("<tr><td>%s</td></tr>" % name)
        self.write("</table>")
        first = first[number1:]

        self.write('<table border="1">')
        self.write("<tr><th>Second Prize</th></tr>")
        for name in second[:number2]:
            self.write("<tr><td>%s</td></tr>" % name)
        self.write("</table>")
        second = second[number2:]

        self.write('<table border="1">')
        self.write("<tr><th>Third Prize</th></tr>")
        for name in third[:number3]:
            self.write("<tr><td>%s</td></tr>" % name)
        self.write("</table>")
        third = third[number3:]

        self.flush()


app = web.Application([
    ("/", MainPageHandler),
    ("/set", SetPrizeHandler),
])

if __name__ == "__main__":
    app.listen(8848)
    ioloop.IOLoop.instance().start()
    ioloop.IOLoop.instance().stop()
