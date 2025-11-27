from datetime import date, timedelta
from collections import defaultdict, deque

DEFAULT_WEIGHTS = {
    "urgency": 0.35,
    "importance": 0.35,
    "effort": 0.15,
    "dependency": 0.15
}

def detect_cycles(tasks):
    # tasks: list of dicts; each has 'id' or uses index; dependencies list of ids
    id_map = {str(task.get('id', idx)): idx for idx, task in enumerate(tasks)}
    graph = defaultdict(list)
    for idx, task in enumerate(tasks):
        src = str(task.get('id', idx))
        for dep in task.get('dependencies', []):
            depid = str(dep)
            if depid in id_map:
                graph[depid].append(src)  # edge dep -> task (dep blocks task)
    # detect cycle using DFS
    visited = {}
    path = []
    def dfs(node):
        if node in visited:
            return visited[node] == 1
        visited[node] = 1  # visiting
        for nbr in graph.get(node, []):
            if dfs(nbr):
                return True
        visited[node] = 2
        return False
    for node in graph:
        if node not in visited:
            if dfs(node):
                return True
    return False

def compute_dependency_score(tasks):
    # count out-degree: how many tasks this task blocks
    id_map = {str(task.get('id', idx)): idx for idx, task in enumerate(tasks)}
    blocks_count = defaultdict(int)
    for idx, task in enumerate(tasks):
        for dep in task.get('dependencies', []):
            depid = str(dep)
            if depid in id_map:
                blocks_count[depid] += 1
    return blocks_count

def urgency_score(due_date):
    if due_date is None:
        return 0.0
    today = date.today()
    days = (due_date - today).days
    if days < 0:
        # past due: high urgency
        return 1.0 + min(abs(days)/30.0, 1.0)  # cap extra boost
    # closer -> higher urgency
    return max(0.0, 1.0 - (days/60.0))  # 0..1 scale, 60 days horizon

def effort_score(estimated_hours):
    # smaller estimated_hours -> higher quick-win score
    h = max(0.1, float(estimated_hours))
    return min(1.0, 1.0 / (h ** 0.5))  # gentle decay

def normalize(value, min_v=0, max_v=10):
    if max_v == min_v:
        return 0
    return (value - min_v) / (max_v - min_v)

def score_tasks(tasks, strategy='smart_balance', weights=None):
    """
    tasks: list of dicts; expected fields: id, title, due_date (date obj or ISO), estimated_hours, importance, dependencies
    strategy: 'fastest_wins', 'high_impact', 'deadline_driven', 'smart_balance'
    """
    import datetime
    if weights is None:
        weights = DEFAULT_WEIGHTS.copy()

    # adjust weights per strategy
    if strategy == 'fastest_wins':
        weights = {"urgency":0.2, "importance":0.2, "effort":0.5, "dependency":0.1}
    elif strategy == 'high_impact':
        weights = {"urgency":0.15, "importance":0.6, "effort":0.1, "dependency":0.15}
    elif strategy == 'deadline_driven':
        weights = {"urgency":0.7, "importance":0.15, "effort":0.05, "dependency":0.1}

    # parse dates
    for t in tasks:
        if isinstance(t.get('due_date'), str):
            try:
                t['due_date'] = datetime.date.fromisoformat(t['due_date'])
            except Exception:
                t['due_date'] = None

    # detect cycles and create reason flag
    cycles = detect_cycles(tasks)
    blocks = compute_dependency_score(tasks)

    results = []
    for idx, t in enumerate(tasks):
        imp = max(1, min(10, int(t.get('importance', 5))))
        est = max(0.1, float(t.get('estimated_hours', 1.0)))
        ud = t.get('due_date')
        u = urgency_score(ud)
        e = effort_score(est)
        dep_count = blocks.get(str(t.get('id', idx)), 0)
        dep_norm = min(1.0, dep_count / max(1, len(tasks)))
        score = (weights['urgency'] * u +
                 weights['importance'] * (imp / 10.0) +
                 weights['effort'] * e +
                 weights['dependency'] * dep_norm)
        # Past-due adjustment: if due_date < today, amplify urgency already included
        reason = []
        if ud and (ud < date.today()):
            reason.append("Past due — needs immediate attention")
        if dep_count > 0:
            reason.append(f"Blocks {dep_count} task(s)")
        if est <= 1.0:
            reason.append("Quick win (low effort)")
        if imp >= 8:
            reason.append("High importance")
        if not reason:
            reason.append("Balanced priority")
        results.append({**t, "score": round(score, 4), "reason": "; ".join(reason)})
    # sort descending by score
    results.sort(key=lambda x: x['score'], reverse=True)
    meta = {"cycle_detected": cycles}
    return results, meta
