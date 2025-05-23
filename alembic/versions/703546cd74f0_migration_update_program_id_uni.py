"""MIGRATION=update_program_id_uni

Revision ID: 703546cd74f0
Revises: dc9d2b7bc296
Create Date: 2025-04-11 17:07:36.208796

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '703546cd74f0'
down_revision: Union[str, None] = 'dc9d2b7bc296'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('program', sa.Column('university_id', sa.Integer(), nullable=False))
    op.drop_index('ix_program_scores_gin', table_name='program', postgresql_using='gin')
    op.create_unique_constraint(None, 'program', ['university_id'])
    op.drop_constraint('program_vuz_long_name_fkey', 'program', type_='foreignkey')
    op.create_foreign_key(None, 'program', 'universities', ['university_id'], ['id'])
    op.drop_column('program', 'vuz_long_name')
    op.drop_column('program', 'scores')
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('program', sa.Column('scores', postgresql.JSONB(astext_type=sa.Text()), autoincrement=False, nullable=True))
    op.add_column('program', sa.Column('vuz_long_name', sa.TEXT(), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'program', type_='foreignkey')
    op.create_foreign_key('program_vuz_long_name_fkey', 'program', 'universities', ['vuz_long_name'], ['long_name'])
    op.drop_constraint(None, 'program', type_='unique')
    op.create_index('ix_program_scores_gin', 'program', ['scores'], unique=False, postgresql_using='gin')
    op.drop_column('program', 'university_id')
    # ### end Alembic commands ###
