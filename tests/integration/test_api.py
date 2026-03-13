"""
API 路由集成测试
"""
import pytest
from fastapi.testclient import TestClient
from src.main import app


client = TestClient(app)


class TestHealthEndpoint:
    """测试健康检查端点"""
    
    def test_health_check(self):
        """测试健康检查返回正确格式"""
        response = client.get("/api/v1/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "timestamp" in data
    
    def test_health_check_request_id_header(self):
        """测试健康检查返回 X-Request-ID 头"""
        response = client.get("/api/v1/health")
        
        assert "X-Request-ID" in response.headers
        assert len(response.headers["X-Request-ID"]) > 0


class TestStatsEndpoints:
    """测试统计端点"""
    
    def test_stats_summary(self):
        """测试汇总统计接口"""
        response = client.get("/api/v1/stats/summary?days=30")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "period_days" in data
        assert "summary" in data
        assert "by_provider" in data
        assert "by_model" in data
    
    def test_stats_projects(self):
        """测试项目统计接口"""
        response = client.get("/api/v1/stats/projects?days=30")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "period_days" in data
        assert "projects" in data
    
    def test_stats_teams(self):
        """测试团队统计接口"""
        response = client.get("/api/v1/stats/teams?days=30")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "period_days" in data
        assert "teams" in data
    
    def test_stats_daily(self):
        """测试日报统计接口"""
        response = client.get("/api/v1/stats/daily?days=7")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "period_days" in data
        assert "daily" in data


class TestRecordsEndpoint:
    """测试记录查询端点"""
    
    def test_get_records(self):
        """测试获取使用记录"""
        response = client.get("/api/v1/records?limit=10")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "total" in data
        assert "limit" in data
        assert "offset" in data
        assert "records" in data


class TestErrorHandling:
    """测试错误处理"""
    
    def test_404_error(self):
        """测试 404 错误返回标准格式"""
        response = client.get("/api/v1/nonexistent")
        
        assert response.status_code == 404
        # FastAPI 默认 404，我们检查是否正确处理
    
    def test_request_id_in_error_response(self):
        """测试错误响应中包含 request_id"""
        # 发送一个会触发错误的请求
        response = client.get("/api/v1/records?limit=invalid")
        
        # 检查响应头中是否有 request_id
        assert "X-Request-ID" in response.headers


class TestDashboard:
    """测试仪表盘页面"""
    
    def test_dashboard_page(self):
        """测试仪表盘页面可访问"""
        response = client.get("/")
        
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert "TokenMeter" in response.text