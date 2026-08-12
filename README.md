# AuditMesh Platform

可直接部署企业试点的事件驱动连续审计与 IT 内控缺陷运营平台。

- 版本化控制策略，将特权操作、备份与身份事件转为可解释缺陷案例。
- 租户级事件幂等、证据哈希、案例生命周期和乐观并发控制；PostgreSQL 原子冲突路径承受 24 路重复投递并返回同一案例。
- 基于严重性的 SLA 截止时间与逾期队列。
- 四眼关闭控制，事件责任人不能自行关闭缺陷。
- FastAPI/OpenAPI、非 root 容器与 GitHub CI。
- JWT 审计角色权限、令牌租户绑定和严格输入校验。
- PostgreSQL/Alembic、健康探针、请求追踪、安全响应头、Prometheus 指标与加固 Compose。
- PostgreSQL 强制 RLS、AES-256-GCM 加密备份、精确 Alembic 版本空库恢复与逐事件证据哈希验证。
- 2 MiB 请求限制、严格字段边界、统一数据库错误、结构化访问日志和管理员完整性接口。
- 生产默认 OIDC/JWKS（RS256/ES256、5 分钟密钥缓存）；HS256 仅允许显式受控例外。
- 版本化 Prometheus 告警规则经 `promtool` 校验；容器 CI 生成 SPDX SBOM，并阻断已有修复的 Critical 漏洞。
- 手动发布候选保留镜像归档、校验和、SBOM 与 GitHub attestations；仅 `vX.Y.Z` 标签可发布带不可变摘要和来源证明的 GHCR 镜像。

```bash
pip install -e ".[test]"
pytest -q
uvicorn auditmesh.api:create_app --factory --port 8000
```

企业试点使用 `.env.example`、`compose.yaml` 和 `docs/production-runbook.md`；迁移所有者与请求运行账号严格分离，API 启动前执行数据库角色、精确 Alembic 版本、强制 RLS、OIDC 与备份密钥准入检查。CI 验证迁移往返、PostgreSQL 并发幂等/RLS 隔离/加密恢复、API 权限边界、非 root 容器和完整 Compose 启动。

运维入口：`auditmesh-operations backup-create <path>`、`backup-restore <path> --target-url <url>` 与 `evidence-verify [--tenant ...]`。

所有事件均为合成测试数据，不代表真实客户审计或控制有效性结论。生产启用仍需客户策略审批、源连接器认证、留存决策与独立控制负责人验收。
