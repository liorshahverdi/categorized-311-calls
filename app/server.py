from flask import Flask, render_template, url_for
import pandas as pd 
import os

app = Flask(__name__)

@app.route("/index", methods=["GET","POST"])
def index():
	return render_template('index.html')

app.run(debug=True)