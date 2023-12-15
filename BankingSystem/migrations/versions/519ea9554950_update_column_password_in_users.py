"""update column password in Users

Revision ID: 519ea9554950
Revises: 
Create Date: 2023-12-13 02:16:10.901030

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '519ea9554950'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('Users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('password_hash', sa.String(length=200), nullable=False))
        batch_op.drop_column('password')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('Users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('password', sa.VARCHAR(length=50), autoincrement=False, nullable=False))
        batch_op.drop_column('password_hash')

    # ### end Alembic commands ###