"""empty message

Revision ID: f2a6c762e00c
Revises: f6f8a7c5ded3
Create Date: 2020-05-16 13:31:58.958287

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f2a6c762e00c'
down_revision = 'f6f8a7c5ded3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('artist', sa.Column('seeking_description', sa.String(), nullable=True))
    op.add_column('artist', sa.Column('seeking_talent', sa.Boolean(), nullable=True))
    op.add_column('artist', sa.Column('website_link', sa.String(length=120), nullable=True))
    op.add_column('venue', sa.Column('seeking_description', sa.String(), nullable=True))
    op.add_column('venue', sa.Column('seeking_talent', sa.Boolean(), nullable=True))
    op.add_column('venue', sa.Column('website_link', sa.String(length=120), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('venue', 'website_link')
    op.drop_column('venue', 'seeking_talent')
    op.drop_column('venue', 'seeking_description')
    op.drop_column('artist', 'website_link')
    op.drop_column('artist', 'seeking_talent')
    op.drop_column('artist', 'seeking_description')
    # ### end Alembic commands ###
