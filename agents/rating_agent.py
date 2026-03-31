"""
RatingAgent: Computes and updates department ratings based on resolution performance.
Rating Formula: (resolved_on_time / total_issues) * 100 - escalation_penalty
"""


class RatingAgent:
    """
    Agent responsible for:
    1. Computing department performance ratings
    2. Updating department records
    3. Returning dashboard-ready rating data
    """

    ESCALATION_PENALTY_PER = 20  # points deducted per escalation ratio

    def __init__(self):
        self.agent_name = "RatingAgent"

    def compute_all_ratings(self) -> list:
        """Recompute and return ratings for all departments."""
        from core.models import Department, Issue

        print(f"[{self.agent_name}] Computing ratings for all departments...")
        results = []

        departments = Department.objects.all()
        for dept in departments:
            rating_data = self._compute_department_rating(dept)
            results.append(rating_data)

        print(f"[{self.agent_name}] Computed {len(results)} department ratings")
        return results

    def compute_department_rating(self, department_code: str) -> dict:
        """Compute rating for a single department by code."""
        from core.models import Department
        try:
            dept = Department.objects.get(code=department_code)
            return self._compute_department_rating(dept)
        except Department.DoesNotExist:
            return {'error': f'Department {department_code} not found'}

    def _compute_department_rating(self, dept) -> dict:
        """Core rating computation logic."""
        from core.models import Issue

        total = Issue.objects.filter(department=dept).count()
        resolved = Issue.objects.filter(department=dept, status='resolved').count()
        escalated = Issue.objects.filter(department=dept, escalation_level__gt=0).count()
        pending = Issue.objects.filter(department=dept, status__in=['pending', 'sent', 'in_progress']).count()

        if total == 0:
            rating = 100.0
            grade = 'N/A'
        else:
            base_score = (resolved / total) * 100
            escalation_ratio = escalated / total
            penalty = escalation_ratio * self.ESCALATION_PENALTY_PER
            rating = max(0.0, round(base_score - penalty, 2))
            grade = self._grade(rating)

        # Update DB
        dept.total_issues = total
        dept.resolved_issues = resolved
        dept.escalated_issues = escalated
        dept.rating = rating
        dept.save()

        return {
            'department_id': dept.id,
            'department_name': dept.name,
            'department_code': dept.code,
            'total_issues': total,
            'resolved_issues': resolved,
            'pending_issues': pending,
            'escalated_issues': escalated,
            'rating': rating,
            'grade': grade,
            'agent': self.agent_name,
        }

    def _grade(self, rating: float) -> str:
        if rating >= 90:
            return 'A'
        elif rating >= 75:
            return 'B'
        elif rating >= 60:
            return 'C'
        elif rating >= 40:
            return 'D'
        else:
            return 'F'
