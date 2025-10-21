from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0001_create_files_table'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        'files',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('filename', sa.String(length=255), nullable=False),
        sa.Column('mime_type', sa.String(length=127), nullable=False),
        sa.Column('size', sa.Integer(), nullable=False),
        sa.Column('bucket', sa.String(length=63), nullable=False),
        sa.Column('object_key', sa.String(length=512), nullable=False, unique=True),
        sa.Column('message_id', sa.String(length=36), nullable=True),
        sa.Column('thread_id', sa.String(length=36), nullable=True),
        sa.Column('checksum_sha256', sa.String(length=64), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    )

def downgrade() -> None:
    op.drop_table('files')
