"""
BigQuery Client Service for SANED Performance Data

Provides access to courier performance data from the BigQuery ultimate table.
Table: looker-barqdata-2030.master_saned.ultimate
"""

import logging
import os
from typing import Any, Dict, List, Optional

from google.cloud import bigquery
from google.oauth2 import service_account
import google.auth

from app.config.settings import settings

logger = logging.getLogger(__name__)


class BigQueryClient:
    """Client for querying BigQuery performance data from SANED"""

    def __init__(self):
        self._client: Optional[bigquery.Client] = None
        self._project_id = settings.BIGQUERY_PROJECT_ID
        self._dataset = settings.BIGQUERY_DATASET

    @property
    def client(self) -> bigquery.Client:
        """
        Lazy-load BigQuery client with credentials.

        Authentication priority:
        1. GOOGLE_APPLICATION_CREDENTIALS env var (service account or OAuth)
        2. BIGQUERY_CREDENTIALS_PATH setting (service account JSON)
        3. Application Default Credentials (gcloud auth, OAuth, or GCE)
        """
        if self._client is None:
            import json

            # Check for explicit credentials path in settings or env var
            credentials_path = settings.BIGQUERY_CREDENTIALS_PATH
            env_creds_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")

            # Use env var first, then settings
            creds_file = env_creds_path or credentials_path

            if creds_file and os.path.exists(creds_file):
                # Check if it's a service account file
                try:
                    with open(creds_file, 'r') as f:
                        creds_data = json.load(f)

                    if creds_data.get('type') == 'service_account':
                        # Use service account credentials directly
                        logger.info(f"Using service account credentials from: {creds_file}")
                        credentials = service_account.Credentials.from_service_account_file(
                            creds_file,
                            scopes=["https://www.googleapis.com/auth/bigquery"],
                        )
                        self._client = bigquery.Client(
                            project=self._project_id, credentials=credentials
                        )
                    else:
                        # Non-service account (OAuth refresh token, etc.)
                        logger.info(f"Using credentials file via ADC: {creds_file}")
                        credentials, project = google.auth.default(
                            scopes=["https://www.googleapis.com/auth/bigquery"]
                        )
                        self._client = bigquery.Client(
                            project=self._project_id or project,
                            credentials=credentials
                        )
                except Exception as e:
                    logger.warning(f"Failed to load credentials from {creds_file}: {e}")
                    # Fall back to ADC
                    try:
                        credentials, project = google.auth.default(
                            scopes=["https://www.googleapis.com/auth/bigquery"]
                        )
                        self._client = bigquery.Client(
                            project=self._project_id or project,
                            credentials=credentials
                        )
                    except Exception as e2:
                        logger.error(f"Failed to get ADC: {e2}")
                        self._client = bigquery.Client(project=self._project_id)
            else:
                # Fall back to Application Default Credentials
                logger.info("Using Application Default Credentials (OAuth/ADC)")
                try:
                    credentials, project = google.auth.default(
                        scopes=["https://www.googleapis.com/auth/bigquery"]
                    )
                    self._client = bigquery.Client(
                        project=self._project_id or project,
                        credentials=credentials
                    )
                except Exception as e:
                    logger.warning(f"Failed to get ADC: {e}. Trying without explicit credentials.")
                    self._client = bigquery.Client(project=self._project_id)
        return self._client

    @property
    def table_ref(self) -> str:
        """Full table reference"""
        return f"{self._project_id}.{self._dataset}.ultimate"

    def query(self, sql: str, params: Optional[Dict[str, Any]] = None) -> List[Dict]:
        """Execute a BigQuery SQL query and return results as list of dicts"""
        job_config = bigquery.QueryJobConfig()

        if params:
            job_config.query_parameters = [
                bigquery.ScalarQueryParameter(k, "STRING", v)
                for k, v in params.items()
            ]

        query_job = self.client.query(sql, job_config=job_config)
        results = query_job.result()

        return [dict(row) for row in results]

    def get_courier_by_barq_id(self, barq_id: int) -> Optional[Dict]:
        """Get courier data by BARQ_ID"""
        sql = f"""
        SELECT *
        FROM `{self.table_ref}`
        WHERE BARQ_ID = @barq_id
        LIMIT 1
        """
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("barq_id", "INT64", barq_id)
            ]
        )
        query_job = self.client.query(sql, job_config=job_config)
        results = list(query_job.result())

        if results:
            return dict(results[0])
        return None

    def get_all_couriers(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        city: Optional[str] = None,
    ) -> List[Dict]:
        """Get all couriers with optional filtering"""
        where_clauses = []
        params = []

        if status:
            where_clauses.append("Status = @status")
            params.append(bigquery.ScalarQueryParameter("status", "STRING", status))
        if city:
            where_clauses.append("city = @city")
            params.append(bigquery.ScalarQueryParameter("city", "STRING", city))

        where_sql = ""
        if where_clauses:
            where_sql = "WHERE " + " AND ".join(where_clauses)

        sql = f"""
        SELECT
            BARQ_ID,
            Name,
            id_number,
            mobile_number,
            Status,
            SponsorshipStatus,
            PROJECT,
            Supervisor,
            city,
            Car,
            Plate,
            Vehicle_Mileage,
            joining_Date,
            last_working_day,
            WPS,
            IBAN,
            Gas_Usage_without_VAT,
            Jahez_Orders,
            Jahez_Revenue,
            Barq_Orders,
            Barq_Revenue,
            Amazon_Revenue,
            Kaykroo_Revenue,
            Mealme_Revenue,
            Chalhoub_Revenue,
            SPL_WH_Orders,
            SPL_WH_Revenue,
            SPL_DS_Orders,
            SPL_DS_Revenue,
            Chefz_Orders,
            Chefz_Revenue,
            Hunger_Orders,
            Hunger_Revenue,
            Mrsool_Orders,
            Mrsool_Revenue,
            Keeta_Orders,
            Keeta_Revenue,
            Total_Orders,
            Total_Revenue
        FROM `{self.table_ref}`
        {where_sql}
        ORDER BY BARQ_ID
        LIMIT @limit OFFSET @skip
        """
        params.extend(
            [
                bigquery.ScalarQueryParameter("limit", "INT64", limit),
                bigquery.ScalarQueryParameter("skip", "INT64", skip),
            ]
        )

        job_config = bigquery.QueryJobConfig(query_parameters=params)
        query_job = self.client.query(sql, job_config=job_config)

        return [dict(row) for row in query_job.result()]

    def get_performance_metrics(
        self, skip: int = 0, limit: int = 100, status: str = "Active"
    ) -> List[Dict]:
        """Get courier performance metrics for the performance dashboard"""
        sql = f"""
        SELECT
            BARQ_ID as barq_id,
            Name as name,
            Status as status,
            city,
            Car as vehicle,
            Plate as plate,
            Total_Orders as total_orders,
            Total_Revenue as total_revenue,
            Gas_Usage_without_VAT as fuel_cost,
            Jahez_Orders as jahez_orders,
            Jahez_Revenue as jahez_revenue,
            Barq_Orders as barq_orders,
            Barq_Revenue as barq_revenue,
            Mrsool_Orders as mrsool_orders,
            Mrsool_Revenue as mrsool_revenue,
            Hunger_Orders as hunger_orders,
            Hunger_Revenue as hunger_revenue,
            Chefz_Orders as chefz_orders,
            Chefz_Revenue as chefz_revenue,
            Keeta_Orders as keeta_orders,
            Keeta_Revenue as keeta_revenue,
            SPL_WH_Orders as spl_wh_orders,
            SPL_WH_Revenue as spl_wh_revenue,
            SPL_DS_Orders as spl_ds_orders,
            SPL_DS_Revenue as spl_ds_revenue,
            Amazon_Revenue as amazon_revenue
        FROM `{self.table_ref}`
        WHERE Status = @status
        ORDER BY Total_Revenue DESC
        LIMIT @limit OFFSET @skip
        """
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("status", "STRING", status),
                bigquery.ScalarQueryParameter("limit", "INT64", limit),
                bigquery.ScalarQueryParameter("skip", "INT64", skip),
            ]
        )
        query_job = self.client.query(sql, job_config=job_config)

        return [dict(row) for row in query_job.result()]

    def get_performance_summary(self) -> Dict:
        """Get aggregate performance summary for all active couriers"""
        sql = f"""
        SELECT
            COUNT(*) as total_couriers,
            COUNT(CASE WHEN Status = 'Active' THEN 1 END) as active_couriers,
            SUM(Total_Orders) as total_orders,
            SUM(Total_Revenue) as total_revenue,
            AVG(Total_Orders) as avg_orders_per_courier,
            AVG(Total_Revenue) as avg_revenue_per_courier,
            SUM(Gas_Usage_without_VAT) as total_fuel_cost,
            COUNT(DISTINCT city) as cities_count,
            COUNT(DISTINCT Car) as vehicle_types_count
        FROM `{self.table_ref}`
        """
        query_job = self.client.query(sql)
        results = list(query_job.result())

        if results:
            return dict(results[0])
        return {}

    def get_city_breakdown(self) -> List[Dict]:
        """Get performance breakdown by city"""
        sql = f"""
        SELECT
            city,
            COUNT(*) as courier_count,
            COUNT(CASE WHEN Status = 'Active' THEN 1 END) as active_count,
            SUM(Total_Orders) as total_orders,
            SUM(Total_Revenue) as total_revenue,
            AVG(Total_Orders) as avg_orders,
            AVG(Total_Revenue) as avg_revenue
        FROM `{self.table_ref}`
        WHERE city IS NOT NULL
        GROUP BY city
        ORDER BY total_revenue DESC
        """
        query_job = self.client.query(sql)

        return [dict(row) for row in query_job.result()]

    def get_platform_breakdown(self) -> List[Dict]:
        """Get order and revenue breakdown by platform"""
        sql = f"""
        SELECT
            'Jahez' as platform,
            SUM(Jahez_Orders) as total_orders,
            SUM(Jahez_Revenue) as total_revenue
        FROM `{self.table_ref}`
        UNION ALL
        SELECT
            'Barq' as platform,
            SUM(Barq_Orders) as total_orders,
            SUM(Barq_Revenue) as total_revenue
        FROM `{self.table_ref}`
        UNION ALL
        SELECT
            'Mrsool' as platform,
            SUM(Mrsool_Orders) as total_orders,
            SUM(Mrsool_Revenue) as total_revenue
        FROM `{self.table_ref}`
        UNION ALL
        SELECT
            'Hunger' as platform,
            SUM(Hunger_Orders) as total_orders,
            SUM(Hunger_Revenue) as total_revenue
        FROM `{self.table_ref}`
        UNION ALL
        SELECT
            'Keeta' as platform,
            SUM(Keeta_Orders) as total_orders,
            SUM(Keeta_Revenue) as total_revenue
        FROM `{self.table_ref}`
        UNION ALL
        SELECT
            'Chefz' as platform,
            SUM(Chefz_Orders) as total_orders,
            SUM(Chefz_Revenue) as total_revenue
        FROM `{self.table_ref}`
        UNION ALL
        SELECT
            'Amazon' as platform,
            0 as total_orders,
            SUM(Amazon_Revenue) as total_revenue
        FROM `{self.table_ref}`
        UNION ALL
        SELECT
            'SPL Warehouse' as platform,
            SUM(SPL_WH_Orders) as total_orders,
            SUM(SPL_WH_Revenue) as total_revenue
        FROM `{self.table_ref}`
        UNION ALL
        SELECT
            'SPL Direct' as platform,
            SUM(SPL_DS_Orders) as total_orders,
            SUM(SPL_DS_Revenue) as total_revenue
        FROM `{self.table_ref}`
        ORDER BY total_revenue DESC
        """
        query_job = self.client.query(sql)

        return [dict(row) for row in query_job.result()]

    def search_couriers(self, search_term: str, limit: int = 20) -> List[Dict]:
        """Search couriers by name, BARQ_ID, or mobile number"""
        sql = f"""
        SELECT
            BARQ_ID,
            Name,
            mobile_number,
            Status,
            city,
            Total_Orders,
            Total_Revenue
        FROM `{self.table_ref}`
        WHERE
            CAST(BARQ_ID AS STRING) LIKE @search_term
            OR LOWER(Name) LIKE @search_lower
            OR mobile_number LIKE @search_term
        ORDER BY Total_Revenue DESC
        LIMIT @limit
        """
        search_pattern = f"%{search_term}%"
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("search_term", "STRING", search_pattern),
                bigquery.ScalarQueryParameter(
                    "search_lower", "STRING", search_pattern.lower()
                ),
                bigquery.ScalarQueryParameter("limit", "INT64", limit),
            ]
        )
        query_job = self.client.query(sql, job_config=job_config)

        return [dict(row) for row in query_job.result()]

    def health_check(self) -> Dict[str, Any]:
        """Check BigQuery connection health"""
        try:
            # Simple query to verify connection
            sql = f"SELECT COUNT(*) as count FROM `{self.table_ref}` LIMIT 1"
            query_job = self.client.query(sql)
            result = list(query_job.result())
            return {
                "status": "healthy",
                "project": self._project_id,
                "dataset": self._dataset,
                "table": "ultimate",
                "row_count": result[0]["count"] if result else 0,
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "project": self._project_id,
                "dataset": self._dataset,
                "table": "ultimate",  # Required field
            }


# Singleton instance
bigquery_client = BigQueryClient()
