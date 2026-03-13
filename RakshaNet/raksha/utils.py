from datetime import datetime, timezone


KEYWORD_URGENCY_HINTS = {
    'critical': [
        'trapped', 'collapse', 'collapsed', 'unconscious', 'severe bleeding',
        'life threatening', 'immediate', 'urgent', 'heart attack', 'stroke'
    ],
    'high': [
        'injured', 'injury', 'flooded', 'fire', 'landslide', 'missing',
        'elderly', 'children', 'pregnant', 'no shelter', 'no food', 'no water'
    ],
    'medium': [
        'shortage', 'supply', 'medical help', 'blocked road', 'power outage'
    ],
}

CRISIS_PENDING_STATUSES = ('submitted', 'verified', 'pending', 'approved')
CRISIS_ACTIVE_STATUSES = ('allocated', 'in_progress')
CRISIS_COMPLETED_STATUSES = ('completed', 'delivered')


def compute_priority_score(cr):
    """Compute a simple priority score for a CrisisRequest instance.

    Factors:
    - urgency (low->critical): weight
    - is_verified: boost
    - age (newer requests slightly higher)
    - presence of location: small boost
    - length of resources_required: proxy for complexity

    Returns float score (0-100).
    """
    score = 0.0

    urgency_weights = {
        'low': 10,
        'medium': 35,
        'high': 65,
        'critical': 90,
    }

    score += urgency_weights.get(cr.urgency, 30)

    if cr.is_verified:
        score += 7.5

    # Age: prefer newer requests but decayed slightly
    try:
        age_hours = (datetime.now(timezone.utc) - cr.created_at).total_seconds() / 3600.0
    except Exception:
        age_hours = 0.0
    # Newer gets small bonus (within first 24h)
    if age_hours < 24:
        score += max(0, 6 - (age_hours / 4))

    # location presence
    if cr.latitude and cr.longitude:
        score += 2.0

    # complexity/resource request length
    if cr.resources_required:
        l = len(cr.resources_required)
        score += min(8.0, (l / 50.0))

    # clamp
    score = max(0.0, min(100.0, score))
    return round(score, 4)


def haversine_distance(lat1, lon1, lat2, lon2):
    """Return distance in kilometers between two lat/lon points."""
    from math import radians, sin, cos, asin, sqrt
    lat1, lon1, lat2, lon2 = map(radians, (lat1, lon1, lat2, lon2))
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1)*cos(lat2)*sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    R = 6371.0
    return R * c


def find_nearest_available_volunteer(request, volunteers, max_km=50.0):
    """Return nearest available volunteer within max_km (or None)."""
    best = None
    best_dist = None
    if not request.latitude or not request.longitude:
        return None
    for v in volunteers:
        if not v.available or v.latitude is None or v.longitude is None:
            continue
        try:
            d = haversine_distance(float(request.latitude), float(request.longitude), float(v.latitude), float(v.longitude))
        except Exception:
            continue
        if d <= max_km and (best is None or d < best_dist):
            best = v
            best_dist = d
    return best


def infer_urgency_from_text(description, resources_required, people_affected=1):
    """Infer urgency level using a lightweight rule-based NLP heuristic."""
    text = f"{description or ''} {resources_required or ''}".lower()
    score = 0

    for keyword in KEYWORD_URGENCY_HINTS['critical']:
        if keyword in text:
            score += 35
    for keyword in KEYWORD_URGENCY_HINTS['high']:
        if keyword in text:
            score += 18
    for keyword in KEYWORD_URGENCY_HINTS['medium']:
        if keyword in text:
            score += 8

    try:
        affected = int(people_affected or 1)
    except Exception:
        affected = 1

    if affected >= 50:
        score += 40
    elif affected >= 20:
        score += 25
    elif affected >= 8:
        score += 12

    if score >= 70:
        return 'critical'
    if score >= 38:
        return 'high'
    if score >= 16:
        return 'medium'
    return 'low'


