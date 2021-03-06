"""change auction number to integers

Revision ID: 3b123dcdb50f
Revises: 
Create Date: 2019-04-07 07:30:13.304011

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3b123dcdb50f'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('auction',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('auction_number', sa.Integer(), nullable=False),
    sa.Column('auction_loc', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('car',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('car_brand', sa.String(), nullable=False),
    sa.Column('car_name', sa.String(), nullable=False),
    sa.Column('year', sa.Integer(), nullable=True),
    sa.Column('transmission', sa.String(length=50), nullable=True),
    sa.Column('fuel_type', sa.String(length=50), nullable=True),
    sa.Column('engine_size', sa.Integer(), nullable=True),
    sa.Column('kilos', sa.Integer(), nullable=True),
    sa.Column('auction_id', sa.Integer(), nullable=True),
    sa.Column('auction_car_id', sa.Integer(), nullable=True),
    sa.Column('car_img_src', sa.String(length=255), nullable=True),
    sa.Column('car_color', sa.String(length=50), nullable=True),
    sa.Column('car_type', sa.String(length=255), nullable=True),
    sa.Column('car_owner', sa.String(length=255), nullable=True),
    sa.Column('car_reputation', sa.String(length=255), nullable=True),
    sa.Column('car_auction_start_price', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['auction_id'], ['auction.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('car')
    op.drop_table('auction')
    # ### end Alembic commands ###
