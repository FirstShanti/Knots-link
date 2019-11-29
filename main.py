from app import app
from app import db
import view

from posts.blueprint import posts, about


app.register_blueprint(posts, url_prefix='/blog')
app.register_blueprint(about, url_prefix='/contacts')


if __name__ == '__main__':
    app.run()