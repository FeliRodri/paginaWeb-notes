"""Añadir reminder

Revision ID: a29458222b73
Revises: 3227570e0346
Create Date: 2023-11-25 12:22:17.772281

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a29458222b73'
down_revision = '3227570e0346'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('note', schema=None) as batch_op:
        batch_op.add_column(sa.Column('reminder', sa.DateTime(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('note', schema=None) as batch_op:
        batch_op.drop_column('reminder')

    # ### end Alembic commands ###