def suggest_resource_types_for_request(cr, resource_types):
    """Return top matching resource types for a crisis request."""
    text = f"{cr.description or ''} {cr.resources_required or ''}".lower()
    scored = []

    for rt in resource_types:
        name = (rt.name or '').lower()
        category = (rt.category or '').lower()
        match_score = 0

        if name and name in text:
            match_score += 25
        if category and category in text:
            match_score += 15

        if category == 'medical' and any(k in text for k in ['injur', 'bleed', 'medical', 'ambulance']):
            match_score += 20
        if category == 'food' and any(k in text for k in ['food', 'water', 'hungry']):
            match_score += 20
        if category == 'shelter' and any(k in text for k in ['shelter', 'home', 'homeless', 'rain']):
            match_score += 20
        if category == 'rescue' and any(k in text for k in ['trapped', 'collapsed', 'rescue']):
            match_score += 20

        if match_score > 0:
            scored.append((match_score, rt))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [item[1] for item in scored[:5]]


def ai_role_insights_for_requests(requests):
    """Build quick AI-style insights for dashboard cards."""
    requests = list(requests)
    if not requests:
        return ["No active crisis data yet. AI insights will appear after requests are submitted."]

    critical = sum(1 for r in requests if r.urgency == 'critical')
    high = sum(1 for r in requests if r.urgency == 'high')
    avg_score = round(sum((r.priority_score or 0) for r in requests) / max(1, len(requests)), 1)

    insights = [f"Average priority score is {avg_score} across {len(requests)} tracked requests."]
    if critical:
        insights.append(f"{critical} critical request(s) need immediate attention.")
    if high:
        insights.append(f"{high} high-urgency request(s) should be allocated next.")

    return insights[:3]


def generate_ai_coordination_reply(prompt, role='user'):
    """Generate a safe, deterministic coordination reply without external AI dependencies."""
    text = (prompt or '').strip()
    if not text:
        return "Please share a crisis situation or coordination question so I can help."

    lowered = text.lower()
    steps = []

    if any(k in lowered for k in ['bleed', 'unconscious', 'stroke', 'heart', 'injur']):
        steps.append('Prioritize immediate medical triage and call emergency services if life-threatening.')
    if any(k in lowered for k in ['flood', 'rain', 'landslide', 'storm']):
        steps.append('Move affected people to higher and safer shelter zones before resource movement.')
    if any(k in lowered for k in ['food', 'water', 'hungry', 'ration']):
        steps.append('Dispatch food and clean-water kits first and track distribution by family count.')
    if any(k in lowered for k in ['trapped', 'collapse', 'rescue']):
        steps.append('Coordinate rescue team assignment and maintain a live headcount of extracted people.')

    if not steps:
        steps.extend([
            'Confirm exact location, urgency, and number of people affected.',
            'Assign one NGO/Admin lead, one field volunteer lead, and one user contact point.',
            'Post status updates every 15-30 minutes in coordination chat until closure.',
        ])

    role_tip = {
        'ngo': 'As NGO/Admin: verify request status and allocate inventory with ETA.',
        'volunteer': 'As Volunteer: share live ground constraints, route risks, and delivery proof.',
        'user': 'As User: share precise needs, landmarks, and immediate safety risks.',
    }.get(role, 'Keep communication short, factual, and time-stamped.')

    numbered = "\n".join([f"{idx + 1}. {step}" for idx, step in enumerate(steps[:3])])
    return f"Recommended coordination plan:\n{numbered}\n\n{role_tip}"


def sync_request_status_from_assignments(crisis_request):
    """Keep a crisis request lifecycle aligned with its related assignments."""
    assignment_statuses = list(crisis_request.assignments.values_list('status', flat=True))
    if not assignment_statuses:
        return crisis_request.status

    next_status = crisis_request.status
    if any(status == 'in_progress' for status in assignment_statuses):
        next_status = 'in_progress'
    elif any(status in ['pending', 'accepted'] for status in assignment_statuses):
        next_status = 'allocated'
    elif all(status == 'completed' for status in assignment_statuses):
        next_status = 'completed'

    if next_status != crisis_request.status:
        crisis_request.status = next_status
        crisis_request.save()

    return crisis_request.status
