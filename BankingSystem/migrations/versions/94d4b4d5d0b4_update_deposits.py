"""update deposits

Revision ID: 94d4b4d5d0b4
Revises: 3d1ecaae744c
Create Date: 2023-12-24 21:32:15.460420

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '94d4b4d5d0b4'
down_revision = '3d1ecaae744c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('Transactions', schema=None) as batch_op:
        batch_op.alter_column('from_account_id',
               existing_type=sa.INTEGER(),
               nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('Transactions', schema=None) as batch_op:
        batch_op.alter_column('from_account_id',
               existing_type=sa.INTEGER(),
               nullable=False)

    # ### end Alembic commands ###
