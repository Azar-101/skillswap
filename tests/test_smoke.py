def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.get_json() == {"status": "ok"}


def test_404_is_clean(client):
    r = client.get("/nope")
    assert r.status_code == 404
    assert "Traceback" not in r.get_data(as_text=True)
