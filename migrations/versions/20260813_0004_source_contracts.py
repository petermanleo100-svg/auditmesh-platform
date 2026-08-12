"""Tenant-scoped source heartbeat contracts."""
from alembic import op
import sqlalchemy as sa
revision="20260813_0004";down_revision="20260812_0003";branch_labels=None;depends_on=None
def upgrade():
 op.create_table("source_contracts",sa.Column("id",sa.Integer(),primary_key=True),sa.Column("tenant_id",sa.String(64),nullable=False),sa.Column("source_id",sa.String(100),nullable=False),sa.Column("principal_subject",sa.String(200),nullable=False),sa.Column("max_silence_seconds",sa.Integer(),nullable=False),sa.Column("enabled",sa.Integer(),nullable=False),sa.Column("last_success_at",sa.String(40)),sa.Column("last_failure_at",sa.String(40)),sa.Column("last_error_code",sa.String(50)),sa.Column("updated_at",sa.String(40),nullable=False),sa.UniqueConstraint("tenant_id","source_id"));op.create_index("ix_source_contracts_tenant_id","source_contracts",["tenant_id"])
 if op.get_bind().dialect.name=="postgresql":
  op.execute("ALTER TABLE source_contracts ENABLE ROW LEVEL SECURITY");op.execute("ALTER TABLE source_contracts FORCE ROW LEVEL SECURITY");op.execute("CREATE POLICY source_contracts_tenant_policy ON source_contracts USING (tenant_id = current_setting('app.tenant_id', true)) WITH CHECK (tenant_id = current_setting('app.tenant_id', true))")
def downgrade():
 count=op.get_bind().execute(sa.text("SELECT count(*) FROM source_contracts")).scalar_one()
 if count:raise RuntimeError("cannot downgrade source_contracts while registered sources exist; archive or remove them through an approved change")
 op.drop_table("source_contracts")
