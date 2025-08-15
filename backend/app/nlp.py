import re
from datetime import date
from typing import List, Tuple
from .schemas import PropLeg
from .players import search_players, PROP_ALIASES

# Examples the parser should handle:
# "Tatum 30+ pts and 8+ reb on 2025-11-03"
# "LeBron over 7.5 ast tonight"
# "Curry 4+ threes & 25+ points"

DATE_PAT = re.compile(r"on\s+(\d{4}-\d{2}-\d{2})|today|tonight|tomorrow", re.I)
LEG_PAT = re.compile(r"(?P<name>[A-Za-z\.\-\'\s]+?)\s+(?P<thresh>\d+(?:\.\d+)?)\+?\s*(?P<prop>pts?|points|reb(?:ounds)?|ast|assists|stl|steals|blk|blocks|tov|turnovers|fg3m|3pm|3pt|threes|point)\b|\bover\s+(?P<thresh2>\d+(?:\.\d+)?)\s*(?P<prop2>ast|pts|reb|stl|blk|tov|fg3m|3pm|3pt|threes|points)", re.I)


def _normalize_date(text: str) -> date | None:
    m = re.search(r"(\d{4}-\d{2}-\d{2})", text)
    if m:
        y, mth, d = map(int, m.group(1).split("-"))
        return date(y, mth, d)
    text_l = text.lower()
    if "today" in text_l or "tonight" in text_l:
        return date.today()
    if "tomorrow" in text_l:
        from datetime import timedelta
        return date.today() + timedelta(days=1)
    return None


def parse_query(query: str) -> Tuple[List[PropLeg], str]:
    legs: List[PropLeg] = []
    d = _normalize_date(query)

    for m in LEG_PAT.finditer(query):
        name = (m.group("name") or "").strip()
        thresh = m.group("thresh") or m.group("thresh2")
        prop = (m.group("prop") or m.group("prop2") or "").lower()
        if not name:
            # name may be in preceding token; naive fallback: look back 2 words
            pass
        # Fuzzy find player
        players = search_players(name or prop)  # if name missing, this will still run but may be irrelevant
        if not players:
            continue
        player_id = int(players[0]["id"])  # best match
        # Normalize prop alias
        prop_norm = PROP_ALIASES.get(prop, prop)
        try:
            threshold = float(thresh)
        except Exception:
            continue
        legs.append(PropLeg(player_id=player_id, prop=prop_norm, threshold=threshold, op=">=", date=d))

    rationale = "Parsed legs from query using regex + fuzzy name matching; date is optional."
    return legs, rationale