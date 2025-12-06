from fastapi.testclient import TestClient
from urllib.parse import quote

from src.app import app

client = TestClient(app)


def test_root_redirect():
    res = client.get("/")
    # RedirectResponse uses 307 by default
    assert res.status_code in (301, 302, 307, 308)
    assert res.headers.get("location", "").endswith("/static/index.html")


def test_get_activities():
    res = client.get("/activities")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, dict)
    # expect at least one known activity from seeded data
    assert "Chess Club" in data
    assert "participants" in data["Chess Club"]


def test_signup_and_unregister_flow():
    activity = "Chess Club"
    test_email = "testuser@example.com"

    # ensure user is not already present
    res = client.get("/activities")
    assert res.status_code == 200
    participants = res.json()[activity]["participants"]
    if test_email in participants:
        # remove if left over from previous run
        client.post(f"/activities/{quote(activity)}/unregister?email={quote(test_email)}")

    # signup
    signup_res = client.post(f"/activities/{quote(activity)}/signup?email={quote(test_email)}")
    assert signup_res.status_code == 200
    assert test_email in client.get("/activities").json()[activity]["participants"]

    # unregister
    unregister_res = client.post(f"/activities/{quote(activity)}/unregister?email={quote(test_email)}")
    assert unregister_res.status_code == 200
    assert test_email not in client.get("/activities").json()[activity]["participants"]
