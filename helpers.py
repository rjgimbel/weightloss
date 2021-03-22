import os
import requests
import urllib.parse
from datetime import date, timedelta
import pytz

from flask import redirect, render_template, request, session
from functools import wraps


def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def calculate_weeks(date):
   """Given a start date; returns the 12 weeks including that date.  In our case we will be doing Monday's"""
   # List will hold 12 weeks worth of Monday's which will be returned by the function
   mondays = {}

   for week in range (24):
      mondays[date] = week + 1
      date += timedelta(days = 7)

   return mondays


def percent_diff(weight1, weight2):
    """Passed 2 weights and returns the % decrease/increase"""
    diff = (weight1 - weight2) / weight1 * 100
    return round(diff, 2)
