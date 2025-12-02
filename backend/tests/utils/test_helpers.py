"""
Test Helper Utilities for BARQ Fleet Management Tests

Provides reusable utilities for:
- API testing helpers
- Assertion helpers
- Mock utilities
- Data generation
- Database helpers

Author: BARQ QA Team
Last Updated: 2025-12-02
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta, date
import random
import string


class APITestHelper:
    """Helper methods for API testing"""

    @staticmethod
    def assert_success_response(response, expected_status=200):
        """Assert successful API response"""
        assert response.status_code == expected_status, f"Expected {expected_status}, got {response.status_code}: {response.text}"
        data = response.json()
        assert data.get("success") is True, "Response should indicate success"
        return data

    @staticmethod
    def assert_error_response(response, expected_status=400):
        """Assert error API response"""
        assert response.status_code == expected_status, f"Expected {expected_status}, got {response.status_code}"
        data = response.json()
        assert "detail" in data or "message" in data, "Error response should contain detail or message"
        return data

    @staticmethod
    def assert_pagination(data, expected_page=1, expected_page_size=50):
        """Assert paginated response structure"""
        assert "items" in data, "Paginated response should have 'items'"
        assert "total" in data, "Paginated response should have 'total'"
        assert "page" in data, "Paginated response should have 'page'"
        assert "page_size" in data, "Paginated response should have 'page_size'"
        assert isinstance(data["items"], list), "'items' should be a list"
        assert data["page"] == expected_page, f"Expected page {expected_page}"
        assert data["page_size"] == expected_page_size, f"Expected page_size {expected_page_size}"


class DataGenerator:
    """Generate test data"""

    @staticmethod
    def random_string(length=10) -> str:
        """Generate random string"""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

    @staticmethod
    def random_email() -> str:
        """Generate random email"""
        return f"test_{DataGenerator.random_string(8)}@barq.test"

    @staticmethod
    def random_phone() -> str:
        """Generate random Saudi phone number"""
        return f"+9665{random.randint(10000000, 99999999)}"

    @staticmethod
    def random_barq_id() -> str:
        """Generate random BARQ ID"""
        return f"BRQ-{random.randint(10000, 99999)}"

    @staticmethod
    def random_plate_number() -> str:
        """Generate random plate number"""
        letters = ''.join(random.choices(string.ascii_uppercase, k=3))
        numbers = random.randint(1000, 9999)
        return f"{letters}-{numbers}"

    @staticmethod
    def future_date(days=30) -> date:
        """Generate future date"""
        return (datetime.now() + timedelta(days=days)).date()

    @staticmethod
    def past_date(days=30) -> date:
        """Generate past date"""
        return (datetime.now() - timedelta(days=days)).date()


class AssertionHelper:
    """Custom assertion helpers"""

    @staticmethod
    def assert_courier_equal(courier_dict: Dict[str, Any], courier_obj: Any):
        """Assert courier data matches object"""
        assert courier_dict["id"] == courier_obj.id
        assert courier_dict["barq_id"] == courier_obj.barq_id
        assert courier_dict["full_name"] == courier_obj.full_name
        assert courier_dict["email"] == courier_obj.email
        assert courier_dict["status"] == courier_obj.status.value

    @staticmethod
    def assert_vehicle_equal(vehicle_dict: Dict[str, Any], vehicle_obj: Any):
        """Assert vehicle data matches object"""
        assert vehicle_dict["id"] == vehicle_obj.id
        assert vehicle_dict["plate_number"] == vehicle_obj.plate_number
        assert vehicle_dict["make"] == vehicle_obj.make
        assert vehicle_dict["model"] == vehicle_obj.model
        assert vehicle_dict["status"] == vehicle_obj.status.value

    @staticmethod
    def assert_date_equal(date_str: Optional[str], date_obj: Optional[date]):
        """Assert date string matches date object"""
        if date_str is None and date_obj is None:
            return
        assert date_str is not None and date_obj is not None
        assert datetime.fromisoformat(date_str).date() == date_obj

    @staticmethod
    def assert_datetime_recent(dt: datetime, seconds=10):
        """Assert datetime is recent (within specified seconds)"""
        diff = abs((datetime.now() - dt).total_seconds())
        assert diff < seconds, f"Datetime {dt} is not recent (diff: {diff}s)"


class MockHelper:
    """Helper for creating mock objects"""

    @staticmethod
    def create_mock_response(status_code=200, json_data=None):
        """Create mock HTTP response"""
        class MockResponse:
            def __init__(self, status_code, json_data):
                self.status_code = status_code
                self._json_data = json_data

            def json(self):
                return self._json_data

        return MockResponse(status_code, json_data or {})


class DatabaseHelper:
    """Database testing helpers"""

    @staticmethod
    def count_records(db_session, model_class) -> int:
        """Count records in table"""
        return db_session.query(model_class).count()

    @staticmethod
    def get_by_id(db_session, model_class, record_id):
        """Get record by ID"""
        return db_session.query(model_class).filter(model_class.id == record_id).first()

    @staticmethod
    def delete_all(db_session, model_class):
        """Delete all records from table"""
        db_session.query(model_class).delete()
        db_session.commit()

    @staticmethod
    def assert_record_exists(db_session, model_class, **filters):
        """Assert record exists with given filters"""
        query = db_session.query(model_class)
        for key, value in filters.items():
            query = query.filter(getattr(model_class, key) == value)
        record = query.first()
        assert record is not None, f"Record not found with filters: {filters}"
        return record

    @staticmethod
    def assert_record_not_exists(db_session, model_class, **filters):
        """Assert record does not exist with given filters"""
        query = db_session.query(model_class)
        for key, value in filters.items():
            query = query.filter(getattr(model_class, key) == value)
        record = query.first()
        assert record is None, f"Record found with filters: {filters}"


class PerformanceHelper:
    """Performance testing helpers"""

    @staticmethod
    def measure_time(func, *args, **kwargs):
        """Measure function execution time"""
        import time
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        return result, end - start

    @staticmethod
    def assert_fast_execution(func, max_seconds=1.0, *args, **kwargs):
        """Assert function executes within time limit"""
        result, duration = PerformanceHelper.measure_time(func, *args, **kwargs)
        assert duration < max_seconds, f"Execution took {duration}s (max: {max_seconds}s)"
        return result
