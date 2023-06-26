"""empty message

Revision ID: c8afdf83ba38
Revises: 807ea060bb65
Create Date: 2023-06-26 15:45:04.251754

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c8afdf83ba38'
down_revision = '807ea060bb65'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('day_ratings', sa.Column('notes_rating', sa.Boolean(), nullable=True))
    op.add_column('day_ratings', sa.Column('health', sa.Boolean(), nullable=True))
    op.drop_column('day_ratings', 'tasks_rating')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('day_ratings', sa.Column('tasks_rating', sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.drop_column('day_ratings', 'health')
    op.drop_column('day_ratings', 'notes_rating')
    # ### end Alembic commands ###