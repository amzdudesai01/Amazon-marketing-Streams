"""Initial migration

Revision ID: 001
Revises: 
Create Date: 2024-01-15 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create stream_messages table
    op.create_table(
        'stream_messages',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('message_id', sa.String(length=255), nullable=False),
        sa.Column('dataset_type', sa.Enum('SP', 'SB', 'SD', name='streamdatasettype'), nullable=False),
        sa.Column('profile_id', sa.String(length=255), nullable=False),
        sa.Column('raw_data', sa.Text(), nullable=False),
        sa.Column('processed', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('processed_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_stream_messages_message_id'), 'stream_messages', ['message_id'], unique=True)
    op.create_index(op.f('ix_stream_messages_dataset_type'), 'stream_messages', ['dataset_type'], unique=False)
    op.create_index(op.f('ix_stream_messages_profile_id'), 'stream_messages', ['profile_id'], unique=False)
    op.create_index(op.f('ix_stream_messages_processed'), 'stream_messages', ['processed'], unique=False)
    op.create_index(op.f('ix_stream_messages_created_at'), 'stream_messages', ['created_at'], unique=False)

    # Create performance_data table
    op.create_table(
        'performance_data',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('stream_message_id', sa.BigInteger(), nullable=False),
        sa.Column('dataset_type', sa.Enum('SP', 'SB', 'SD', name='streamdatasettype'), nullable=False),
        sa.Column('profile_id', sa.String(length=255), nullable=False),
        sa.Column('campaign_id', sa.String(length=255), nullable=False),
        sa.Column('campaign_name', sa.String(length=500), nullable=True),
        sa.Column('ad_group_id', sa.String(length=255), nullable=True),
        sa.Column('ad_group_name', sa.String(length=500), nullable=True),
        sa.Column('keyword_id', sa.String(length=255), nullable=True),
        sa.Column('keyword_text', sa.String(length=500), nullable=True),
        sa.Column('asin', sa.String(length=20), nullable=True),
        sa.Column('impressions', sa.Integer(), nullable=True),
        sa.Column('clicks', sa.Integer(), nullable=True),
        sa.Column('cost', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('sales', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('orders', sa.Integer(), nullable=True),
        sa.Column('units_sold', sa.Integer(), nullable=True),
        sa.Column('ctr', sa.Numeric(precision=5, scale=4), nullable=True),
        sa.Column('cpc', sa.Numeric(precision=10, scale=4), nullable=True),
        sa.Column('acos', sa.Numeric(precision=5, scale=4), nullable=True),
        sa.Column('roas', sa.Numeric(precision=10, scale=4), nullable=True),
        sa.Column('conversion_rate', sa.Numeric(precision=5, scale=4), nullable=True),
        sa.Column('start_date', sa.DateTime(), nullable=False),
        sa.Column('end_date', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['stream_message_id'], ['stream_messages.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_performance_data_stream_message_id'), 'performance_data', ['stream_message_id'], unique=False)
    op.create_index(op.f('ix_performance_data_dataset_type'), 'performance_data', ['dataset_type'], unique=False)
    op.create_index(op.f('ix_performance_data_profile_id'), 'performance_data', ['profile_id'], unique=False)
    op.create_index(op.f('ix_performance_data_campaign_id'), 'performance_data', ['campaign_id'], unique=False)
    op.create_index(op.f('ix_performance_data_ad_group_id'), 'performance_data', ['ad_group_id'], unique=False)
    op.create_index(op.f('ix_performance_data_keyword_id'), 'performance_data', ['keyword_id'], unique=False)
    op.create_index(op.f('ix_performance_data_asin'), 'performance_data', ['asin'], unique=False)
    op.create_index(op.f('ix_performance_data_start_date'), 'performance_data', ['start_date'], unique=False)
    op.create_index('idx_performance_campaign_date', 'performance_data', ['campaign_id', 'start_date'], unique=False)
    op.create_index('idx_performance_profile_date', 'performance_data', ['profile_id', 'start_date'], unique=False)

    # Create performance_aggregates table
    op.create_table(
        'performance_aggregates',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('performance_data_id', sa.BigInteger(), nullable=False),
        sa.Column('dataset_type', sa.Enum('SP', 'SB', 'SD', name='streamdatasettype'), nullable=False),
        sa.Column('profile_id', sa.String(length=255), nullable=False),
        sa.Column('campaign_id', sa.String(length=255), nullable=False),
        sa.Column('period_type', sa.String(length=20), nullable=False),
        sa.Column('period_start', sa.DateTime(), nullable=False),
        sa.Column('period_end', sa.DateTime(), nullable=False),
        sa.Column('total_impressions', sa.Integer(), nullable=True),
        sa.Column('total_clicks', sa.Integer(), nullable=True),
        sa.Column('total_cost', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('total_sales', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('total_orders', sa.Integer(), nullable=True),
        sa.Column('total_units_sold', sa.Integer(), nullable=True),
        sa.Column('avg_ctr', sa.Numeric(precision=5, scale=4), nullable=True),
        sa.Column('avg_cpc', sa.Numeric(precision=10, scale=4), nullable=True),
        sa.Column('avg_acos', sa.Numeric(precision=5, scale=4), nullable=True),
        sa.Column('avg_roas', sa.Numeric(precision=10, scale=4), nullable=True),
        sa.Column('avg_conversion_rate', sa.Numeric(precision=5, scale=4), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['performance_data_id'], ['performance_data.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_performance_aggregates_performance_data_id'), 'performance_aggregates', ['performance_data_id'], unique=False)
    op.create_index(op.f('ix_performance_aggregates_dataset_type'), 'performance_aggregates', ['dataset_type'], unique=False)
    op.create_index(op.f('ix_performance_aggregates_profile_id'), 'performance_aggregates', ['profile_id'], unique=False)
    op.create_index(op.f('ix_performance_aggregates_campaign_id'), 'performance_aggregates', ['campaign_id'], unique=False)
    op.create_index(op.f('ix_performance_aggregates_period_type'), 'performance_aggregates', ['period_type'], unique=False)
    op.create_index(op.f('ix_performance_aggregates_period_start'), 'performance_aggregates', ['period_start'], unique=False)
    op.create_index('idx_aggregate_unique', 'performance_aggregates', ['campaign_id', 'period_type', 'period_start'], unique=True)

    # Create alerts table
    op.create_table(
        'alerts',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('alert_type', sa.String(length=50), nullable=False),
        sa.Column('severity', sa.String(length=20), nullable=False),
        sa.Column('campaign_id', sa.String(length=255), nullable=False),
        sa.Column('campaign_name', sa.String(length=500), nullable=True),
        sa.Column('profile_id', sa.String(length=255), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('metric_value', sa.Numeric(precision=10, scale=4), nullable=True),
        sa.Column('threshold_value', sa.Numeric(precision=10, scale=4), nullable=True),
        sa.Column('previous_value', sa.Numeric(precision=10, scale=4), nullable=True),
        sa.Column('sent', sa.Boolean(), nullable=True),
        sa.Column('sent_at', sa.DateTime(), nullable=True),
        sa.Column('acknowledged', sa.Boolean(), nullable=True),
        sa.Column('acknowledged_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_alerts_alert_type'), 'alerts', ['alert_type'], unique=False)
    op.create_index(op.f('ix_alerts_severity'), 'alerts', ['severity'], unique=False)
    op.create_index(op.f('ix_alerts_campaign_id'), 'alerts', ['campaign_id'], unique=False)
    op.create_index(op.f('ix_alerts_profile_id'), 'alerts', ['profile_id'], unique=False)
    op.create_index(op.f('ix_alerts_sent'), 'alerts', ['sent'], unique=False)
    op.create_index(op.f('ix_alerts_acknowledged'), 'alerts', ['acknowledged'], unique=False)
    op.create_index(op.f('ix_alerts_created_at'), 'alerts', ['created_at'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_alerts_created_at'), table_name='alerts')
    op.drop_index(op.f('ix_alerts_acknowledged'), table_name='alerts')
    op.drop_index(op.f('ix_alerts_sent'), table_name='alerts')
    op.drop_index(op.f('ix_alerts_profile_id'), table_name='alerts')
    op.drop_index(op.f('ix_alerts_campaign_id'), table_name='alerts')
    op.drop_index(op.f('ix_alerts_severity'), table_name='alerts')
    op.drop_index(op.f('ix_alerts_alert_type'), table_name='alerts')
    op.drop_table('alerts')
    
    op.drop_index('idx_aggregate_unique', table_name='performance_aggregates')
    op.drop_index(op.f('ix_performance_aggregates_period_start'), table_name='performance_aggregates')
    op.drop_index(op.f('ix_performance_aggregates_period_type'), table_name='performance_aggregates')
    op.drop_index(op.f('ix_performance_aggregates_campaign_id'), table_name='performance_aggregates')
    op.drop_index(op.f('ix_performance_aggregates_profile_id'), table_name='performance_aggregates')
    op.drop_index(op.f('ix_performance_aggregates_dataset_type'), table_name='performance_aggregates')
    op.drop_index(op.f('ix_performance_aggregates_performance_data_id'), table_name='performance_aggregates')
    op.drop_table('performance_aggregates')
    
    op.drop_index('idx_performance_profile_date', table_name='performance_data')
    op.drop_index('idx_performance_campaign_date', table_name='performance_data')
    op.drop_index(op.f('ix_performance_data_start_date'), table_name='performance_data')
    op.drop_index(op.f('ix_performance_data_asin'), table_name='performance_data')
    op.drop_index(op.f('ix_performance_data_keyword_id'), table_name='performance_data')
    op.drop_index(op.f('ix_performance_data_ad_group_id'), table_name='performance_data')
    op.drop_index(op.f('ix_performance_data_campaign_id'), table_name='performance_data')
    op.drop_index(op.f('ix_performance_data_profile_id'), table_name='performance_data')
    op.drop_index(op.f('ix_performance_data_dataset_type'), table_name='performance_data')
    op.drop_index(op.f('ix_performance_data_stream_message_id'), table_name='performance_data')
    op.drop_table('performance_data')
    
    op.drop_index(op.f('ix_stream_messages_created_at'), table_name='stream_messages')
    op.drop_index(op.f('ix_stream_messages_processed'), table_name='stream_messages')
    op.drop_index(op.f('ix_stream_messages_profile_id'), table_name='stream_messages')
    op.drop_index(op.f('ix_stream_messages_dataset_type'), table_name='stream_messages')
    op.drop_index(op.f('ix_stream_messages_message_id'), table_name='stream_messages')
    op.drop_table('stream_messages')
    
    # Drop enum types
    sa.Enum(name='streamdatasettype').drop(op.get_bind(), checkfirst=True)

