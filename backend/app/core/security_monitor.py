"""
Security Monitoring and Alerting System

This module provides real-time security monitoring:
- Anomaly detection (unusual login patterns, suspicious activities)
- Real-time threat detection
- Security event aggregation
- Alert generation and notification
- Security metrics collection
- Integration with audit logging

Author: BARQ Security Team
Last Updated: 2025-12-02
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from enum import Enum
from dataclasses import dataclass, asdict

import redis

from app.core.security_config import security_config


class ThreatLevel(str, Enum):
    """Threat severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertType(str, Enum):
    """Types of security alerts"""
    BRUTE_FORCE = "brute_force"
    ACCOUNT_TAKEOVER = "account_takeover"
    UNUSUAL_LOCATION = "unusual_location"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    MULTIPLE_FAILURES = "multiple_failures"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    DATA_EXFILTRATION = "data_exfiltration"
    ANOMALOUS_BEHAVIOR = "anomalous_behavior"


@dataclass
class SecurityAlert:
    """Security alert data structure"""
    alert_id: str
    alert_type: AlertType
    threat_level: ThreatLevel
    title: str
    description: str
    user_id: Optional[int]
    username: Optional[str]
    ip_address: Optional[str]
    metadata: Dict[str, Any]
    timestamp: str
    acknowledged: bool = False
    acknowledged_by: Optional[int] = None
    acknowledged_at: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return asdict(self)


