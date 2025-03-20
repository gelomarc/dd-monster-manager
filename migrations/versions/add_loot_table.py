"""add loot table

Revision ID: add_loot_table
Revises: e75cf71e1a77
Create Date: 2024-03-19 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_loot_table'
down_revision = 'e75cf71e1a77'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('loot',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('quantity', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('value', sa.String(length=50), nullable=True),
        sa.Column('rarity', sa.String(length=50), nullable=True),
        sa.Column('attunement', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('encounter_id', sa.Integer(), nullable=False),
        sa.Column('campaign_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'), onupdate=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['campaign_id'], ['campaign.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['encounter_id'], ['encounter.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_loot_campaign_id'), 'loot', ['campaign_id'], unique=False)
    op.create_index(op.f('ix_loot_encounter_id'), 'loot', ['encounter_id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_loot_encounter_id'), table_name='loot')
    op.drop_index(op.f('ix_loot_campaign_id'), table_name='loot')
    op.drop_table('loot') 