"""update Rates

Revision ID: 8bbf076683e9
Revises: 31bb0b96acbb
Create Date: 2023-12-13 05:25:41.731361

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8bbf076683e9'
down_revision = '31bb0b96acbb'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('CurrencyRates', schema=None) as batch_op:
        batch_op.add_column(sa.Column('from_currency_id', sa.Integer(), nullable=False))
        batch_op.add_column(sa.Column('to_currency_id', sa.Integer(), nullable=False))
        batch_op.drop_constraint('CurrencyRates_currency_id_fkey', type_='foreignkey')
        batch_op.create_foreign_key(None, 'Currencies', ['to_currency_id'], ['id'])
        batch_op.create_foreign_key(None, 'Currencies', ['from_currency_id'], ['id'])
        batch_op.drop_column('currency_id')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('CurrencyRates', schema=None) as batch_op:
        batch_op.add_column(sa.Column('currency_id', sa.INTEGER(), autoincrement=False, nullable=False))
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key('CurrencyRates_currency_id_fkey', 'Currencies', ['currency_id'], ['id'])
        batch_op.drop_column('to_currency_id')
        batch_op.drop_column('from_currency_id')

    # ### end Alembic commands ###
