from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True
    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id',               models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name',             models.CharField(max_length=100)),
                ('code',             models.CharField(max_length=20, unique=True)),
                ('email',            models.EmailField(default='dept@gov.in', max_length=254)),
                ('total_issues',     models.IntegerField(default=0)),
                ('resolved_issues',  models.IntegerField(default=0)),
                ('escalated_issues', models.IntegerField(default=0)),
                ('rating',           models.FloatField(default=100.0)),
            ],
        ),
        migrations.CreateModel(
            name='Issue',
            fields=[
                ('id',               models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image',            models.FileField(blank=True, null=True, upload_to='issues/')),
                ('issue_type',       models.CharField(max_length=50)),
                ('location',         models.CharField(default='Unknown Location', max_length=255)),
                ('severity',         models.CharField(choices=[('low','Low'),('medium','Medium'),('high','High'),('critical','Critical')], default='medium', max_length=20)),
                ('description',      models.TextField()),
                ('complaint_text',   models.TextField(blank=True)),
                ('status',           models.CharField(choices=[('pending','Pending'),('sent','Sent to Department'),('in_progress','In Progress'),('resolved','Resolved'),('escalated','Escalated')], default='pending', max_length=20)),
                ('escalation_level', models.IntegerField(default=0)),
                ('confidence',       models.FloatField(default=0.0)),
                ('created_at',       models.DateTimeField(default=django.utils.timezone.now)),
                ('last_updated',     models.DateTimeField(auto_now=True)),
                ('deadline_hours',   models.IntegerField(default=48)),
                ('resolved_at',      models.DateTimeField(blank=True, null=True)),
                ('department',       models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.department')),
            ],
        ),
        migrations.CreateModel(
            name='EscalationLog',
            fields=[
                ('id',               models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('level',            models.IntegerField()),
                ('complaint_text',   models.TextField()),
                ('timestamp',        models.DateTimeField(default=django.utils.timezone.now)),
                ('reason',           models.CharField(max_length=255)),
                ('issue',            models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='escalation_logs', to='core.issue')),
            ],
        ),
    ]
