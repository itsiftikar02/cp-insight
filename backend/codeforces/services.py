"""
Service layer for the Codeforces public API.

All HTTP access to Codeforces is isolated here so the rest of the app never
talks to the network directly. Public endpoints used:
  - user.info    : current/max rating
  - user.rating  : contest (rating change) history
  - user.status  : submissions (to derive solved problems)

Docs: https://codeforces.com/apiHelp
"""
from datetime import datetime, timezone

import requests
from django.conf import settings
from django.db import transaction
from django.utils import timezone as dj_tz

from .models import (
    CodeforcesContest,
    CodeforcesProblem,
    TopicStatistics,
    UserSolvedProblem,
)


class CodeforcesError(Exception):
    """Raised when the Codeforces API returns a failure or is unreachable."""


def _get(method: str, params: dict) -> list | dict:
    """Make one GET request to the Codeforces API and return its `result`."""
    url = f"{settings.CODEFORCES_API_BASE}/{method}"
    try:
        resp = requests.get(url, params=params, timeout=20)
    except requests.RequestException as exc:
        raise CodeforcesError(f"Could not reach Codeforces: {exc}") from exc

    if resp.status_code != 200:
        raise CodeforcesError(
            f"Codeforces returned HTTP {resp.status_code} for {method}"
        )

    payload = resp.json()
    if payload.get("status") != "OK":
        raise CodeforcesError(payload.get("comment", "Unknown Codeforces error"))
    return payload["result"]


def fetch_user_info(handle: str) -> dict:
    """Return current and max rating for a handle."""
    result = _get("user.info", {"handles": handle})
    info = result[0]
    return {
        "current_rating": info.get("rating"),
        "max_rating": info.get("maxRating"),
    }


def fetch_rating_history(handle: str) -> list[dict]:
    """Return the list of rating changes (one per rated contest)."""
    return _get("user.rating", {"handle": handle})


def fetch_submissions(handle: str) -> list[dict]:
    """Return all submissions for a handle."""
    return _get("user.status", {"handle": handle})


def _ts_to_dt(unix_ts: int) -> datetime:
    return datetime.fromtimestamp(unix_ts, tz=timezone.utc)


@transaction.atomic
def sync_user(user, handle: str) -> dict:
    """
    Fetch everything for `handle` and persist it for `user`.
    Returns a small summary dict. Wrapped in a transaction so a partial
    failure never leaves half-written data.
    """
    profile = user.profile
    profile.codeforces_handle = handle

    # 1. Current / max rating ------------------------------------------------
    info = fetch_user_info(handle)
    profile.current_rating = info["current_rating"]
    profile.max_rating = info["max_rating"]

    # 2. Contest history -----------------------------------------------------
    rating_history = fetch_rating_history(handle)
    CodeforcesContest.objects.filter(user=user).delete()
    contests = [
        CodeforcesContest(
            user=user,
            contest_id=entry["contestId"],
            contest_name=entry["contestName"],
            rank=entry["rank"],
            old_rating=entry["oldRating"],
            new_rating=entry["newRating"],
            rating_update_time=_ts_to_dt(entry["ratingUpdateTimeSeconds"]),
        )
        for entry in rating_history
    ]
    CodeforcesContest.objects.bulk_create(contests)

    # 3. Solved problems (verdict OK) ---------------------------------------
    submissions = fetch_submissions(handle)
    solved_keys = {}  # (contestId, index) -> (problem dict, earliest solve time)
    for sub in submissions:
        if sub.get("verdict") != "OK":
            continue
        prob = sub.get("problem", {})
        cid = prob.get("contestId")
        index = prob.get("index")
        if index is None:
            continue
        key = (cid, index)
        t = sub["creationTimeSeconds"]
        if key not in solved_keys or t < solved_keys[key][1]:
            solved_keys[key] = (prob, t)

    UserSolvedProblem.objects.filter(user=user).delete()
    solved_records = []
    for (cid, index), (prob, t) in solved_keys.items():
        problem_obj, _ = CodeforcesProblem.objects.get_or_create(
            contest_id=cid,
            index=index,
            defaults={
                "name": prob.get("name", ""),
                "rating": prob.get("rating"),
                "tags": prob.get("tags", []),
            },
        )
        solved_records.append(
            UserSolvedProblem(
                user=user, problem=problem_obj, solved_at=_ts_to_dt(t)
            )
        )
    UserSolvedProblem.objects.bulk_create(solved_records)

    # 4. Recompute topic statistics -----------------------------------------
    rebuild_topic_statistics(user)

    profile.last_synced_at = dj_tz.now()
    profile.save()

    return {
        "handle": handle,
        "current_rating": profile.current_rating,
        "max_rating": profile.max_rating,
        "contests_synced": len(contests),
        "problems_synced": len(solved_records),
        "synced_at": profile.last_synced_at.isoformat(),
    }


def rebuild_topic_statistics(user) -> None:
    """Recount solved problems per tag for a user."""
    counts: dict[str, int] = {}
    solved = UserSolvedProblem.objects.filter(user=user).select_related("problem")
    for sp in solved:
        for tag in sp.problem.tags:
            counts[tag] = counts.get(tag, 0) + 1

    TopicStatistics.objects.filter(user=user).delete()
    TopicStatistics.objects.bulk_create(
        [
            TopicStatistics(user=user, tag=tag, solved_count=count)
            for tag, count in counts.items()
        ]
    )
