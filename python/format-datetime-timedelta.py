#!/usr/bin/env python3

# https://stackoverflow.com/questions/538666/format-timedelta-to-string
# Format timedelta to string

# https://stackoverflow.com/a/28242294/10440128

# NOTE this is probably wrong, because it uses leap years since year 1
# https://en.wikipedia.org/wiki/Leap_year

import datetime

# i was born on 1989-08-23, how old am i today?
t1 = datetime.datetime(year=1989, month=8, day=23)
t2 = datetime.datetime.now()
print("t1", t1)
print("t2", t2)

dt = t2 - t1 # datetime.timedelta

print("dt.total_seconds:", dt.total_seconds())

# convert datetime.timedelta to datetime.datetime so we can use the strftime method
# wrong! this would start at the unix epoch 1980-01-01
# dt2 = datetime.datetime.fromtimestamp(dt.total_seconds(), datetime.UTC)
# dt2 = datetime.datetime(year=1, month=1, day=1, second=int(dt.total_seconds())) # zoneinfo=datetime.UTC)
# dt2 = datetime.datetime(year=1, month=1, day=1) + dt
dt2 = datetime.datetime(year=1, month=1, day=1) + dt - datetime.timedelta(days=365)
# dt2 = datetime.datetime(year=1, month=1, day=1) - datetime.timedelta(days=365)

# no: AttributeError: attribute 'year' of 'datetime.date' objects is not writable
# dt2.year = dt2.year - 1

print("dt2:", dt2.strftime("%Y-%m-%d %H:%M:%S"))

# days_per_year = 365.2425 # Gregorian calendar
days_per_year = 365.24219 # tropical year

seconds_per_year = days_per_year * 24 * 60 * 60

years = dt.total_seconds() / seconds_per_year

print("years:", years)
