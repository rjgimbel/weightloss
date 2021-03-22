import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, calculate_weeks, percent_diff
from datetime import date, timedelta, datetime
import pytz

app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///weightloss.db")


@app.route("/")
@login_required
def index():

    # confirm if user is registered for the new competition
    rows = db.execute("SELECT * FROM weight WHERE user_id = :user_id", user_id=session["user_id"])

    if len(rows) != 1:
        # Have them join the competition
        return render_template("/join.html")

    # get weights from db
    rows = db.execute("SELECT users.display_name, weight.'1', weight.'2', weight.'3', \
        weight.'4', weight.'5', weight.'6', weight.'7', weight.'8', weight.'9', \
        weight.'10', weight.'11', weight.'12', weight.'13', weight.'14', weight.'15', \
        weight.'16', weight.'17', weight.'18', weight.'19', weight.'20', weight.'21', \
        weight.'22', weight.'23', weight.'24' \
        FROM users JOIN weight on weight.user_id=users.id WHERE weight.user_id=:user_id", user_id=session["user_id"])

    # if no weights, return apology
    if len(rows) != 1:
        return apology("No weights entered yet", 403)
    return render_template("index.html", rows=rows)


@app.route("/join", methods=["GET", "POST"])
@login_required
def join():
    """Join the competition"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # enter user into the weight db
        db.execute("INSERT INTO weight (user_id) VALUES (:user_id)", user_id=session["user_id"])

        return render_template("inputweight.html")
    else:
        return render_template("join.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Ensure password confirmation was submitted
        elif not request.form.get("confirmation"):
            return apology("must confirm password", 403)

        # Ensure passwords match
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("password and confirmation must match", 403)

        # Ensure email was submitted
        elif not request.form.get("email"):
            return apology("must provide email", 403)

        # Ensure display name was submitted
        elif not request.form.get("name"):
            return apology("must provide display name", 403)

        # Insert user into database
        db.execute("INSERT INTO users (username, hash, email, display_name) VALUES (:username, :hash, :email, :display_name)",
                username=request.form.get("username"),
                hash=generate_password_hash(request.form.get("password")),
                email=request.form.get("email"),
                display_name=request.form.get("name"))


        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")

@app.route("/inputweight", methods=["GET", "POST"])
@login_required
def inputweight():
    """Enter this week's weight"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # ensure weight has been entered
        if not request.form.get("weight"):
            return apology("must enter weight", 403)

        # get the week and weight
        weight = float(request.form.get("weight"))
        # Enter weight into db
        db.execute("UPDATE weight SET :week = :weight WHERE user_id = :user_id", user_id=session["user_id"],
            week=request.form.get("week"),
            weight=weight)
        return redirect("/")

    else:
        # confirm if user is registered for the new competition
        rows = db.execute("SELECT * FROM weight WHERE user_id = :user_id", user_id=session["user_id"])

        if len(rows) != 1:
            # Redirect to index so they're prompted to register
            return redirect("/")

        # starting on 1/4/21
        YEAR = 2021
        MONTH = 1
        DAY = 4
        start_date = date(YEAR, MONTH, DAY)

        # if the contest hasn't started, return apology
        if date.today() < start_date:
            return apology(f"Start date is {start_date:%m/%d/%Y}, please return at that time")

        # The contest has started, lets figure out which week it is.
        weeks = calculate_weeks(start_date)
        # Get today's date and calculate which date is Monday, this will tell us which week of the competition it is
        now = datetime.now().date()
        monday = now - timedelta(days = now.weekday())
        # get the week from the weeks dictionary
        week = weeks[monday]

        return render_template("inputweight.html", week=week)

@app.route("/results", methods=["GET"])
@login_required
def results():
    """Display results for all users (% lost only)."""

    # figure out the week
    # get the weights for all users for week 1 and this week and last week
    # calculate % up/down from starting weight for last week and this week (if weight inputted already)
    # starting on 1/4/21
    YEAR = 2021
    MONTH = 1
    DAY = 4
    start_date = date(YEAR, MONTH, DAY)

    # if the contest hasn't started, return apology
    if date.today() < start_date:
        return apology(f"Start date is {start_date:%m/%d/%Y}, please return at that time")

    # The contest has started, lets figure out which week it is.
    weeks = calculate_weeks(start_date)
    # Get today's date and calculate which date is Monday, this will tell us which week of the competition it is
    now = datetime.now().date()
    monday = now - timedelta(days = now.weekday())
    # get the week from the weeks dictionary
    week = weeks[monday]

    # list of dicts which will hold th results to be displayed on the screen
    results = []

    # get the first week and current week's weights from the db
    # if the week is > 3, then grab last week's number to which can be used as a fallback if the user hasn't entered their weight for the current week
    if week < 2:
        # nothing exciting to show, just grab the users in the competition
        rows = db.execute("SELECT users.username, users.display_name FROM users JOIN weight on weight.user_id = users.id")
        results = rows
        # update results for % lost to none
        for result in results:
            result['lost'] = None
        return render_template("results.html", results=results)
    elif week < 3:
        # can only get 2 weeks of data
        rows = db.execute("SELECT users.username, users.display_name, weight.'1', weight.:week \
            FROM users JOIN weight on weight.user_id = users.id", week=str(week))
        for row in rows:
            # calculate # of weight gained/lost as long as there is a value
            if row['1'] != None and row[str(week)] != None:
                lost = percent_diff(row['1'], row[str(week)])
            else:
                lost = None
            # update results with dictionary
            results.append({'username': row['username'], 'display_name': row['display_name'], 'lost': lost})
        # sort dict in reverse order
        results = sorted(results, key = lambda i: i['lost'], reverse=True)
        return render_template("results.html", results=results)
    else:
        # get the first week, last week, and this week.  If this week isn't filled in yet, use last week's number for the diff
        rows = db.execute("SELECT users.username, users.display_name, weight.'1', weight.:last, weight.:week \
            FROM users JOIN weight on weight.user_id = users.id", last=str(week-1), week=str(week))
        for row in rows:
            # calculate # of weight gained/lost as long as there is a value
            if row['1'] != None and row[str(week)] != None:
                lost = percent_diff(row['1'], row[str(week)])
            # No weight provided for this week yet, try to use last week's weight
            elif row['1'] != None and row[str(week -1)] != None:
                lost = percent_diff(row['1'], row[str(week - 1)])
            # if no weights, go with none
            else:
                lost = None
            # update results with dictionary
            results.append({'username': row['username'], 'display_name': row['display_name'], 'lost': lost})
        # sort dict in reverse order must use or 0.0 to account for users not entering weight yet
        results = sorted(results, key = lambda i: i['lost'] or 0.0, reverse=True)
        return render_template("results.html", results=results)


@app.route("/weightadmin", methods=["GET"])
@login_required
def weightadmin():
    return render_template("weightadmin.html")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
