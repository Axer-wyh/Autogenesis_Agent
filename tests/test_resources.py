from autogenesis_agent.resources import ResourceRegistry
from autogenesis_agent.storage import connect


def test_register_resource_creates_initial_active_version(tmp_path):
    db = connect(tmp_path / "agent.sqlite")
    registry = ResourceRegistry(db)

    resource = registry.register_resource(
        name="base-system-prompt",
        resource_type="prompt",
        description="Base prompt",
        content="You are useful.",
        trainable=True,
    )

    active = registry.get_active_version(resource.id)
    assert resource.id.startswith("res_")
    assert active.resource_id == resource.id
    assert active.version == 1
    assert active.content == "You are useful."
    assert active.parent_version_id is None


def test_create_version_tracks_lineage_and_becomes_active(tmp_path):
    db = connect(tmp_path / "agent.sqlite")
    registry = ResourceRegistry(db)
    resource = registry.register_resource(
        name="skill-search",
        resource_type="skill",
        description="Search skill",
        content="Search once.",
        trainable=True,
    )
    first = registry.get_active_version(resource.id)

    second = registry.create_version(resource.id, content="Search, verify, summarize.", reason="Improve reliability")

    active = registry.get_active_version(resource.id)
    assert second.version == 2
    assert second.parent_version_id == first.id
    assert active.id == second.id
    assert active.reason == "Improve reliability"
