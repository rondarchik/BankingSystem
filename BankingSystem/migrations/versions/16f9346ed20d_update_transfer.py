"""update transfer

Revision ID: 16f9346ed20d
Revises: cfcd86c5b498
Create Date: 2023-12-25 21:01:34.707232

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '16f9346ed20d'
down_revision = 'cfcd86c5b498'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('TransferRequests', schema=None) as batch_op:
        batch_op.drop_constraint('TransferRequests_from_user_key', type_='unique')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('TransferRequests', schema=None) as batch_op:
        batch_op.create_unique_constraint('TransferRequests_from_user_key', ['from_user'])

    # ### end Alembic commands ###
