def test_create_post_missing_csrf_returns_400(client):
    resp = client.post(
        "/blog/create",
        data={"title": "t1", "body": "b1"},
        follow_redirects=False,
    )
    assert resp.status_code == 400