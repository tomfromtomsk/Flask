"""empty message

Revision ID: 00f00540c27b
Revises: 15db72513733
Create Date: 2018-11-01 12:13:49.815185

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '00f00540c27b'
down_revision = '15db72513733'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('period',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('type', sa.Enum('DAY', 'YEAR', name='periodtype'), nullable=False),
    sa.Column('year', sa.Integer(), nullable=False),
    sa.Column('month', sa.Integer(), nullable=True),
    sa.Column('week', sa.Integer(), nullable=True),
    sa.Column('day', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('snapshot', sa.Column('period_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'snapshot', 'period', ['period_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'snapshot', type_='foreignkey')
    op.drop_column('snapshot', 'period_id')
    op.drop_table('period')
    # ### end Alembic commands ###
