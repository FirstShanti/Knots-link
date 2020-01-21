"""empty message

Revision ID: 5f1207aaa403
Revises: 92b348ae5235
Create Date: 2019-12-28 01:49:37.434297

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '5f1207aaa403'
down_revision = '92b348ae5235'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('post_knot')
    op.add_column('post', sa.Column('author', sa.String(length=32), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('post', 'author')
    op.create_table('post_knot',
    sa.Column('post_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True),
    sa.Column('knot_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['knot_id'], ['knot.id'], name='post_knot_ibfk_1'),
    sa.ForeignKeyConstraint(['post_id'], ['post.id'], name='post_knot_ibfk_2'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    # ### end Alembic commands ###