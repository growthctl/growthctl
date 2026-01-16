from dataclasses import dataclass
from typing import Any


@dataclass
class AdSetMatch:
    local_id: str
    local_name: str
    remote_ad_set: dict[str, Any] | None
    remote_real_id: str | None


def build_ad_set_lookup(
    remote_ad_sets: dict[str, dict[str, Any]],
) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    by_id = dict(remote_ad_sets.items())
    by_name = {v["name"]: v for v in remote_ad_sets.values()}
    return by_id, by_name


def match_ad_set(
    local_id: str,
    local_name: str,
    remote_by_id: dict[str, dict[str, Any]],
    remote_by_name: dict[str, dict[str, Any]],
) -> dict[str, Any] | None:
    if local_id in remote_by_id:
        return remote_by_id[local_id]
    if local_name in remote_by_name:
        return remote_by_name[local_name]
    return None
