"""update Users

Revision ID: 577c1b884325
Revises: 519ea9554950
Create Date: 2023-12-13 04:52:18.528170

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '577c1b884325'
down_revision = '519ea9554950'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('Users', schema=None) as batch_op:
        batch_op.drop_constraint('Users_phone_number_key', type_='unique')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('Users', schema=None) as batch_op:
        batch_op.create_unique_constraint('Users_phone_number_key', ['phone_number'])

    # ### end Alembic commands ###
