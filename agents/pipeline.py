"""
Pipeline: Central orchestrator for AutoGov AI multi-agent system.
VisionAgent → ValidationAgent → ComplaintAgent → RoutingAgent → ToolAgent
"""
import os
import random

from agents.vision_agent     import VisionAgent
from agents.validation_agent import ValidationAgent
from agents.complaint_agent  import ComplaintAgent
from agents.routing_agent    import RoutingAgent
from agents.tool_agent       import ToolAgent

DUMMY_LOCATIONS = [
    "MG Road, Near City Mall, Ward 12",
    "Station Road, Opp. Railway Gate, Ward 5",
    "Gandhi Nagar, Block B, Sector 3",
    "Civil Lines, Near District Court",
    "Sadar Bazaar, Main Market Area, Ward 7",
    "Nehru Colony, Street 4, Block C",
    "Ring Road, Near Flyover Junction",
    "Old City, Char Minar Area, Ward 9",
]


class Pipeline:
    def __init__(self):
        self.vision_agent     = VisionAgent()
        self.validation_agent = ValidationAgent()
        self.complaint_agent  = ComplaintAgent()
        self.routing_agent    = RoutingAgent()
        self.tool_agent       = ToolAgent()

    # ------------------------------------------------------------------
    def run(self, image_path: str, raw_bytes: bytes = None,
            filename: str = '', location: str = None) -> dict:
        """
        Full pipeline for a new issue report.
        image_path : real filesystem path (for VisionAgent heuristics)
        raw_bytes  : original file bytes (saved directly to DB, no Pillow needed)
        filename   : original upload filename
        location   : user-supplied location string (auto-assigned if None)
        """
        print("\n" + "="*60)
        print("AUTOGOV AI PIPELINE STARTED")
        print("="*60)

        if not location:
            location = random.choice(DUMMY_LOCATIONS)

        fname = filename or os.path.basename(image_path)

        # ── STEP 1: Vision ────────────────────────────────────────────
        print("\n[Pipeline] STEP 1: Vision Detection")
        detection = self.vision_agent.analyze(image_path, fname)

        # ── STEP 2: Validation ────────────────────────────────────────
        print("\n[Pipeline] STEP 2: Validation")
        validation = self.validation_agent.validate(detection, location)

        if not validation['valid']:
            print(f"[Pipeline] REJECTED: {validation['reason']}")
            return {
                'success': False,
                'stage':   'validation',
                'reason':  validation['reason'],
                'detection': detection,
            }

        # ── STEP 3: Routing ───────────────────────────────────────────
        print("\n[Pipeline] STEP 3: Routing")
        routing = self.routing_agent.route(detection['issue_type'], escalation_level=0)

        # ── STEP 4: Complaint ─────────────────────────────────────────
        print("\n[Pipeline] STEP 4: Complaint Generation")
        complaint_data = {
            'issue_type': detection['issue_type'],
            'location':   location,
            'severity':   validation['severity'],
            'confidence': detection['confidence'],
            'issue_id':   'NEW',
        }
        complaint = self.complaint_agent.generate(complaint_data, escalation_level=0)

        # ── STEP 5: Save ──────────────────────────────────────────────
        print("\n[Pipeline] STEP 5: Saving Issue")
        issue = self.tool_agent.save_issue({
            'raw_bytes':    raw_bytes,
            'filename':     fname,
            'issue_type':   detection['issue_type'],
            'location':     location,
            'severity':     validation['severity'],
            'description':  (
                f"Detected {detection['issue_type'].replace('_',' ')} "
                f"with {detection['confidence']:.0%} confidence."
            ),
            'complaint_text': complaint['complaint_text'],
            'department':     routing.get('department'),
            'confidence':     detection['confidence'],
            'deadline_hours': validation['deadline_hours'],
        })

        print(f"\n{'='*60}")
        print(f"PIPELINE COMPLETE — Issue #{issue.id} created")
        print("="*60 + "\n")

        return {
            'success':          True,
            'issue_id':         issue.id,
            'issue_type':       detection['issue_type'],
            'location':         location,
            'severity':         validation['severity'],
            'confidence':       detection['confidence'],
            'department':       routing['department_name'],
            'department_code':  routing['department_code'],
            'complaint_text':   complaint['complaint_text'],
            'status':           issue.status,
            'is_duplicate':     validation.get('is_duplicate', False),
            'duplicate_issue_id': validation.get('duplicate_issue_id'),
            'agents_trace': {
                'vision':     detection.get('agent'),
                'validation': validation.get('agent'),
                'routing':    routing.get('agent'),
                'complaint':  complaint.get('agent'),
                'tool':       self.tool_agent.agent_name,
            },
        }

    # ------------------------------------------------------------------
    def send_complaint(self, issue_id: int) -> dict:
        try:
            from core.models import Issue
            issue = Issue.objects.get(id=issue_id)
            return self.tool_agent.send_complaint(issue)
        except Issue.DoesNotExist:
            return {'success': False, 'error': f'Issue #{issue_id} not found'}
