from rest_framework import serializers
from .models import Issue, Department, EscalationLog


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'


class EscalationLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = EscalationLog
        fields = '__all__'


class IssueSerializer(serializers.ModelSerializer):
    department_name = serializers.SerializerMethodField()
    is_overdue = serializers.SerializerMethodField()
    escalation_logs = EscalationLogSerializer(many=True, read_only=True)

    class Meta:
        model = Issue
        fields = '__all__'

    def get_department_name(self, obj):
        return obj.department.name if obj.department else 'Unassigned'

    def get_is_overdue(self, obj):
        return obj.is_overdue
