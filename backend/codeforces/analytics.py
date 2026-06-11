"""
Rule-based analytics. No machine learning anywhere on purpose: every number
and message below is produced by deterministic rules so it can be explained.
"""
from collections import defaultdict

from django.db.models import Avg

from .models import CodeforcesContest, TopicStatistics, UserSolvedProblem

# Canonical topics we care about, mapped to the raw Codeforces tag strings.
CORE_TOPICS = {
    "Dynamic Programming": ["dp"],
    "Graphs": ["graphs", "dfs and similar", "shortest paths", "graph matchings"],
    "Trees": ["trees"],
    "Greedy": ["greedy"],
    "Binary Search": ["binary search"],
    "Math": ["math", "number theory", "combinatorics"],
    "Strings": ["strings", "string suffix structures", "hashing"],
    "Data Structures": ["data structures"],
}


def _topic_counts(user) -> dict[str, int]:
    """Map each core topic to the user's solved count."""
    raw = {ts.tag: ts.solved_count for ts in TopicStatistics.objects.filter(user=user)}
    result = {}
    for topic, tags in CORE_TOPICS.items():
        result[topic] = sum(raw.get(t, 0) for t in tags)
    return result


def overview_stats(user) -> dict:
    profile = user.profile
    contests = CodeforcesContest.objects.filter(user=user)
    return {
        "current_rating": profile.current_rating,
        "max_rating": profile.max_rating,
        "contest_count": contests.count(),
        "total_solved": UserSolvedProblem.objects.filter(user=user).count(),
    }


def rating_analytics(user) -> dict:
    contests = list(CodeforcesContest.objects.filter(user=user))
    if not contests:
        return {"progression": [], "best_rating": None, "avg_change": 0}

    progression = [
        {
            "contest_name": c.contest_name,
            "rating": c.new_rating,
            "date": c.rating_update_time.isoformat(),
        }
        for c in contests
    ]
    best_rating = max(c.new_rating for c in contests)
    avg_change = round(sum(c.rating_change for c in contests) / len(contests), 2)
    return {
        "progression": progression,
        "best_rating": best_rating,
        "avg_change": avg_change,
    }


def contest_analytics(user) -> dict:
    contests = list(CodeforcesContest.objects.filter(user=user))
    if not contests:
        return {"by_year": {}, "avg_rank": None, "best_rank": None}

    by_year = defaultdict(int)
    for c in contests:
        by_year[c.rating_update_time.year] += 1

    avg_rank = round(
        CodeforcesContest.objects.filter(user=user).aggregate(a=Avg("rank"))["a"], 1
    )
    best_rank = min(c.rank for c in contests)
    return {
        "by_year": dict(sorted(by_year.items())),
        "avg_rank": avg_rank,
        "best_rank": best_rank,
    }


def topic_analysis(user) -> dict:
    counts = _topic_counts(user)
    ordered = sorted(counts.items(), key=lambda kv: kv[1], reverse=True)
    return {
        "per_topic": counts,
        "most_practiced": [t for t, _ in ordered[:3]],
        "least_practiced": [t for t, _ in ordered[-3:] if _ == _][::-1],
    }


def detect_weaknesses(user) -> list[dict]:
    """
    Deterministic weakness rules. Each returns a topic + human message.
    """
    counts = _topic_counts(user)
    total = sum(counts.values())
    insights: list[dict] = []

    if total == 0:
        return [{"topic": None, "message": "Sync your Codeforces handle to see insights."}]

    avg = total / len(counts)

    for topic, count in counts.items():
        # Rule 1: well below the user's own average across topics.
        if count < avg * 0.5:
            insights.append({
                "topic": topic,
                "message": f"Your {topic} practice ({count} solved) is well below "
                           f"your average of {avg:.0f} per topic.",
            })
        # Rule 2: almost untouched.
        elif count <= 3:
            insights.append({
                "topic": topic,
                "message": f"You have solved very few {topic} problems ({count}).",
            })

    # Rule 3: relative comparison between strongest and a weak topic.
    if counts:
        strongest = max(counts, key=counts.get)
        weakest = min(counts, key=counts.get)
        if counts[strongest] >= counts[weakest] * 3 and counts[weakest] >= 0:
            insights.append({
                "topic": weakest,
                "message": f"Your {weakest} problems are significantly lower than "
                           f"your {strongest} problems.",
            })

    return insights or [{"topic": None, "message": "No major weaknesses detected. Keep it up!"}]


# Maps a weak topic to a deterministic recommendation message.
RECOMMENDATION_RULES = {
    "Dynamic Programming": "Start with beginner DP: knapsack, coin change, and longest "
                           "increasing subsequence. Aim for 5 easy DP problems this week.",
    "Graphs": "Practice graph fundamentals: BFS/DFS traversal, connected components, "
              "and shortest paths (Dijkstra). Try 5 graph problems rated 1200-1500.",
    "Trees": "Work on tree basics: tree traversal, subtree sizes, and lowest common "
             "ancestor. Solve 4 introductory tree problems.",
    "Greedy": "Reinforce greedy by solving sorting-based and exchange-argument problems "
              "rated 1300-1600.",
    "Binary Search": "Practice binary search on answer and on sorted arrays. Target 5 "
                     "problems tagged 'binary search'.",
    "Math": "Brush up on number theory, GCD/LCM, and modular arithmetic. Solve 5 math "
            "problems rated 1200-1500.",
    "Strings": "Practice string handling: prefix functions, hashing, and two-pointer "
               "string problems.",
    "Data Structures": "Practice prefix sums, stacks/queues, and Fenwick/segment trees "
                       "on introductory problems.",
}


def generate_recommendations(user) -> list[dict]:
    """Turn detected weaknesses into deterministic recommendations."""
    weaknesses = detect_weaknesses(user)
    recs = []
    seen = set()
    for w in weaknesses:
        topic = w["topic"]
        if topic and topic in RECOMMENDATION_RULES and topic not in seen:
            recs.append({"topic": topic, "message": RECOMMENDATION_RULES[topic]})
            seen.add(topic)
    return recs
