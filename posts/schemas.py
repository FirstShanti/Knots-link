from app import ma
# from flask_marshmallow import SQLAlchemySchema
from models import Post, Comment


class CommentSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Comment
        # include_fk = True

    id = ma.auto_field()
    text = ma.auto_field()
    created = ma.auto_field()
    edited = ma.auto_field()

comment_schema = CommentSchema()
comments_schema = CommentSchema(many=True)

class PostSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Post
    
    id = ma.auto_field()
    body = ma.auto_field()
    created = ma.auto_field()
    preview = ma.auto_field()
    title = ma.auto_field()
    visible = ma.auto_field()
    author = ma.auto_field()

    comments = ma.Nested(comments_schema, many=True)


post_schema = PostSchema()
posts_schema = PostSchema(many=True)