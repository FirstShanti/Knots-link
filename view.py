from app import app
from flask import render_template


@app.route('/')
def index():
    return render_template('index.html')

@app.errorhandler(404)
def error_404(page):
	return render_template('error404.html')