from django.db import models
from django.utils import timezone


class Department(models.Model):
    name             = models.CharField(max_length=100)
    code             = models.CharField(max_length=20, unique=True)
    email            = models.EmailField(default='dept@gov.in')
    total_issues     = models.IntegerField(default=0)
    resolved_issues  = models.IntegerField(default=0)
    escalated_issues = models.IntegerField(default=0)
    rating           = models.FloatField(default=100.0)

    def __str__(self):
        return self.name

    def update_rating(self):
        if self.total_issues == 0:
            self.rating = 100.0
        else:
            base    = (self.resolved_issues / self.total_issues) * 100
            penalty = (self.escalated_issues / self.total_issues) * 20
            self.rating = max(0.0, round(base - penalty, 2))
        self.save()


class Issue(models.Model):
    STATUS_CHOICES = [
        ('pending',     'Pending'),
        ('sent',        'Sent to Department'),
        ('in_progress', 'In Progress'),
        ('resolved',    'Resolved'),
        ('escalated',   'Escalated'),
    ]
    SEVERITY_CHOICES = [
        ('low',      'Low'),
        ('medium',   'Medium'),
        ('high',     'High'),
        ('critical', 'Critical'),
    ]

    # Use FileField so Pillow is NOT required
    image          = models.FileField(upload_to='issues/', null=True, blank=True)
    issue_type     = models.CharField(max_length=50)
    location       = models.CharField(max_length=255, default='Unknown Location')
    severity       = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='medium')
    description    = models.TextField()
    complaint_text = models.TextField(blank=True)
    status         = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    department     = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    escalation_level = models.IntegerField(default=0)
    confidence     = models.FloatField(default=0.0)
    created_at     = models.DateTimeField(default=timezone.now)
    last_updated   = models.DateTimeField(auto_now=True)
    deadline_hours = models.IntegerField(default=48)
    resolved_at    = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.issue_type} - {self.location} [{self.status}]"

    @property
    def is_overdue(self):
        if self.status == 'resolved':
            return False
        from datetime import timedelta
        return timezone.now() > (self.created_at + timedelta(hours=self.deadline_hours))

    @property
    def hours_since_creation(self):
        return (timezone.now() - self.created_at).total_seconds() / 3600


class EscalationLog(models.Model):
    issue          = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name='escalation_logs')
    level          = models.IntegerField()
    complaint_text = models.TextField()
    timestamp      = models.DateTimeField(default=timezone.now)
    reason         = models.CharField(max_length=255)

    def __str__(self):
        return f"Escalation L{self.level} for Issue #{self.issue.id}"
