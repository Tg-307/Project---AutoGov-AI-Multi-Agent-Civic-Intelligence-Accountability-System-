from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from .models import Issue, Department, EscalationLog
from .serializers import IssueSerializer, DepartmentSerializer


class UploadIssueView(APIView):
    """POST /api/upload/ — Accept image, run full pipeline, return result."""
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        import os, traceback
        from django.core.files.storage import default_storage
        from django.core.files.base import ContentFile

        image_file = request.FILES.get('image')
        location   = request.data.get('location', '').strip()

        if not image_file:
            return Response({'error': 'No image provided'}, status=400)

        # 1. Read raw bytes once
        raw_bytes = image_file.read()
        filename  = image_file.name or 'upload.jpg'

        # 2. Save to /media/tmp/ so VisionAgent has a real path
        tmp_rel  = f'tmp/{filename}'
        tmp_path = default_storage.path(
            default_storage.save(tmp_rel, ContentFile(raw_bytes))
        )

        try:
            from agents.pipeline import Pipeline
            pipeline = Pipeline()
            result = pipeline.run(
                image_path   = tmp_path,
                raw_bytes    = raw_bytes,
                filename     = filename,
                location     = location or None,
            )
        except Exception as exc:
            traceback.print_exc()
            return Response({'error': str(exc)}, status=500)
        finally:
            try:
                os.remove(tmp_path)
            except Exception:
                pass

        if result.get('success'):
            return Response(result, status=201)
        return Response(result, status=422)


class SendComplaintView(APIView):
    """POST /api/send/<issue_id>/"""

    def post(self, request, issue_id):
        try:
            from agents.pipeline import Pipeline
            result = Pipeline().send_complaint(issue_id)
            code = 200 if (result.get('sent') or result.get('success')) else 404
            return Response(result, status=code)
        except Exception as exc:
            return Response({'error': str(exc)}, status=500)


class IssueListView(APIView):
    """GET /api/issues/"""

    def get(self, request):
        issues = Issue.objects.select_related('department').prefetch_related('escalation_logs').order_by('-created_at')
        return Response({'count': issues.count(), 'issues': IssueSerializer(issues, many=True).data})


class IssueDetailView(APIView):
    """GET /api/issues/<id>/"""

    def get(self, request, issue_id):
        try:
            issue = Issue.objects.prefetch_related('escalation_logs').get(id=issue_id)
            return Response(IssueSerializer(issue).data)
        except Issue.DoesNotExist:
            return Response({'error': 'Issue not found'}, status=404)


class ResolveIssueView(APIView):
    """POST /api/resolve/<issue_id>/"""

    def post(self, request, issue_id):
        from agents.tool_agent import ToolAgent
        result = ToolAgent().resolve_issue(issue_id)
        return Response(result, status=200 if result.get('success') else 404)


class EscalateView(APIView):
    """POST /api/escalate/ or GET /api/escalate/?issue_id=X"""
    parser_classes = [JSONParser, FormParser]

    def post(self, request):
        from agents.escalation_agent import EscalationAgent
        simulate_hours = request.data.get('simulate_hours')
        if simulate_hours is not None:
            simulate_hours = float(simulate_hours)
        agent = EscalationAgent()
        ids   = agent.check_and_escalate(simulate_hours=simulate_hours)
        issues = Issue.objects.filter(id__in=ids)
        return Response({
            'escalated_count':    len(ids),
            'escalated_issue_ids': ids,
            'issues': IssueSerializer(issues, many=True).data,
        })

    def get(self, request):
        from agents.escalation_agent import EscalationAgent
        issue_id = request.query_params.get('issue_id')
        if not issue_id:
            return Response({'error': 'Provide issue_id'}, status=400)
        try:
            issue  = Issue.objects.get(id=issue_id)
            result = EscalationAgent().escalate_issue(issue)
            return Response({'escalated': result, 'issue': IssueSerializer(issue).data})
        except Issue.DoesNotExist:
            return Response({'error': 'Issue not found'}, status=404)


class RatingsView(APIView):
    """GET /api/ratings/"""

    def get(self, request):
        from agents.rating_agent import RatingAgent
        ratings = RatingAgent().compute_all_ratings()
        return Response({'departments': ratings, 'count': len(ratings)})


class DashboardView(APIView):
    """GET /api/dashboard/"""

    def get(self, request):
        from django.db.models import Count
        total      = Issue.objects.count()
        by_status  = dict(Issue.objects.values_list('status').annotate(c=Count('id')))
        by_type    = dict(Issue.objects.values_list('issue_type').annotate(c=Count('id')))
        by_severity= dict(Issue.objects.values_list('severity').annotate(c=Count('id')))
        escalated  = Issue.objects.filter(escalation_level__gt=0).count()
        overdue    = sum(
            1 for i in Issue.objects.filter(status__in=['pending','sent','in_progress'])
            if i.is_overdue
        )
        return Response({
            'total_issues':    total,
            'by_status':       by_status,
            'by_type':         by_type,
            'by_severity':     by_severity,
            'escalated_issues': escalated,
            'overdue_issues':  overdue,
        })
