"""Add extended support module tables

Revision ID: 012
Revises: 011
Create Date: 2025-01-16 10:00:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '012'
down_revision = '011'
branch_labels = None
depends_on = None


def upgrade():
    """Create support module tables"""

    # 1. Update existing tickets table (if it exists, add new fields)
    # Note: Ticket table already exists, just add replies relationship support

    # 2. Create ticket_replies table
    op.create_table(
        'ticket_replies',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('ticket_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('message', sa.Text(), nullable=False, comment='Reply message content'),
        sa.Column('is_internal', sa.Integer(), default=0, comment='Whether this is an internal note'),
        sa.ForeignKeyConstraint(['ticket_id'], ['tickets.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        comment='Ticket replies for threaded conversations'
    )
    op.create_index('ix_ticket_replies_ticket_id', 'ticket_replies', ['ticket_id'])
    op.create_index('ix_ticket_replies_user_id', 'ticket_replies', ['user_id'])

    # 3. Create kb_articles table (Knowledge Base)
    op.create_table(
        'kb_articles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('slug', sa.String(255), nullable=False, unique=True, comment='URL-friendly slug'),
        sa.Column('title', sa.String(255), nullable=False, comment='Article title'),
        sa.Column('content', sa.Text(), nullable=False, comment='Article content (Markdown)'),
        sa.Column('summary', sa.String(500), nullable=True, comment='Short summary'),
        sa.Column('category', sa.String(100), nullable=False, comment='Article category'),
        sa.Column('tags', sa.Text(), nullable=True, comment='Comma-separated tags'),
        sa.Column('status', sa.Enum('draft', 'published', 'archived', name='articlestatus'),
                 nullable=False, default='draft', comment='Publication status'),
        sa.Column('version', sa.Integer(), default=1, nullable=False, comment='Article version'),
        sa.Column('author_id', sa.Integer(), nullable=False, comment='Article author'),
        sa.Column('view_count', sa.Integer(), default=0, nullable=False, comment='View count'),
        sa.Column('helpful_count', sa.Integer(), default=0, nullable=False, comment='Helpful votes'),
        sa.Column('not_helpful_count', sa.Integer(), default=0, nullable=False, comment='Not helpful votes'),
        sa.Column('meta_description', sa.String(255), nullable=True, comment='SEO meta description'),
        sa.ForeignKeyConstraint(['author_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        comment='Knowledge base articles'
    )
    op.create_index('ix_kb_articles_slug', 'kb_articles', ['slug'], unique=True)
    op.create_index('ix_kb_articles_title', 'kb_articles', ['title'])
    op.create_index('ix_kb_articles_category', 'kb_articles', ['category'])
    op.create_index('ix_kb_articles_status', 'kb_articles', ['status'])
    op.create_index('ix_kb_articles_author_id', 'kb_articles', ['author_id'])

    # 4. Create faqs table
    op.create_table(
        'faqs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('question', sa.String(500), nullable=False, comment='FAQ question'),
        sa.Column('answer', sa.Text(), nullable=False, comment='FAQ answer (Markdown)'),
        sa.Column('category', sa.String(100), nullable=False, comment='FAQ category'),
        sa.Column('order', sa.Integer(), default=0, nullable=False, comment='Display order'),
        sa.Column('is_active', sa.Boolean(), default=True, nullable=False, comment='Active status'),
        sa.Column('view_count', sa.Integer(), default=0, nullable=False, comment='View count'),
        sa.PrimaryKeyConstraint('id'),
        comment='Frequently asked questions'
    )
    op.create_index('ix_faqs_question', 'faqs', ['question'])
    op.create_index('ix_faqs_category', 'faqs', ['category'])
    op.create_index('ix_faqs_is_active', 'faqs', ['is_active'])

    # 5. Create chat_sessions table
    op.create_table(
        'chat_sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('session_id', sa.String(50), nullable=False, unique=True, comment='Unique session ID'),
        sa.Column('customer_id', sa.Integer(), nullable=False, comment='Customer user ID'),
        sa.Column('agent_id', sa.Integer(), nullable=True, comment='Support agent user ID'),
        sa.Column('status', sa.Enum('waiting', 'active', 'ended', 'transferred', name='chatstatus'),
                 nullable=False, default='waiting', comment='Session status'),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True, comment='When agent joined'),
        sa.Column('ended_at', sa.DateTime(timezone=True), nullable=True, comment='When session ended'),
        sa.Column('initial_message', sa.String(500), nullable=True, comment='Initial customer message'),
        sa.ForeignKeyConstraint(['customer_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['agent_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        comment='Live chat sessions'
    )
    op.create_index('ix_chat_sessions_session_id', 'chat_sessions', ['session_id'], unique=True)
    op.create_index('ix_chat_sessions_customer_id', 'chat_sessions', ['customer_id'])
    op.create_index('ix_chat_sessions_agent_id', 'chat_sessions', ['agent_id'])
    op.create_index('ix_chat_sessions_status', 'chat_sessions', ['status'])

    # 6. Create chat_messages table
    op.create_table(
        'chat_messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('session_id', sa.Integer(), nullable=False, comment='Chat session ID'),
        sa.Column('sender_id', sa.Integer(), nullable=False, comment='Message sender user ID'),
        sa.Column('message', sa.Text(), nullable=False, comment='Message content'),
        sa.Column('is_agent', sa.Boolean(), default=False, nullable=False, comment='Is from agent'),
        sa.Column('is_system', sa.Boolean(), default=False, nullable=False, comment='Is system message'),
        sa.ForeignKeyConstraint(['session_id'], ['chat_sessions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['sender_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        comment='Chat messages'
    )
    op.create_index('ix_chat_messages_session_id', 'chat_messages', ['session_id'])
    op.create_index('ix_chat_messages_sender_id', 'chat_messages', ['sender_id'])

    # 7. Create feedbacks table
    op.create_table(
        'feedbacks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True, comment='User who submitted feedback'),
        sa.Column('subject', sa.String(255), nullable=False, comment='Feedback subject'),
        sa.Column('message', sa.Text(), nullable=False, comment='Feedback message'),
        sa.Column('category', sa.Enum('general', 'feature_request', 'bug_report', 'complaint',
                                      'compliment', 'suggestion', name='feedbackcategory'),
                 nullable=False, comment='Feedback category'),
        sa.Column('rating', sa.Integer(), nullable=True, comment='Rating 1-5 stars'),
        sa.Column('status', sa.Enum('new', 'reviewed', 'in_progress', 'completed', 'dismissed',
                                    name='feedbackstatus'),
                 nullable=False, default='new', comment='Processing status'),
        sa.Column('response', sa.Text(), nullable=True, comment='Response to feedback'),
        sa.Column('responded_by', sa.Integer(), nullable=True, comment='User who responded'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['responded_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        comment='Customer feedback'
    )
    op.create_index('ix_feedbacks_user_id', 'feedbacks', ['user_id'])
    op.create_index('ix_feedbacks_category', 'feedbacks', ['category'])
    op.create_index('ix_feedbacks_status', 'feedbacks', ['status'])


def downgrade():
    """Drop support module tables"""

    # Drop tables in reverse order (respecting foreign key constraints)
    op.drop_table('feedbacks')
    op.drop_table('chat_messages')
    op.drop_table('chat_sessions')
    op.drop_table('faqs')
    op.drop_table('kb_articles')
    op.drop_table('ticket_replies')

    # Drop enums
    op.execute('DROP TYPE IF EXISTS feedbackstatus')
    op.execute('DROP TYPE IF EXISTS feedbackcategory')
    op.execute('DROP TYPE IF EXISTS chatstatus')
    op.execute('DROP TYPE IF EXISTS articlestatus')