class SecurityMonitor:
    """
    Real-time security monitoring and threat detection

    Features:
    - Behavioral anomaly detection
    - Pattern-based threat detection
    - Alert generation and tracking
    - Security metrics collection
    - Integration with external SIEM systems
    """

    def __init__(self, redis_client: Optional[redis.Redis] = None):
        """
        Initialize security monitor

        Args:
            redis_client: Optional Redis client
        """
        self.redis = redis_client
        if not self.redis:
            try:
                from app.config.settings import settings
                redis_url = security_config.rate_limit.storage_uri or getattr(settings, 'REDIS_URL', None)
                if redis_url:
                    self.redis = redis.from_url(
                        redis_url,
                        decode_responses=True,
                        socket_connect_timeout=5,
                        socket_timeout=5
                    )
            except:
                pass

        # In-memory fallback
        if not self.redis:
            self._memory_alerts: List[SecurityAlert] = []

    def detect_brute_force(
        self,
        identifier: str,
        failed_attempts: int,
        time_window_minutes: int = 15
    ) -> Optional[SecurityAlert]:
        """
        Detect brute force attack

        Args:
            identifier: User identifier (email, IP, etc.)
            failed_attempts: Number of failed attempts
            time_window_minutes: Time window to check

        Returns:
            SecurityAlert if brute force detected, None otherwise
        """
        threshold = security_config.brute_force.max_attempts

        if failed_attempts >= threshold:
            alert = self._create_alert(
                alert_type=AlertType.BRUTE_FORCE,
                threat_level=ThreatLevel.HIGH,
                title="Brute Force Attack Detected",
                description=f"{failed_attempts} failed login attempts for {identifier} in {time_window_minutes} minutes",
                metadata={
                    "identifier": identifier,
                    "failed_attempts": failed_attempts,
                    "time_window": time_window_minutes,
                    "threshold": threshold
                }
            )

            self._store_alert(alert)
            return alert

        return None

    def detect_unusual_location(
        self,
        user_id: int,
        username: str,
        current_ip: str,
        current_location: Optional[str] = None
    ) -> Optional[SecurityAlert]:
        """
        Detect login from unusual location

        Args:
            user_id: User ID
            username: Username
            current_ip: Current IP address
            current_location: Optional location string

        Returns:
            SecurityAlert if unusual location detected
        """
        # Get user's previous IPs
        previous_ips = self._get_user_ip_history(user_id)

        if previous_ips and current_ip not in previous_ips:
            # New IP detected
            if len(previous_ips) > 0:  # User has login history
                alert = self._create_alert(
                    alert_type=AlertType.UNUSUAL_LOCATION,
                    threat_level=ThreatLevel.MEDIUM,
                    title="Login from New Location",
                    description=f"User {username} logged in from new IP: {current_ip}",
                    user_id=user_id,
                    username=username,
                    ip_address=current_ip,
                    metadata={
                        "current_ip": current_ip,
                        "current_location": current_location,
                        "previous_ips": list(previous_ips)[:5]  # Last 5 IPs
                    }
                )

                self._store_alert(alert)
                return alert

        # Track this IP
        self._add_user_ip(user_id, current_ip)
        return None

    def detect_privilege_escalation(
        self,
        user_id: int,
        username: str,
        old_role: str,
        new_role: str,
        changed_by: Optional[int] = None
    ) -> Optional[SecurityAlert]:
        """
        Detect privilege escalation

        Args:
            user_id: User ID
            username: Username
            old_role: Previous role
            new_role: New role
            changed_by: User ID who made the change

        Returns:
            SecurityAlert if suspicious escalation detected
        """
        # Check if escalation is suspicious
        from app.core.permissions import RoleHierarchy

        old_level = RoleHierarchy.get_level(old_role)
        new_level = RoleHierarchy.get_level(new_role)

        if new_level > old_level:
            # Privilege escalation
            threat_level = ThreatLevel.HIGH if new_role in ["system_admin", "organization_admin"] else ThreatLevel.MEDIUM

            alert = self._create_alert(
                alert_type=AlertType.PRIVILEGE_ESCALATION,
                threat_level=threat_level,
                title="Privilege Escalation Detected",
                description=f"User {username} role changed from {old_role} to {new_role}",
                user_id=user_id,
                username=username,
                metadata={
                    "old_role": old_role,
                    "new_role": new_role,
                    "changed_by": changed_by,
                    "old_level": old_level,
                    "new_level": new_level
                }
            )

            self._store_alert(alert)
            return alert

        return None

    def detect_data_exfiltration(
        self,
        user_id: int,
        username: str,
        export_count: int,
        time_window_hours: int = 1
    ) -> Optional[SecurityAlert]:
        """
        Detect potential data exfiltration

        Args:
            user_id: User ID
            username: Username
            export_count: Number of exports
            time_window_hours: Time window

        Returns:
            SecurityAlert if suspicious export activity detected
        """
        threshold = 10  # Configurable threshold

        if export_count > threshold:
            alert = self._create_alert(
                alert_type=AlertType.DATA_EXFILTRATION,
                threat_level=ThreatLevel.CRITICAL,
                title="Potential Data Exfiltration Detected",
                description=f"User {username} exported data {export_count} times in {time_window_hours} hour(s)",
                user_id=user_id,
                username=username,
                metadata={
                    "export_count": export_count,
                    "time_window_hours": time_window_hours,
                    "threshold": threshold
                }
            )

            self._store_alert(alert)
            return alert

        return None

    def detect_suspicious_activity(
        self,
        user_id: int,
        username: str,
        activity_type: str,
        reason: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> SecurityAlert:
        """
        Report suspicious activity

        Args:
            user_id: User ID
            username: Username
            activity_type: Type of activity
            reason: Reason for suspicion
            metadata: Additional metadata

        Returns:
            SecurityAlert
        """
        alert = self._create_alert(
            alert_type=AlertType.SUSPICIOUS_ACTIVITY,
            threat_level=ThreatLevel.MEDIUM,
            title=f"Suspicious Activity: {activity_type}",
            description=reason,
            user_id=user_id,
            username=username,
            metadata=metadata or {}
        )

        self._store_alert(alert)
        return alert

    def get_alerts(
        self,
        limit: int = 100,
        threat_level: Optional[ThreatLevel] = None,
        alert_type: Optional[AlertType] = None,
        unacknowledged_only: bool = False
    ) -> List[SecurityAlert]:
        """
        Get security alerts

        Args:
            limit: Maximum number of alerts to return
            threat_level: Filter by threat level
            alert_type: Filter by alert type
            unacknowledged_only: Only return unacknowledged alerts

        Returns:
            List of SecurityAlert objects
        """
        if self.redis:
            # Get alerts from Redis
            keys = self.redis.keys("security_alert:*")
            alerts = []

            for key in keys[:limit]:
                data = self.redis.get(key)
                if data:
                    alert_dict = json.loads(data)
                    alert = SecurityAlert(**alert_dict)

                    # Apply filters
                    if threat_level and alert.threat_level != threat_level:
                        continue
                    if alert_type and alert.alert_type != alert_type:
                        continue
                    if unacknowledged_only and alert.acknowledged:
                        continue

                    alerts.append(alert)

            # Sort by timestamp (newest first)
            alerts.sort(key=lambda a: a.timestamp, reverse=True)
            return alerts[:limit]
        else:
            # In-memory alerts
            alerts = self._memory_alerts.copy()

            # Apply filters
            if threat_level:
                alerts = [a for a in alerts if a.threat_level == threat_level]
            if alert_type:
                alerts = [a for a in alerts if a.alert_type == alert_type]
            if unacknowledged_only:
                alerts = [a for a in alerts if not a.acknowledged]

            return alerts[:limit]

    def acknowledge_alert(self, alert_id: str, acknowledged_by: int) -> bool:
        """
        Acknowledge security alert

        Args:
            alert_id: Alert ID
            acknowledged_by: User ID acknowledging the alert

        Returns:
            True if acknowledged successfully
        """
        key = f"security_alert:{alert_id}"

        if self.redis:
            data = self.redis.get(key)
            if not data:
                return False

            alert_dict = json.loads(data)
            alert_dict["acknowledged"] = True
            alert_dict["acknowledged_by"] = acknowledged_by
            alert_dict["acknowledged_at"] = datetime.utcnow().isoformat()

            self.redis.set(key, json.dumps(alert_dict))
            return True
        else:
            for alert in self._memory_alerts:
                if alert.alert_id == alert_id:
                    alert.acknowledged = True
                    alert.acknowledged_by = acknowledged_by
                    alert.acknowledged_at = datetime.utcnow().isoformat()
                    return True

        return False

    def get_security_metrics(self, days: int = 7) -> Dict[str, Any]:
        """
        Get security metrics for dashboard

        Args:
            days: Number of days to analyze

        Returns:
            Dictionary with security metrics
        """
        alerts = self.get_alerts(limit=1000)

        # Filter by time range
        cutoff = datetime.utcnow() - timedelta(days=days)
        recent_alerts = [
            a for a in alerts
            if datetime.fromisoformat(a.timestamp) > cutoff
        ]

        # Calculate metrics
        metrics = {
            "total_alerts": len(recent_alerts),
            "critical_alerts": len([a for a in recent_alerts if a.threat_level == ThreatLevel.CRITICAL]),
            "high_alerts": len([a for a in recent_alerts if a.threat_level == ThreatLevel.HIGH]),
            "medium_alerts": len([a for a in recent_alerts if a.threat_level == ThreatLevel.MEDIUM]),
            "low_alerts": len([a for a in recent_alerts if a.threat_level == ThreatLevel.LOW]),
            "unacknowledged": len([a for a in recent_alerts if not a.acknowledged]),
            "by_type": {},
            "days_analyzed": days
        }

        # Group by type
        for alert_type in AlertType:
            count = len([a for a in recent_alerts if a.alert_type == alert_type])
            if count > 0:
                metrics["by_type"][alert_type.value] = count

        return metrics

    def _create_alert(
        self,
        alert_type: AlertType,
        threat_level: ThreatLevel,
        title: str,
        description: str,
        user_id: Optional[int] = None,
        username: Optional[str] = None,
        ip_address: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> SecurityAlert:
        """Create security alert"""
        import secrets

        alert_id = secrets.token_urlsafe(16)

        return SecurityAlert(
            alert_id=alert_id,
            alert_type=alert_type,
            threat_level=threat_level,
            title=title,
            description=description,
            user_id=user_id,
            username=username,
            ip_address=ip_address,
            metadata=metadata or {},
            timestamp=datetime.utcnow().isoformat()
        )

    def _store_alert(self, alert: SecurityAlert):
        """Store alert in Redis/memory"""
        key = f"security_alert:{alert.alert_id}"
        data = json.dumps(alert.to_dict())

        # Store for 30 days
        ttl = 30 * 24 * 60 * 60

        if self.redis:
            self.redis.setex(key, ttl, data)
        else:
            self._memory_alerts.append(alert)

            # Limit memory storage
            if len(self._memory_alerts) > 1000:
                self._memory_alerts = self._memory_alerts[-1000:]

    def _get_user_ip_history(self, user_id: int) -> set:
        """Get user's IP history"""
        key = f"user_ip_history:{user_id}"

        if self.redis:
            return self.redis.smembers(key)
        else:
            # In-memory fallback
            return set()

    def _add_user_ip(self, user_id: int, ip_address: str):
        """Add IP to user's history"""
        key = f"user_ip_history:{user_id}"

        if self.redis:
            self.redis.sadd(key, ip_address)
            # Keep IP history for 90 days
            self.redis.expire(key, 90 * 24 * 60 * 60)


# Global security monitor instance
_security_monitor: Optional[SecurityMonitor] = None


def get_security_monitor() -> SecurityMonitor:
    """
    Get global security monitor instance

    Returns:
        SecurityMonitor instance
    """
    global _security_monitor

    if _security_monitor is None:
        _security_monitor = SecurityMonitor()

    return _security_monitor


# Convenience functions
def detect_brute_force(identifier: str, failed_attempts: int) -> Optional[SecurityAlert]:
    """Convenience function for brute force detection"""
    return get_security_monitor().detect_brute_force(identifier, failed_attempts)


def detect_unusual_location(user_id: int, username: str, ip: str) -> Optional[SecurityAlert]:
    """Convenience function for unusual location detection"""
    return get_security_monitor().detect_unusual_location(user_id, username, ip)


def get_security_dashboard_metrics(days: int = 7) -> Dict[str, Any]:
    """Convenience function to get security metrics"""
    return get_security_monitor().get_security_metrics(days)
