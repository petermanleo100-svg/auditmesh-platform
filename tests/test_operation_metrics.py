import pytest
from auditmesh.operation_metrics import record_operation


def test_operation_metric_is_atomic_and_preserves_last_success_on_failure(tmp_path):
    path=tmp_path/"auditmesh.prom";record_operation(path,"evidence_verify",True,now=100);record_operation(path,"evidence_verify",False,now=200);text=path.read_text()
    assert 'auditmesh_operation_success{operation="evidence_verify"} 0' in text
    assert 'auditmesh_operation_last_run_timestamp_seconds{operation="evidence_verify"} 200.000' in text
    assert 'auditmesh_operation_last_success_timestamp_seconds{operation="evidence_verify"} 100.000' in text
    assert list(tmp_path.glob(".auditmesh.prom.*"))==[]


def test_operation_metric_rejects_unbounded_labels(tmp_path):
    with pytest.raises(ValueError,match="bounded"):record_operation(tmp_path/"metric.prom",'bad"label',True)
