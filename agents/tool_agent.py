"""
ToolAgent: Handles saving issues to DB and simulating email dispatch.
Image is saved as raw bytes — no Pillow dependency needed at this layer.
"""
from django.utils import timezone


class ToolAgent:
    def __init__(self):
        self.agent_name = "ToolAgent"

    # ------------------------------------------------------------------
    def save_issue(self, data: dict):
        """
        Save a new Issue to the database.
        Accepts raw_bytes + filename to store the image without Pillow.
        """
        from core.models import Issue
        from django.core.files.base import ContentFile

        print(f"[{self.agent_name}] Saving issue to database...")

        issue = Issue(
            issue_type    = data.get('issue_type', 'unknown'),
            location      = data.get('location', 'Unknown Location'),
            severity      = data.get('severity', 'medium'),
            description   = data.get('description', ''),
            complaint_text= data.get('complaint_text', ''),
            status        = 'pending',
            department    = data.get('department'),
            escalation_level = 0,
            confidence    = data.get('confidence', 0.0),
            deadline_hours= data.get('deadline_hours', 48),
        )

        # Save image via raw bytes — no Pillow needed
        raw_bytes = data.get('raw_bytes')
        filename  = data.get('filename', 'upload.jpg')
        if raw_bytes:
            issue.image.save(filename, ContentFile(raw_bytes), save=False)

        issue.save()
        print(f"[{self.agent_name}] Issue #{issue.id} saved")
        return issue

    # ------------------------------------------------------------------
    def send_complaint(self, issue) -> dict:
        """Simulate sending complaint email (print/log)."""
        dept_name  = issue.department.name  if issue.department else "Unassigned"
        dept_email = issue.department.email if issue.department else "unknown@gov.in"

        log = (
            f"\n{'='*60}\n"
            f"[SIMULATED EMAIL]\n"
            f"To: {dept_email} ({dept_name})\n"
            f"Issue #{issue.id} | {issue.issue_type} | {issue.severity.upper()}\n"
            f"Location: {issue.location}\n"
            f"Body:\n{issue.complaint_text}\n"
            f"{'='*60}\n"
        )
        print(log)

        issue.status       = 'sent'
        issue.last_updated = timezone.now()
        issue.save()

        if issue.department:
            issue.department.total_issues += 1
            issue.department.save()
            issue.department.update_rating()

        return {
            'sent':       True,
            'to':         dept_email,
            'department': dept_name,
            'issue_id':   issue.id,
            'agent':      self.agent_name,
        }

    # ------------------------------------------------------------------
    def resolve_issue(self, issue_id: int) -> dict:
        from core.models import Issue
        try:
            issue              = Issue.objects.get(id=issue_id)
            issue.status       = 'resolved'
            issue.resolved_at  = timezone.now()
            issue.last_updated = timezone.now()
            issue.save()
            if issue.department:
                issue.department.resolved_issues += 1
                issue.department.update_rating()
            print(f"[{self.agent_name}] Issue #{issue_id} resolved")
            return {'success': True, 'issue_id': issue_id}
        except Issue.DoesNotExist:
            return {'success': False, 'error': f'Issue #{issue_id} not found'}
