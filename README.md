# AuditMesh Platform

独立的事件驱动连续审计与 IT 内控缺陷运营平台。

- 版本化控制策略，将特权操作、备份与身份事件转为可解释缺陷案例。
- 租户级事件幂等、证据哈希、案例生命周期和乐观并发控制。
- 基于严重性的 SLA 截止时间与逾期队列。
- 四眼关闭控制，事件责任人不能自行关闭缺陷。
- FastAPI/OpenAPI、非 root 容器与 GitHub CI。

```bash
pip install -e ".[test]"
pytest -q
uvicorn auditmesh.api:create_app --factory --port 8000
```

所有事件均为合成测试数据，不代表真实客户审计或控制有效性结论。
