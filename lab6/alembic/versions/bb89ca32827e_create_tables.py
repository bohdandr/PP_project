"""Create tables

Revision ID: bb89ca32827e
Revises: 
Create Date: 2022-10-24 18:37:15.170969

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bb89ca32827e'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'user',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('username', sa.VARCHAR(32)),
        sa.Column('firstName', sa.VARCHAR(32)),
        sa.Column('lastName', sa.VARCHAR(32)),
        sa.Column('email', sa.VARCHAR(64)),
        sa.Column('password', sa.VARCHAR(128)),
        sa.Column('phone', sa.VARCHAR(32)),
        sa.Column('birthDate', sa.Date),
        sa.Column('wallet', sa.Float),
        sa.Column('userStatus', sa.Enum('0', '1'), default='1')
    )

    op.create_table(
        'transaction',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('sentByUser', sa.Integer, sa.ForeignKey("user.id")),
        sa.Column('sentToUser', sa.Integer, sa.ForeignKey("user.id")),
        sa.Column('value', sa.Float),
        # sa.Column('datePerformed', sa.Date),
        sa.Column('datePerformed', sa.DateTime, server_default=sa.func.current_timestamp())
    )


def downgrade() -> None:
    op.drop_table('transaction')
    op.drop_table('user')

