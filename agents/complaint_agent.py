"""
ComplaintAgent: Generates human-readable complaint text.
Escalation level determines tone severity of the complaint.
"""
from datetime import datetime


TEMPLATES = {
    'pothole': {
        0: (
            "Subject: Complaint Regarding Dangerous Pothole\n\n"
            "Respected Sir/Madam,\n\n"
            "I am writing to bring to your urgent attention a severe pothole located at {location}. "
            "This road defect poses a significant hazard to motorists and pedestrians alike. "
            "The issue was detected with {confidence:.0%} confidence and has been classified as {severity} severity.\n\n"
            "Immediate repair is requested to prevent accidents and vehicle damage.\n\n"
            "Issue Reference ID: #{issue_id}\n"
            "Reported On: {date}\n\n"
            "Yours sincerely,\nAutoGov AI Civic System"
        ),
        1: (
            "Subject: ESCALATION LEVEL 1 — Unresolved Pothole Complaint\n\n"
            "Respected Sir/Madam,\n\n"
            "This is a FIRST ESCALATION notice. Despite our earlier complaint (Issue #{issue_id}) "
            "regarding a dangerous pothole at {location}, no action has been taken within the stipulated deadline.\n\n"
            "The issue severity has been upgraded to: {severity}.\n"
            "Continued inaction may result in legal and administrative consequences.\n\n"
            "Reported On: {date}\nEscalation Level: 1\n\nAutoGov AI Civic System"
        ),
        2: (
            "Subject: ⚠️ ESCALATION LEVEL 2 — URGENT: Pothole Causing Public Hazard\n\n"
            "This is a SECOND ESCALATION. Issue #{issue_id} at {location} remains UNRESOLVED. "
            "This constitutes a failure of civic duty. The severity is now {severity}. "
            "We demand immediate resolution within 6 hours or this matter will be forwarded to the District Magistrate.\n\n"
            "AutoGov AI Civic System | {date}"
        ),
        3: (
            "Subject: 🚨 FINAL ESCALATION — District Magistrate Notification Required\n\n"
            "Issue #{issue_id} at {location} has reached CRITICAL ESCALATION LEVEL 3. "
            "This has been reported {escalation_level} times without resolution. "
            "Severity: {severity}. This case is being forwarded to the District Magistrate and "
            "State Municipal Commissioner for immediate intervention.\n\nAutoGov AI | {date}"
        ),
    },
    'garbage': {
        0: (
            "Subject: Complaint — Unsanitary Garbage Accumulation\n\n"
            "Respected Sir/Madam,\n\n"
            "I wish to report an unsanitary garbage accumulation at {location}. "
            "This poses serious health risks to local residents including risk of disease spread. "
            "Severity: {severity}. Detection Confidence: {confidence:.0%}.\n\n"
            "Prompt sanitation action is requested.\n\n"
            "Issue ID: #{issue_id} | Reported: {date}\n\nAutoGov AI Civic System"
        ),
        1: (
            "Subject: ESCALATION 1 — Garbage Complaint Unresolved\n\n"
            "Issue #{issue_id} at {location} remains unaddressed. "
            "Garbage accumulation continues to create health hazards. Severity upgraded to {severity}.\n"
            "Immediate sanitation drive is demanded.\n\nAutoGov AI | {date}"
        ),
        2: (
            "Subject: ⚠️ ESCALATION 2 — Health Hazard Unresolved\n\n"
            "Issue #{issue_id}: Garbage at {location} is now a CRITICAL HEALTH HAZARD. "
            "Two prior complaints ignored. Severity: {severity}. Resolution required in 4 hours.\n\nAutoGov AI | {date}"
        ),
        3: (
            "Subject: 🚨 FINAL ESCALATION — Health Emergency Notification\n\n"
            "Issue #{issue_id} at {location} — LEVEL 3 ESCALATION. "
            "Garbage issue unresolved across {escalation_level} escalations. "
            "Forwarding to Chief Medical Officer and District Health Department.\n\nAutoGov AI | {date}"
        ),
    },
}

GENERIC_TEMPLATE = {
    0: (
        "Subject: Civic Issue Complaint — {issue_type}\n\n"
        "A civic issue of type '{issue_type}' has been detected at {location}. "
        "Severity: {severity}. Confidence: {confidence:.0%}.\n\n"
        "Issue ID: #{issue_id} | Date: {date}\n\nAutoGov AI"
    ),
    1: (
        "Subject: ESCALATION 1 — {issue_type} Unresolved\n\n"
        "Issue #{issue_id} at {location} remains unresolved. Severity: {severity}.\n\nAutoGov AI | {date}"
    ),
    2: (
        "Subject: ⚠️ ESCALATION 2 — {issue_type} Critical\n\n"
        "Issue #{issue_id}: {issue_type} at {location} is CRITICAL. "
        "Severity: {severity}. Immediate action required.\n\nAutoGov AI | {date}"
    ),
    3: (
        "Subject: 🚨 FINAL ESCALATION — {issue_type} District Level\n\n"
        "Issue #{issue_id} escalated {escalation_level} times. Forwarding to higher authority.\n\nAutoGov AI | {date}"
    ),
}


class ComplaintAgent:
    """
    Agent responsible for generating structured complaint text.
    Escalation level determines the tone and urgency.
    """

    def __init__(self):
        self.agent_name = "ComplaintAgent"

    def generate(self, issue_data: dict, escalation_level: int = 0) -> dict:
        """
        Generate complaint text based on issue details and escalation level.
        Returns: {complaint_text, subject}
        """
        print(f"[{self.agent_name}] Generating complaint (escalation={escalation_level})")

        issue_type = issue_data.get('issue_type', 'unknown')
        templates = TEMPLATES.get(issue_type, GENERIC_TEMPLATE)
        level = min(escalation_level, 3)
        template = templates.get(level, templates[0])

        params = {
            'issue_type': issue_type.replace('_', ' ').title(),
            'location': issue_data.get('location', 'Unknown Location'),
            'severity': issue_data.get('severity', 'medium').upper(),
            'confidence': issue_data.get('confidence', 0.75),
            'issue_id': issue_data.get('issue_id', 'N/A'),
            'date': datetime.now().strftime('%d %B %Y, %I:%M %p'),
            'escalation_level': escalation_level,
        }

        complaint_text = template.format(**params)
        subject = complaint_text.split('\n')[0].replace('Subject: ', '')

        result = {
            'complaint_text': complaint_text,
            'subject': subject,
            'escalation_level': escalation_level,
            'agent': self.agent_name,
        }

        print(f"[{self.agent_name}] Complaint generated ({len(complaint_text)} chars)")
        return result
