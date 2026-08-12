"""retain canonical raw event material for evidence verification"""
from alembic import op
import sqlalchemy as sa
revision="20260812_0002";down_revision="20260812_0001";branch_labels=None;depends_on=None
def upgrade(): op.add_column("control_events",sa.Column("raw_event_json",sa.Text(),nullable=False,server_default="{}"))
def downgrade(): op.drop_column("control_events","raw_event_json")
