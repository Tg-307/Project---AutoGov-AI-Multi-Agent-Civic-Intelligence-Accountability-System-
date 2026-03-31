"""
ValidationAgent: Validates detection confidence and checks for duplicate issues.
Filters out low-confidence detections and near-duplicate reports.
"""
from datetime import timedelta
from django.utils import timezone


class ValidationAgent:
    """
    Agent responsible for:
    1. Filtering detections below confidence threshold
    2. Detecting duplicate/near-duplicate reports
    3. Assigning severity based on issue type + confidence
    """

    CONFIDENCE_THRESHOLD = 0.50

    SEVERITY_MAP = {
        'pothole': {
            'high_confidence': 'high',
            'medium_confidence': 'medium',
            'low_confidence': 'low',
        },
        'garbage': {
            'high_confidence': 'medium',
            'medium_confidence': 'medium',
            'low_confidence': 'low',
        },
        'broken_streetlight': {
            'high_confidence': 'medium',
            'medium_confidence': 'low',
            'low_confidence': 'low',
        },
        'open_drain': {
            'high_confidence': 'high',
            'medium_confidence': 'medium',
            'low_confidence': 'low',
        },
        'encroachment': {
            'high_confidence': 'medium',
            'medium_confidence': 'low',
            'low_confidence': 'low',
        },
    }

    DEADLINE_MAP = {
        'critical': 12,
        'high': 24,
        'medium': 48,
        'low': 72,
    }

    def __init__(self):
        self.agent_name = "ValidationAgent"

    def validate(self, detection: dict, location: str) -> dict:
        """
        Validate a detection result.
        Returns: {valid, reason, severity, is_duplicate, deadline_hours}
        """
        print(f"[{self.agent_name}] Validating detection for: {detection.get('issue_type')}")

        confidence = detection.get('confidence', 0.0)
        issue_type = detection.get('issue_type', '')

        # Confidence check
        if confidence < self.CONFIDENCE_THRESHOLD:
            return {
                'valid': False,
                'reason': f"Confidence {confidence:.2f} below threshold {self.CONFIDENCE_THRESHOLD}",
                'severity': None,
                'is_duplicate': False,
                'deadline_hours': 48,
            }

        # Determine severity
        severity = self._compute_severity(issue_type, confidence)

        # Duplicate check
        is_duplicate, duplicate_id = self._check_duplicate(issue_type, location)

        result = {
            'valid': True,
            'reason': 'Passed validation',
            'severity': severity,
            'is_duplicate': is_duplicate,
            'duplicate_issue_id': duplicate_id,
            'deadline_hours': self.DEADLINE_MAP.get(severity, 48),
            'agent': self.agent_name,
        }

        print(f"[{self.agent_name}] Valid={result['valid']}, Severity={severity}, Duplicate={is_duplicate}")
        return result

    def _compute_severity(self, issue_type: str, confidence: float) -> str:
        """Map confidence level to severity category."""
        severity_rules = self.SEVERITY_MAP.get(issue_type, {
            'high_confidence': 'medium',
            'medium_confidence': 'low',
            'low_confidence': 'low',
        })

        if confidence >= 0.80:
            return severity_rules['high_confidence']
        elif confidence >= 0.65:
            return severity_rules['medium_confidence']
        else:
            return severity_rules['low_confidence']

    def _check_duplicate(self, issue_type: str, location: str):
        """Check if a similar issue was reported in the last 24 hours."""
        try:
            from core.models import Issue
            cutoff = timezone.now() - timedelta(hours=24)
            duplicate = Issue.objects.filter(
                issue_type=issue_type,
                location__icontains=location[:20] if location else '',
                created_at__gte=cutoff,
                status__in=['pending', 'sent', 'in_progress'],
            ).first()
            if duplicate:
                return True, duplicate.id
        except Exception as e:
            print(f"[{self.agent_name}] Duplicate check error: {e}")
        return False, None
