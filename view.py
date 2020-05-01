from app import app
from flask import render_template, request


@app.route('/', methods=['GET'])
def index():
	return render_template('index.html', endpoint=request.endpoint)

@app.errorhandler(404)
def error_404(page):
	return render_template('error404.html')