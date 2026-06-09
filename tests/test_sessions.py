from autogenesis_agent.sessions import SessionManager
from autogenesis_agent.storage import connect


def test_session_creation_persists_metadata_and_starts_empty(tmp_path):
    db = connect(tmp_path / "agent.sqlite")
    manager = SessionManager(db)

    session = manager.create_session(user_id="user-1", channel="cli", workspace="/tmp/work")

    assert session.id.startswith("ses_")
    assert session.user_id == "user-1"
    assert session.channel == "cli"
    assert session.workspace == "/tmp/work"
    assert manager.get_messages(session.id) == []


def test_messages_are_returned_in_append_order(tmp_path):
    db = connect(tmp_path / "agent.sqlite")
    manager = SessionManager(db)
    session = manager.create_session(user_id="user-1", channel="cli", workspace="/tmp/work")

    manager.append_message(session.id, role="user", content="first")
    manager.append_message(session.id, role="assistant", content="second")

    messages = manager.get_messages(session.id)
    assert [(message.role, message.content) for message in messages] == [
        ("user", "first"),
        ("assistant", "second"),
    ]
