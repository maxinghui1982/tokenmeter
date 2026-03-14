"""
TokenMeter 配置模块
集中管理所有配置项
"""
import os
import secrets
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置"""

    # 应用信息
    APP_NAME: str = "TokenMeter"
    APP_VERSION: str = "0.5.0"
    ENV: str = "development"  # development, production, testing

    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8080
    LOG_LEVEL: str = "INFO"

    # 数据库配置
    DATABASE_URL: str = "sqlite:///./data/tokenmeter.db"

    # JWT 配置
    JWT_SECRET: str = ""
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24

    # 安全配置
    MAX_LOGIN_ATTEMPTS: int = 5
    LOGIN_LOCKOUT_MINUTES: int = 30
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_BURST: int = 10

    # 可选的外部 API Keys
    OPENAI_API_KEY: Optional[str] = None
    AZURE_OPENAI_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    DASHSCOPE_API_KEY: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = True


def get_settings() -> Settings:
    """获取配置实例"""
    settings = Settings()

    # 生产环境安全检查
    if settings.ENV == "production":
        # 检查 JWT_SECRET
        if not settings.JWT_SECRET or settings.JWT_SECRET == "your-secret-key-change-in-production":
            raise ValueError(
                "生产环境必须设置 JWT_SECRET 环境变量！\n"
                "请运行: export JWT_SECRET=$(openssl rand -hex 32)"
            )

        # 检查是否是默认密钥
        if len(settings.JWT_SECRET) < 32:
            raise ValueError(
                "JWT_SECRET 长度必须至少 32 个字符！\n"
                "请运行: export JWT_SECRET=$(openssl rand -hex 32)"
            )

    # 如果 JWT_SECRET 未设置，生成一个随机密钥（仅开发环境）
    if not settings.JWT_SECRET:
        if settings.ENV == "development":
            settings.JWT_SECRET = secrets.token_hex(32)
            print(f"警告: 使用随机生成的 JWT_SECRET (开发环境): {settings.JWT_SECRET}")
        else:
            raise ValueError("必须设置 JWT_SECRET 环境变量！")

    return settings


# 全局配置实例
settings = get_settings()
