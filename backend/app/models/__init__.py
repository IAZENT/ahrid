"""SQLAlchemy model registry  importing this module registers every table."""
from app.models.attempt import Attempt
from app.models.audit_log import AuditLog
from app.models.awareness_assessment import AwarenessAssessment
from app.models.behavior_event import UserBehaviorEvent
from app.models.cluster import UserCluster
from app.models.notification import Notification
from app.models.password_reset import PasswordResetRequest
from app.models.risk_score import RiskScore
from app.models.scenario import Scenario
from app.models.sus_response import SUSResponse
from app.models.threat_feed import ThreatFeedEntry
from app.models.token_blocklist import TokenBlocklist
from app.models.user import User

__all__ = [
    "Attempt",
    "AuditLog",
    "AwarenessAssessment",
    "Notification",
    "PasswordResetRequest",
    "RiskScore",
    "Scenario",
    "SUSResponse",
    "ThreatFeedEntry",
    "TokenBlocklist",
    "User",
    "UserBehaviorEvent",
    "UserCluster",
]
