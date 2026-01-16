from growthctl.utils import build_ad_set_lookup, match_ad_set


def test_build_ad_set_lookup():
    """Test building lookup maps from remote ad sets."""
    remote_ad_sets = {
        "id1": {"id": "id1", "name": "Name 1"},
        "id2": {"id": "id2", "name": "Name 2"},
    }
    by_id, by_name = build_ad_set_lookup(remote_ad_sets)

    assert by_id["id1"]["name"] == "Name 1"
    assert by_id["id2"]["name"] == "Name 2"
    assert by_name["Name 1"]["id"] == "id1"
    assert by_name["Name 2"]["id"] == "id2"


def test_match_ad_set_by_id():
    """Test matching by ID."""
    remote_by_id = {"id1": {"id": "id1", "name": "Name 1"}}
    remote_by_name = {"Name 1": {"id": "id1", "name": "Name 1"}}

    match = match_ad_set("id1", "Different Name", remote_by_id, remote_by_name)
    assert match["id"] == "id1"


def test_match_ad_set_by_name():
    """Test matching by name when ID doesn't match."""
    remote_by_id = {"id1": {"id": "id1", "name": "Name 1"}}
    remote_by_name = {"Name 1": {"id": "id1", "name": "Name 1"}}

    match = match_ad_set("new_id", "Name 1", remote_by_id, remote_by_name)
    assert match["id"] == "id1"


def test_match_ad_set_no_match():
    """Test that it returns None when no match found."""
    remote_by_id = {"id1": {"id": "id1", "name": "Name 1"}}
    remote_by_name = {"Name 1": {"id": "id1", "name": "Name 1"}}

    match = match_ad_set("new_id", "New Name", remote_by_id, remote_by_name)
    assert match is None
