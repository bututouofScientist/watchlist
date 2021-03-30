from Watchlist import app
from flask import render_template


@app.errorhandler(404)
def page_not_found(e):
    return render_template("errors/404.html"), 404
