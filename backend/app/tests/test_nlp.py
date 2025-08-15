from app.nlp import parse_query

def test_parse_basic():
    legs, _ = parse_query("Tatum 30+ pts and 8+ reb on 2025-11-03")
    # Parser won't assert specific IDs here; ensure at least two legs parsed
    assert len(legs) >= 2