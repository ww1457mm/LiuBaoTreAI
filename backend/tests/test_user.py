"""Tests for user API endpoints."""

import pytest


class TestLogin:
    def test_login_with_openid(self, client, test_openid):
        """开发模式登录：传入 openid 直接创建用户"""
        resp = client.post("/api/user/login", json={"openid": test_openid})
        assert resp.status_code == 200
        data = resp.json()
        assert data["openid"] == test_openid
        assert data["nickname"] == "茶友"

    def test_login_creates_new_user(self, client, test_openid):
        """首次登录自动创建用户"""
        resp = client.post("/api/user/login", json={"openid": "new_user_openid"})
        assert resp.status_code == 200
        data = resp.json()
        assert "openid" in data

    def test_login_dev_mode(self, client):
        """无 openid 时降级为开发模式"""
        resp = client.post("/api/user/login", json={"code": "dev_code_123"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["openid"].startswith("dev_")


class TestProfile:
    def test_get_profile(self, client, test_openid):
        """登录后获取用户资料"""
        # 先登录
        client.post("/api/user/login", json={"openid": test_openid})
        # 再获取
        resp = client.get("/api/user/profile", params={"openid": test_openid})
        assert resp.status_code == 200
        data = resp.json()
        assert data["openid"] == test_openid
        assert "nickname" in data

    def test_get_profile_not_found(self, client):
        """不存在的用户返回 404"""
        resp = client.get("/api/user/profile", params={"openid": "nonexistent"})
        assert resp.status_code == 404

    def test_update_profile(self, client, test_openid):
        """更新用户昵称和头像"""
        client.post("/api/user/login", json={"openid": test_openid})
        resp = client.put(
            "/api/user/profile",
            json={"openid": test_openid, "nickname": "六堡茶爱好者", "avatar": "https://example.com/avatar.png"}
        )
        assert resp.status_code == 200
        assert resp.json()["message"] == "更新成功"

        # 验证更新成功
        profile = client.get("/api/user/profile", params={"openid": test_openid})
        assert profile.json()["nickname"] == "六堡茶爱好者"

    def test_profile_xss_protection(self, client, test_openid):
        """昵称过滤危险字符"""
        client.post("/api/user/login", json={"openid": test_openid})
        resp = client.put(
            "/api/user/profile",
            json={"openid": test_openid, "nickname": "<script>alert(1)</script>"}
        )
        assert resp.status_code == 200
        profile = client.get("/api/user/profile", params={"openid": test_openid})
        assert "<script>" not in profile.json()["nickname"]
