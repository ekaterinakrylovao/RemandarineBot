"""new_migration_name

Revision ID: 0122a1620b37
Revises: 
Create Date: 2024-05-19 20:40:29.949785

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0122a1620b37'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.String(length=100), nullable=False),
    sa.Column('username', sa.String(length=100), nullable=True),
    sa.Column('first_name', sa.String(length=100), nullable=True),
    sa.Column('last_name', sa.String(length=100), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('cases',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.String(length=100), nullable=True),
    sa.Column('name', sa.String(length=100), nullable=True),
    sa.Column('start_date', sa.DateTime(), nullable=False),
    sa.Column('description', sa.String(length=100), nullable=True),
    sa.Column('deadline_date', sa.DateTime(), nullable=True),
    sa.Column('repeat', sa.String(length=100), nullable=True),
    sa.Column('is_finished', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('file',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('case_id', sa.Integer(), nullable=True),
    sa.Column('file_name', sa.String(length=100), nullable=True),
    sa.Column('file_url', sa.String(length=100), nullable=True),
    sa.ForeignKeyConstraint(['case_id'], ['cases.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('file')
    op.drop_table('cases')
    op.drop_table('users')
    # ### end Alembic commands ###
