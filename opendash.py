# -*- coding: utf-8 -*-

from flask import Flask, render_template

app = Flask(__name__)

@app.route("/report")
def show_chart():

    return render_template('report.html')

if __name__ == "__main__":
    app.run(debug=True)