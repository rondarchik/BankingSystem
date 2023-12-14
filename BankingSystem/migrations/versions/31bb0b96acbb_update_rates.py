"""update Rates

Revision ID: 31bb0b96acbb
Revises: 71e7efbe92e3
Create Date: 2023-12-13 05:23:46.851911

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '31bb0b96acbb'
down_revision = '71e7efbe92e3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('CurrencyRates', schema=None) as batch_op:
        batch_op.add_column(sa.Column('rate_type', sa.Integer(), nullable=False))
        batch_op.create_foreign_key(None, 'RateTypes', ['rate_type'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('CurrencyRates', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('rate_type')

    # ### end Alembic commands ###
