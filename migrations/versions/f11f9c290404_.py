"""empty message

Revision ID: f11f9c290404
Revises: b072f2d496a8
Create Date: 2023-01-07 19:58:06.158603

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f11f9c290404'
down_revision = 'b072f2d496a8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('token_black_list',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('access_token', sa.String(length=256), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('token_black_list')
    # ### end Alembic commands ###
