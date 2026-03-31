"""
RoutingAgent: Maps detected issue type to responsible government department.
Also handles routing escalations to higher authorities.
"""


ROUTING_TABLE = {
    'pothole': {
        'department_code': 'PWD',
        'department_name': 'Public Works Department',
        'escalation_authority': 'COLLECTOR',
    },
    'garbage': {
        'department_code': 'MCD',
        'department_name': 'Municipal Corporation Department',
        'escalation_authority': 'COLLECTOR',
    },
    'broken_streetlight': {
        'department_code': 'ELEC',
        'department_name': 'Electricity & Street Lighting Department',
        'escalation_authority': 'COLLECTOR',
    },
    'open_drain': {
        'department_code': 'PHE',
        'department_name': 'Public Health Engineering Department',
        'escalation_authority': 'COLLECTOR',
    },
    'encroachment': {
        'department_code': 'REVENUE',
        'department_name': 'Revenue & Land Management Department',
        'escalation_authority': 'COLLECTOR',
    },
}

ESCALATION_AUTHORITY = {
    'department_code': 'COLLECTOR',
    'department_name': "District Collector's Office",
}


class RoutingAgent:
    """
    Agent responsible for routing issues to the correct department.
    On max escalation, routes to the District Collector.
    """

    def __init__(self):
        self.agent_name = "RoutingAgent"

    def route(self, issue_type: str, escalation_level: int = 0) -> dict:
        """
        Determine which department should handle this issue.
        Returns: {department_code, department_name, department_obj}
        """
        print(f"[{self.agent_name}] Routing issue_type={issue_type}, escalation={escalation_level}")

        if escalation_level >= 3:
            routing_info = ESCALATION_AUTHORITY
            print(f"[{self.agent_name}] Max escalation — routing to District Collector")
        else:
            routing_info = ROUTING_TABLE.get(issue_type, {
                'department_code': 'MCD',
                'department_name': 'Municipal Corporation Department',
                'escalation_authority': 'COLLECTOR',
            })

        department = self._get_or_create_department(
            routing_info['department_code'],
            routing_info['department_name'],
        )

        result = {
            'department_code': routing_info['department_code'],
            'department_name': routing_info['department_name'],
            'department': department,
            'agent': self.agent_name,
        }

        print(f"[{self.agent_name}] Routed to: {routing_info['department_name']}")
        return result

    def _get_or_create_department(self, code: str, name: str):
        """Get existing or create new department record."""
        try:
            from core.models import Department
            dept, created = Department.objects.get_or_create(
                code=code,
                defaults={'name': name, 'email': f"{code.lower()}@gov.in"}
            )
            return dept
        except Exception as e:
            print(f"[{self.agent_name}] Department DB error: {e}")
            return None
