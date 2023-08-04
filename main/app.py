import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from datetime import datetime
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    user_id = session["user_id"]
    username = db.execute("SELECT username FROM users WHERE id = ?", user_id)[0]["username"]

    #get user's data of stock
    portfolio = db.execute("SELECT * FROM purchases WHERE username = :username", username = username)

    #initial cash amount
    cash = db.execute("SELECT * FROM users WHERE id = ?", user_id)[0]["cash"]

    #cash earned from stocks
    earnings = 0

    #total earnings
    for stock in portfolio:
        symbol = stock["name"]
        shares = stock["shares"]
        stock_info = lookup(symbol)

        pps = stock_info["price"]
        total = shares*pps #updated_price

        earnings += float(total)

        db.execute("UPDATE purchases SET price = :total, pps = :pps WHERE username = :username AND name = :name", total = usd(total), pps = usd(pps), username = username, name = symbol)

    total_cash = float(cash + earnings)

    return render_template("index.html", cash=usd(cash), portfolio = portfolio, total_cash = usd(total_cash))

@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":
        try:
            symbol = request.form.get("symbol")
        except:
            return apology("must provide symbol")

        quote = lookup(symbol)

        try:
            shares = int(request.form.get("shares"))
        except:
            return apology("must provide shares")

        if not quote:
            return apology("must provide valid symbol")
        elif shares <= 0:
            return apology("must provide postitive shares number")

        user_id = session["user_id"]
        cash = db.execute("SELECT * FROM users WHERE id = ?", user_id)[0]["cash"]

        price = quote["price"]
        total_price = price*shares

        if total_price > float(cash):
            return apology("not enough cash")

        username = db.execute("SELECT username FROM users WHERE id = ?", user_id)[0]["username"]

        now = datetime.now()
        formatted_date = now.strftime("%Y-%m-%d %H:%M:%S")

        #checking if user has already bought shares
        rows = db.execute("SELECT * FROM purchases WHERE name = :name AND username = :username", name = symbol, username = username)
        if len(rows) != 0:
            num_shares = int(db.execute("SELECT * FROM purchases WHERE name = :name AND username = :username", name = symbol, username = username)[0]["shares"]) + shares
            updated_price = float(db.execute("SELECT * FROM purchases WHERE name = :name AND username = :username", name = symbol, username = username)[0]["updated_price"]) + total_price
            db.execute("UPDATE purchases SET pps = :price, shares = :shares, updated_price=:total_price, price = :table_price WHERE username = :username AND name = :name", price = usd(price), shares = num_shares, total_price = updated_price, table_price = usd(updated_price), username = username, name = symbol)
        else:
            db.execute("INSERT INTO purchases (username, pps, name, shares, updated_price, price, date) VALUES(?, ?, ?, ?, ?, ?, ?)", username, usd(price), symbol, shares, total_price, usd(updated_price), formatted_date)

        db.execute("INSERT INTO history (username, date, action, name, price, shares) VALUES(?, ?, ?, ?, ?, ?)", username, formatted_date, "BOUGHT", symbol, usd(total_price), shares)
        db.execute("UPDATE users SET cash = ? WHERE id = ?", cash-total_price, user_id)

        #Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("buy.html")

@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    user_id = session["user_id"]
    username = db.execute("SELECT username FROM users WHERE id = ?", user_id)[0]["username"]

    histories = db.execute("SELECT * FROM history WHERE username = ?", username)

    cash = db.execute("SELECT * FROM users WHERE id = ?", user_id)[0]["cash"]

    return render_template("history.html", cash = cash, histories = histories)


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
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

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


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""

    if request.method == "POST":
        symbol = request.form.get("symbol").upper()

        #If user leaves entry blank
        if not symbol:
            return apology("must provide symbol")

        #get data of provided symbol
        quote = lookup(symbol)

        #if symbol not valid
        if not quote:
            return apology("must provide accurate symbol")

        return render_template("quoted.html", quote=quote)

    #user reached route via GET
    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        hash = generate_password_hash(password)

        #ensure username submitted
        if not username:
            return apology("must provide username")

        #ensure password submitted
        elif not password:
            return apology("must provide password")

        #esnure password re-submitted
        elif not confirmation:
            return apology("must re-enter password")

        #ensure password matches confirmation
        elif confirmation != password:
            return apology("passwords do not match")

        #check if username is taken
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)
        if len(rows) != 0:
            return apology("username is taken")

        #Insert new user into users
        new_user = db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", username, hash)

        #Remember which user has logged in
        session["user_id"] = new_user

        #Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    if request.method == "POST":
        try:
            symbol = request.form.get("symbol")
        except:
            return apology("must provide symbol")

        shares = int(request.form.get("shares"))
        if shares < 1:
            return apology("must provide valid shares")

        user_id = session["user_id"]
        username = db.execute("SELECT username FROM users WHERE id = ?", user_id)[0]["username"]

        #checking if user has the stock/shares of stock
        row = db.execute("SELECT * FROM purchases WHERE name = :name AND username = :username", name = symbol, username = username)
        if len(row) == 0:
            return apology("failure to sell stock")
        elif int(row[0]["shares"]) < shares:
            return apology("not enough shares to sell")

        pps = lookup(symbol)["price"]
        earnings = pps*shares

        #insert time and date
        now = datetime.now()
        formatted_date = now.strftime("%Y-%m-%d %H:%M:%S")

        db.execute("INSERT INTO stock_sold (username, name, shares, pps, earnings, date) VALUES (?, ?, ?, ?, ?, ?)", username, symbol, shares, pps, earnings, formatted_date)

        #remove from purchases
        new_shares = int(row[0]["shares"]) - shares

        if new_shares < 1:
            db.execute("DELETE FROM purchases WHERE name = :name AND username = :username", name = symbol, username = username)
            return redirect("/")
        else:
            db.execute("UPDATE purchases SET shares = :shares WHERE username = :username AND name = :name", shares = new_shares, username = username, name = symbol)

        #update cash
        cash_val = db.execute("SELECT * FROM users WHERE id = ?", user_id)[0]["cash"]
        cash_val += earnings
        db.execute("UPDATE users SET cash = :cash WHERE id = :id", cash = cash_val, id = user_id)

        db.execute("INSERT INTO history (username, date, action, name, price, shares) VALUES(?, ?, ?, ?, ?, ?)", username, formatted_date, "SOLD", symbol, usd(earnings), shares)

        return redirect("/")

    else:
        return render_template("sell.html")
