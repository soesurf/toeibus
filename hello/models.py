# -*- coding: utf-8 -*-
import datetime
import json
import bisect
import requests
from datetime import datetime, timedelta
from django.shortcuts import render
from django.http import HttpResponse
from django.db import models


# Create your models here.
class Greeting(models.Model):
    when = models.DateTimeField('date created', auto_now_add=True)


class Bus(models.Model):
    next_bus = ''
    japan_time = ''
    current_time = ''
    current_time_as_int = ''
    current_date = ''
    from_and_to = ''
    time_for_calculation = ''
    message = ''

    def __init__(self, line):

        self.japan_time = datetime.now() + timedelta(hours=1)
        self.current_time = self.japan_time.strftime("%H:%M:%S")
        self.current_time_as_int = int(self.japan_time.strftime("%H%M"))
        self.current_date = self.japan_time.date()

        self.__handle_work__(line)

    def __handle_work__(self, line):
        if line == 'harumi':
            self.from_and_to = 'ほっとプラザはるみ前 -> 丸の内行き!'
        else:
            self.from_and_to = '新島橋 -> 亀戸行き'

        url = 'http://toeibus.azurewebsites.net/api/values/' + line
        # handle as if below is for harumi url
        # time_table = requests.get('http://toeibus.azurewebsites.net/api/values')

        next_bus = self.__get_next_bus__(url)
        self.next_bus = Bus.pretty_print(next_bus)

        # sabun check
        if self.current_time_as_int < next_bus:
            time_difference = Bus.__calculate_difference__(self)
            self.message = '約 {0} 分後に次のバス({1})が到着します'.format(time_difference, self.next_bus)
            self.time_for_calculation = self.japan_time.strftime('%B %d %Y ') + self.next_bus + ' GMT+09:00'

        else:
            self.message = '次のバスは翌朝の ' + str(self.next_bus)
            # I should add one day here.
            date_added_1day = self.japan_time + timedelta(days=1)

            self.time_for_calculation = date_added_1day.strftime('%B %d %Y ') + self.next_bus + ' GMT+09:00'

    # get the next bus based on current time
    # logic is align the time table and insert current time and sort it.
    # return the value of current_time + 1.
    # it should be the next_bus
    # if current_time is the last index, the next bus would be 始発 bus.
    def __get_next_bus__(self, url):
        schedule = Bus.__get_schedule__(url)
        schedule.append(self.current_time_as_int)
        # test
        # schedule.append(2345)
        schedule.sort()
        next_bus = bisect.bisect(schedule, self.current_time_as_int)

        if next_bus == len(schedule):
            # when you are in this block
            # it means the last bus has gone already.
            # so the next bus is the first bus in the following day.
            return schedule[0]
        return schedule[next_bus]

    @staticmethod
    def pretty_print(next_bus_time):
        temp = str(next_bus_time)
        if len(temp) == 4:
            return str(temp[:2] + ":" + temp[2:4])
        else:
            #631 -> 6:31
            return str(temp[:1] + ":" + temp[1:3])

    @staticmethod
    def __get_schedule__(url):
            schedule = requests.get(url)
            time_table_int_list = []
            sorted_schedule = []
            key_list = json.loads(schedule.text)

            for k in key_list.keys():
                time_table_int_list.append(int(k))

            for hour in sorted(time_table_int_list):

                for minutes in key_list[str(hour)]:
                    sorted_schedule.append(int(str(hour) + minutes))

            return sorted_schedule

    @staticmethod
    def __calculate_difference__(self):
        # type: (object) -> object

        # check if first 1 or 2 digits equals or not
        # if it does, no need to use magic number (40)
        # same hour from 6 to 9

        # I should refactor real hard.
        # this is not clean.

        current_time = int(self.japan_time.strftime("%H%M"))
        next_bus = int(self.next_bus.replace(':', ''))
        remaining_minutes = 0
        if len(str(current_time)) == 3 and len(str(next_bus)) == 3:
            if str(current_time)[0] == str(next_bus)[0]:
                remaining_minutes = next_bus - current_time
            else:
                remaining_minutes = (next_bus - current_time) - 40

        if len(str(current_time)) == 3 and len(str(next_bus)) == 4:
            remaining_minutes = (next_bus - current_time) - 40

        if len(str(current_time)) == 4 and len(str(next_bus)) == 4:
            if str(current_time)[:2] == str(next_bus)[:2]:
                remaining_minutes = next_bus - current_time
            else:
                remaining_minutes = (next_bus - current_time) - 40

        return remaining_minutes



