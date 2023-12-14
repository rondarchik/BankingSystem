"""update tables

Revision ID: f2f03b046635
Revises: 39b2deae7cac
Create Date: 2023-12-13 22:38:43.814700

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f2f03b046635'
down_revision = '39b2deae7cac'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('Departments', schema=None) as batch_op:
        batch_op.alter_column('department_address',
               existing_type=sa.VARCHAR(length=200),
               nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('Departments', schema=None) as batch_op:
        batch_op.alter_column('department_address',
               existing_type=sa.VARCHAR(length=200),
               nullable=True)

    # ### end Alembic commands ###
