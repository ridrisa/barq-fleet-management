"""Admin Module Schemas"""

from app.schemas.admin.api_key import (
    ApiKeyCreate,
    ApiKeyResponse,
    ApiKeyUpdate,
    ApiKeyWithSecret,
)
from app.schemas.admin.backup import (
    BackupCreate,
    BackupListResponse,
    BackupResponse,
    BackupUpdate,
)
from app.schemas.admin.integration import (
    IntegrationCreate,
    IntegrationResponse,
    IntegrationTestRequest,
    IntegrationUpdate,
)
from app.schemas.admin.monitoring import (
    APIMetricsResponse,
    DatabaseStatsResponse,
    SystemHealthResponse,
)
from app.schemas.admin.system_setting import (
    SystemSettingCreate,
    SystemSettingResponse,
    SystemSettingUpdate,
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
