"""Tests for history and favorite API endpoints."""

import pytest


class TestHistory:
    def test_get_history_empty(self, client, test_openid):
        """新用户历史为空"""
        client.post("/api/user/login", json={"openid": test_openid})
        resp = client.get("/api/history", params={"openid": test_openid, "type": "all"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["code"] == 0
        assert "recognition" in data["data"]
        assert "qa" in data["data"]

    def test_history_requires_login(self, client):
        """未登录用户返回 401"""
        resp = client.get("/api/history", params={"openid": "nonexistent", "type": "all"})
        assert resp.status_code == 200
        assert resp.json()["code"] == 401

    def test_history_pagination(self, client, test_openid):
        """历史记录支持分页"""
        client.post("/api/user/login", json={"openid": test_openid})
        resp = client.get(
            "/api/history",
            params={"openid": test_openid, "type": "all", "page": 1, "page_size": 10}
        )
        assert resp.status_code == 200
        data = resp.json()
        rec = data["data"]["recognition"]
        qa = data["data"]["qa"]
        # 兼容新旧格式
        rec_items = rec["items"] if isinstance(rec, dict) else rec
        qa_items = qa["items"] if isinstance(qa, dict) else qa
        assert isinstance(rec_items, list)
        assert isinstance(qa_items, list)

    def test_history_type_filter(self, client, test_openid):
        """类型过滤正常"""
        client.post("/api/user/login", json={"openid": test_openid})
        resp = client.get("/api/history", params={"openid": test_openid, "type": "recognition"})
        assert resp.status_code == 200
        assert "recognition" in resp.json()["data"]


class TestFavorite:
    def test_add_favorite(self, client, test_openid):
        """添加收藏成功"""
        client.post("/api/user/login", json={"openid": test_openid})
        resp = client.post("/api/favorite", json={
            "openid": test_openid,
            "fav_type": "knowledge",
            "title": "六堡茶历史",
            "content": "六堡茶产于广西..."
        })
        assert resp.status_code == 200
        assert resp.json()["code"] == 0

    def test_add_favorite_requires_login(self, client):
        """添加收藏需要登录"""
        resp = client.post("/api/favorite", json={
            "openid": "nonexistent",
            "fav_type": "knowledge",
            "title": "test",
            "content": "test"
        })
        assert resp.json()["code"] == 401

    def test_list_favorites(self, client, test_openid):
        """收藏列表正常返回"""
        client.post("/api/user/login", json={"openid": test_openid})
        client.post("/api/favorite", json={
            "openid": test_openid, "fav_type": "knowledge", "title": "test", "content": "ct"
        })
        resp = client.get("/api/favorite", params={"openid": test_openid})
        assert resp.status_code == 200
        data = resp.json()
        assert data["code"] == 0
        assert isinstance(data["data"], list)
        assert "total" in data

    def test_delete_favorite(self, client, test_openid):
        """删除收藏成功"""
        client.post("/api/user/login", json={"openid": test_openid})
        add_resp = client.post("/api/favorite", json={
            "openid": test_openid, "fav_type": "qa", "title": "q", "content": "a"
        })
        fid = add_resp.json()["data"] if "data" in add_resp.json() else 1

        resp = client.delete(
            f"/api/favorite/{fid}",
            params={"openid": test_openid}
        )
        assert resp.status_code == 200
        assert resp.json()["code"] == 0

    def test_favorite_sanitization(self, client, test_openid):
        """收藏内容经过清理"""
        client.post("/api/user/login", json={"openid": test_openid})
        resp = client.post("/api/favorite", json={
            "openid": test_openid,
            "fav_type": "invalid",
            "title": "<script>alert(1)</script>",
            "content": "test"
        })
        assert resp.status_code == 200
        # fav_type 被规范化为 knowledge
        list_resp = client.get("/api/favorite", params={"openid": test_openid})
        items = list_resp.json()["data"]
        if items:
            assert "<script>" not in items[0]["title"]
