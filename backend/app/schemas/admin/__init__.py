"""Admin Module Schemas"""
from app.schemas.admin.api_key import (
    ApiKeyCreate,
    ApiKeyUpdate,
    ApiKeyResponse,
    ApiKeyWithSecret,
)
from app.schemas.admin.integration import (
    IntegrationCreate,
    IntegrationUpdate,
    IntegrationResponse,
    IntegrationTestRequest,
)
from app.schemas.admin.system_setting import (
    SystemSettingCreate,
    SystemSettingUpdate,
    SystemSettingResponse,
)
from app.schemas.admin.backup import (
    BackupCreate,
    BackupUpdate,
    BackupResponse,
    BackupListResponse,
)
from app.schemas.admin.monitoring import (
    SystemHealthResponse,
    DatabaseStatsResponse,
    APIMetricsResponse,
)

__all__ = [
    "ApiKeyCreate",
    "ApiKeyUpdate",
    "ApiKeyResponse",
    "ApiKeyWithSecret",
    "IntegrationCreate",
    "IntegrationUpdate",
    "IntegrationResponse",
    "IntegrationTestRequest",
    "SystemSettingCreate",
    "SystemSettingUpdate",
    "SystemSettingResponse",
    "BackupCreate",
    "BackupUpdate",
    "BackupResponse",
    "BackupListResponse",
    "SystemHealthResponse",
    "DatabaseStatsResponse",
    "APIMetricsResponse",
]
