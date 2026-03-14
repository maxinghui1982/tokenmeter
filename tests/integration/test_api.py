"""
API 集成测试
测试主要 API 端点
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# 导入应用
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from src.main import app
from src.database.models import Base, get_db


# 创建测试数据库
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """覆盖数据库依赖"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

# 创建测试客户端
client = TestClient(app)


@pytest.fixture(scope="function")
def setup_database():
    """设置测试数据库"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


class TestHealthEndpoints:
    """测试健康检查端点"""

    def test_health_check(self, setup_database):
        """测试健康检查"""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data

    def test_ready_check(self, setup_database):
        """测试就绪检查"""
        response = client.get("/api/v1/ready")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ready"


class TestStatsEndpoints:
    """测试统计端点"""

    def test_stats_summary_empty(self, setup_database):
        """测试空数据统计摘要"""
        response = client.get("/api/v1/stats/summary")
        assert response.status_code == 200
        data = response.json()
        assert data["total_requests"] == 0
        assert data["total_cost"] == 0.0

    def test_stats_by_provider_empty(self, setup_database):
        """测试空数据按提供商统计"""
        response = client.get("/api/v1/stats/by-provider")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_stats_by_project_empty(self, setup_database):
        """测试空数据按项目统计"""
        response = client.get("/api/v1/stats/by-project")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0


class TestBudgetEndpoints:
    """测试预算管理端点"""

    def test_create_budget(self, setup_database):
        """测试创建预算"""
        budget_data = {
            "name": "测试预算",
            "amount": 1000.0,
            "period": "monthly",
            "project": "test-project",
            "alert_thresholds": [50, 80, 100],
        }
        response = client.post("/api/v1/budgets", json=budget_data)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "测试预算"
        assert data["amount"] == 1000.0

    def test_list_budgets_empty(self, setup_database):
        """测试空预算列表"""
        response = client.get("/api/v1/budgets")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_list_budgets_with_data(self, setup_database):
        """测试有数据的预算列表"""
        # 先创建预算
        budget_data = {
            "name": "月度预算",
            "amount": 500.0,
            "period": "monthly",
            "project": "proj-1",
        }
        client.post("/api/v1/budgets", json=budget_data)

        response = client.get("/api/v1/budgets")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "月度预算"


class TestAuthEndpoints:
    """测试认证端点"""

    def test_register_user(self, setup_database):
        """测试用户注册"""
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123",
            "full_name": "Test User",
        }
        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["user"]["username"] == "testuser"

    def test_register_duplicate_username(self, setup_database):
        """测试重复用户名注册"""
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123",
        }
        client.post("/api/v1/auth/register", json=user_data)

        # 再次注册相同用户名
        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 400

    def test_login_success(self, setup_database):
        """测试成功登录"""
        # 先注册
        user_data = {
            "username": "logintest",
            "email": "login@example.com",
            "password": "password123",
        }
        client.post("/api/v1/auth/register", json=user_data)

        # 登录
        login_data = {"username": "logintest", "password": "password123"}
        response = client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data

    def test_login_wrong_password(self, setup_database):
        """测试错误密码登录"""
        # 先注册
        user_data = {
            "username": "logintest2",
            "email": "login2@example.com",
            "password": "password123",
        }
        client.post("/api/v1/auth/register", json=user_data)

        # 错误密码登录
        login_data = {"username": "logintest2", "password": "wrongpassword"}
        response = client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 401

    def test_get_me_without_token(self, setup_database):
        """测试无 token 获取用户信息"""
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 403


class TestExportEndpoints:
    """测试导出端点"""

    def test_export_usage_csv_empty(self, setup_database):
        """测试空数据导出 CSV"""
        response = client.get("/api/v1/export/usage/csv")
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/csv; charset=utf-8"

    def test_export_summary_csv_empty(self, setup_database):
        """测试空数据导出汇总 CSV"""
        response = client.get("/api/v1/export/summary/csv")
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/csv; charset=utf-8"


class TestProxyEndpoints:
    """测试代理端点"""

    def test_proxy_without_auth(self, setup_database):
        """测试无认证访问代理"""
        response = client.post(
            "/proxy/openai/v1/chat/completions",
            json={"model": "gpt-4", "messages": [{"role": "user", "content": "Hello"}]},
        )
        # 应该返回 401 或 422（因为需要有效 API key）
        assert response.status_code in [401, 422, 500]


class TestDashboardEndpoints:
    """测试仪表盘端点"""

    def test_dashboard_home(self, setup_database):
        """测试仪表盘首页"""
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_dashboard_stats(self, setup_database):
        """测试仪表盘统计数据"""
        response = client.get("/dashboard/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total_requests" in data
        assert "total_cost" in data
