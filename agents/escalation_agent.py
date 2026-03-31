"""
EscalationAgent: Monitors issue deadlines and triggers escalation workflows.
Runs on demand or via simulated time trigger endpoint.
"""
from django.utils import timezone


SEVERITY_ESCALATION = {
    'low': 'medium',
    'medium': 'high',
    'high': 'critical',
    'critical': 'critical',
}


class EscalationAgent:
    """
    Agent responsible for:
    1. Checking if issues are past deadline
    2. Incrementing escalation level
    3. Upgrading severity
    4. Logging escalation history
    """

    MAX_ESCALATION = 3

    def __init__(self):
        self.agent_name = "EscalationAgent"

    def check_and_escalate(self, simulate_hours: float = None) -> list:
        """
        Check all unresolved issues and escalate those past deadline.
        simulate_hours: if set, treat issues older than X hours as overdue.
        Returns list of escalated issue IDs.
        """
        from core.models import Issue
        print(f"[{self.agent_name}] Running escalation check...")

        pending_issues = Issue.objects.filter(
            status__in=['pending', 'sent', 'in_progress']
        )

        escalated = []
        for issue in pending_issues:
            if self._is_overdue(issue, simulate_hours):
                result = self.escalate_issue(issue)
                if result:
                    escalated.append(issue.id)

        print(f"[{self.agent_name}] Escalated {len(escalated)} issues: {escalated}")
        return escalated

    def escalate_issue(self, issue) -> bool:
        """
        Escalate a single issue.
        Returns True if escalation occurred.
        """
        from core.models import EscalationLog
        from agents.complaint_agent import ComplaintAgent
        from agents.routing_agent import RoutingAgent

        if issue.escalation_level >= self.MAX_ESCALATION:
            print(f"[{self.agent_name}] Issue #{issue.id} already at max escalation")
            return False

        old_level = issue.escalation_level
        issue.escalation_level += 1
        issue.severity = SEVERITY_ESCALATION.get(issue.severity, 'critical')
        issue.status = 'escalated'
        issue.last_updated = timezone.now()

        # Regenerate complaint with stronger wording
        complaint_agent = ComplaintAgent()
        issue_data = {
            'issue_type': issue.issue_type,
            'location': issue.location,
            'severity': issue.severity,
            'confidence': issue.confidence,
            'issue_id': issue.id,
        }
        complaint_result = complaint_agent.generate(issue_data, issue.escalation_level)
        issue.complaint_text = complaint_result['complaint_text']

        # Re-route if max escalation
        if issue.escalation_level >= self.MAX_ESCALATION:
            routing_agent = RoutingAgent()
            routing = routing_agent.route(issue.issue_type, issue.escalation_level)
            if routing.get('department'):
                issue.department = routing['department']

        issue.save()

        # Log escalation
        EscalationLog.objects.create(
            issue=issue,
            level=issue.escalation_level,
            complaint_text=issue.complaint_text,
            reason=f"Deadline exceeded at level {old_level}",
        )

        # Update department stats
        if issue.department:
            issue.department.escalated_issues += 1
            issue.department.update_rating()

        print(f"[{self.agent_name}] Issue #{issue.id} escalated L{old_level}→L{issue.escalation_level}, severity={issue.severity}")
        return True

    def _is_overdue(self, issue, simulate_hours=None) -> bool:
        """Check if issue has exceeded its deadline."""
        from datetime import timedelta
        if simulate_hours is not None:
            # In simulation mode: treat issue as being simulate_hours old
            simulated_age = simulate_hours
            return simulated_age >= issue.deadline_hours
        else:
            deadline = issue.created_at + timedelta(hours=issue.deadline_hours)
            return timezone.now() > deadline
