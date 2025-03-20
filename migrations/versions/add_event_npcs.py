"""add event npcs association table

Revision ID: add_event_npcs
Revises: update_npc_model
Create Date: 2024-03-19 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_event_npcs'
down_revision = 'update_npc_model'
branch_labels = None
depends_on = None


def upgrade():
    # Create event_npcs table
    op.create_table('event_npcs',
        sa.Column('event_id', sa.Integer(), nullable=False),
        sa.Column('npc_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['event_id'], ['event.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['npc_id'], ['npc.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('event_id', 'npc_id')
    )


def downgrade():
    # Drop event_npcs table
    op.drop_table('event_npcs') 