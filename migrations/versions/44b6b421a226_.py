"""empty message

Revision ID: 44b6b421a226
Revises: b014ba5a3e8b
Create Date: 2023-02-01 17:30:18.028458

"""
from uuid import uuid4
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from models import Message
# revision identifiers, used by Alembic.
revision = '44b6b421a226'
down_revision = 'b014ba5a3e8b'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    session = sa.orm.Session(bind=bind)

    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('message', schema=None) as batch_op:
        batch_op.add_column(sa.Column('uuid', postgresql.UUID(as_uuid=True), nullable=True))

    for msg in session.query(Message):
        msg.uuid = uuid4()

    session.commit()
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('message', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='unique')
        batch_op.drop_column('uuid')

    # ### end Alembic commands ###