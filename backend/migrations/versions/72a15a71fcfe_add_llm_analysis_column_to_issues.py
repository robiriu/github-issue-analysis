"""Add llm_analysis column to issues

Revision ID: 72a15a71fcfe
Revises: 6b040d5c6374
Create Date: 2025-05-01 16:45:44.229876

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '72a15a71fcfe'
down_revision: Union[str, None] = '6b040d5c6374'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('issues', sa.Column('llm_analysis', sa.Text(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('issues', 'llm_analysis')
    # ### end Alembic commands ###
