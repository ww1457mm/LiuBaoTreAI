"""Tests for knowledge API endpoints."""

import pytest

# Skip search tests if FAISS is not available
try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False


class TestKnowledgeList:
    def test_get_knowledge_list(self, client, db):
        """获取知识库列表"""
        resp = client.get("/api/knowledge")
        assert resp.status_code == 200
        data = resp.json()
        assert data["code"] == 0
        assert "data" in data
        assert "total" in data
        assert "page" in data
        assert "page_size" in data

    def test_get_knowledge_list_with_pagination(self, client):
        """分页参数生效"""
        resp = client.get("/api/knowledge", params={"page": 1, "page_size": 5})
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["data"]) <= 5
        assert data["page"] == 1
        assert data["page_size"] == 5

    def test_knowledge_list_item_structure(self, client):
        """列表每项包含必要字段"""
        resp = client.get("/api/knowledge")
        items = resp.json()["data"]
        if items:
            item = items[0]
            assert "id" in item
            assert "title" in item
            assert "content" in item
            assert "category" in item


class TestKnowledgeDetail:
    def test_get_knowledge_detail(self, client):
        """获取知识详情"""
        # 先获取列表拿到 id
        list_resp = client.get("/api/knowledge")
        items = list_resp.json()["data"]
        if items:
            kid = items[0]["id"]
            resp = client.get(f"/api/knowledge/{kid}")
            assert resp.status_code == 200
            data = resp.json()
            assert data["code"] == 0
            assert "content" in data["data"]
            assert "title" in data["data"]

    def test_get_knowledge_detail_not_found(self, client):
        """不存在的文章返回 404"""
        resp = client.get("/api/knowledge/999999")
        assert resp.status_code == 404


class TestKnowledgeSearch:
    @pytest.mark.skipif(not FAISS_AVAILABLE, reason="FAISS not installed")
    def test_search_knowledge(self, client):
        """搜索功能返回结果"""
        resp = client.get("/api/knowledge/search/query", params={"q": "六堡茶"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["code"] == 0
        assert isinstance(data["data"], list)

    @pytest.mark.skipif(not FAISS_AVAILABLE, reason="FAISS not installed")
    def test_search_with_db_id_attached(self, client):
        """搜索结果附加了数据库 ID"""
        resp = client.get("/api/knowledge/search/query", params={"q": "六堡茶"})
        items = resp.json()["data"]
        # 所有结果应有 id 字段（即使是0也说明字段存在）
        for item in items:
            assert "id" in item
            assert "title" in item
            assert "content" in item

    @pytest.mark.skipif(not FAISS_AVAILABLE, reason="FAISS not installed")
    def test_search_pagination(self, client):
        """搜索结果支持分页"""
        resp = client.get("/api/knowledge/search/query", params={"q": "茶", "page": 1, "page_size": 2})
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["data"]) <= 2
