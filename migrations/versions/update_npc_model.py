"""update npc model

Revision ID: update_npc_model
Revises: add_loot_table
Create Date: 2024-03-19 11:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.models.npc import NPC


# revision identifiers, used by Alembic.
revision = 'update_npc_model'
down_revision = 'add_loot_table'
branch_labels = None
depends_on = None


def upgrade():
    # Drop temporary table if it exists
    connection = op.get_bind()
    session = Session(bind=connection)
    session.execute(text('DROP TABLE IF EXISTS npc_temp'))
    session.commit()
    
    # Create new table
    op.create_table(
        'npc_temp',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('role', sa.String(length=100), nullable=False),
        sa.Column('attitude', sa.String(length=20), nullable=False, server_default='neutral'),
        sa.Column('places_to_find', sa.Text(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('equipment', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('campaign_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['campaign_id'], ['campaign.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Copy data from old table
    session.execute(
        text('''
        INSERT INTO npc_temp (id, name, role, description, created_at, campaign_id)
        SELECT id, name, COALESCE(role, 'Unknown'), description, created_at, campaign_id
        FROM npc;
        ''')
    )
    session.commit()
    
    # Drop old table and rename new one
    op.drop_table('npc')
    op.rename_table('npc_temp', 'npc')


def downgrade():
    # Drop temporary table if it exists
    connection = op.get_bind()
    session = Session(bind=connection)
    session.execute(text('DROP TABLE IF EXISTS npc_old'))
    session.commit()
    
    # Create old table structure
    op.create_table(
        'npc_old',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('role', sa.String(length=100), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('campaign_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['campaign_id'], ['campaign.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Copy data back
    session.execute(
        text('''
        INSERT INTO npc_old (id, name, role, description, created_at, campaign_id)
        SELECT id, name, role, description, created_at, campaign_id
        FROM npc;
        ''')
    )
    session.commit()
    
    # Drop new table and rename old one
    op.drop_table('npc')
    op.rename_table('npc_old', 'npc') 