from datetime import datetime, timedelta
from app import app
from flask import render_template, request, make_response, url_for
from models import Post
from posts.blueprint import posts


@app.route('/', methods=['GET'])
def index():
	return render_template('index.html', endpoint=request.endpoint)

@app.route('/sitemap.xml', methods=['GET'])
def sitemap():
	try:
		"""Generate sitemap.xml. Makes a list of urls and date modified."""
		pages=[]
		ten_days_ago=(datetime.now() - timedelta(days=7)).date().isoformat()
		# static pages
		for rule in app.url_map.iter_rules():
		    if 'GET' in rule.methods \
		    	and len(rule.arguments) == 0 \
		    	and not rule.rule.startswith('/admin') \
		    	and rule.rule != '/blog/category/add':
		        pages.append([ f'{request.url_root}'[:-1:]  + rule.rule, ten_days_ago])

		posts = Post.query.all()

		for post in posts:
		    url = url_for('posts.post_content', slug=post.slug, _external=True)
		    modified_time = post.created.date().isoformat()
		    pages.append([url, modified_time])

		sitemap_xml = render_template('sitemap_template.xml', pages=pages)
		response= make_response(sitemap_xml)
		response.headers["Content-Type"] = "application/xml" 
		
		return response
	except Exception as e:
		return(str(e))

@app.errorhandler(404)
def error_404(page):
	return render_template('error404.html')