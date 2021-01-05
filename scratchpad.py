from datetime import date, timedelta
import pytz
"""
def allsundays(year):
   d = date(year, 1, 1)                    # January 1st
   d += timedelta(days = 6 - d.weekday())  # First Sunday
   while d.year == year:
      yield d
      d += timedelta(days = 7)

for d in allsundays(2010):
   print(d)

d = date(2021, 1, 1)

# first monday
d2 = d.replace(days = d.weekday())

for week in range (12):
    print(f"week {week}: {d2}")
    d2 += timedelta(days=7)

"""



""">>> import pytz
>>> est = pytz.timezone('America/New_York')
>>> est
<DstTzInfo 'America/New_York' LMT-1 day, 19:04:00 STD>
>>> datetime.now()
datetime.datetime(2020, 12, 23, 3, 2, 29, 60280)
>>> datetime.today()
datetime.datetime(2020, 12, 23, 3, 2, 33, 595812)
>>> datetime.now(est)
datetime.datetime(2020, 12, 22, 22, 2, 37, 536764, tzinfo=<DstTzInfo 'America/New_York' EST-1 day, 19:00:00 STD>)
>>>

from datetime import datetime, timedelta
now = datetime.now()
monday = now - timedelta(days = now.weekday())
print(monday)

"""

#def calculate_weeks(year):
"""Given a year, calculates the first 12 Monday's of the year"""
"""   d = date(year, 1, 1)

   # First Monday
   monday = d - timedelta(days = d.weekday())
   if monday.year < d.year:
      # need to start with the first monday in the given year
      monday += timedelta(days = 7)
   # dict to hold all Monday's
   mondays = {}

   for week in range (12):
      print(f"week {week + 1}: {monday}")
      mondays[week + 1] = monday
      monday += timedelta(days = 7)

   return mondays


test = calculate_weeks(2021)
print(test)
"""

def calculate_weeks(year, month, day):
   d = date(year, month, day)
   mondays = {}

   for week in range (12):
      print(f"week {week + 1}: {d}")
      mondays[d] = week + 1
      d += timedelta(days = 7)
   return mondays

test = calculate_weeks(2021, 1, 4)
print(test)

from cs50 import SQL
db = SQL("sqlite:///weightloss.db")

week = 2

rows = db.execute("SELECT users.username, users.display_name, weight.'1', weight.:week \
        FROM users JOIN weight on weight.user_id = users.id", week=str(week))

rows = db.execute("SELECT users.display_name, weight.'1', weight.'2', weight.'3', \
   weight.'4', weight.'5', weight.'6', weight.'7', weight.'8', weight.'9', \
   weight.'10', weight.'11', weight.'12' \
   FROM users JOIN weight on weight.user_id=users.id")

rows = db.execute("SELECT users.display_name, '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12' \
   FROM users JOIN weight on weight.user_id=users.id WHERE weight.user_id=:user_id", user_id=1)

for row in rows:
   for key in row.keys():
      if row[key] == None:
         print(0)
      else:
         print(row[key])