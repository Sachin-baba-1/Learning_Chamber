import uuid
import pytest
from pydantic import ValidationError
from schema import Resource, ResourceKind


def make_resource(**overrides):
    base = dict(
        id=uuid.uuid4(),
        import_id=uuid.uuid4(),
        kind=ResourceKind.video,
        title="Week 2.3 - Bash and terminal.mp4",
        parent_id=None,          # None = root — the named state
        path="Mission 1",
        source_uri="drive://file/abc123",
        status="active",
    )
    base.update(overrides)
    return Resource(**base)


def test_valid_construction():
    r = make_resource()
    assert r.kind is ResourceKind.video
    assert r.parent_id is None


def test_invalid_kind_rejected():
    with pytest.raises(ValidationError):
        make_resource(kind="exe")   # garbage kinds can never enter storage


def test_json_round_trip():
    r = make_resource(order_index=None)
    r2 = Resource.model_validate_json(r.model_dump_json())
    assert r2 == r                  # serialization loses nothing