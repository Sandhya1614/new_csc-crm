from django.db import migrations, models
import django.db.models.deletion


def backfill(apps, schema_editor):
    CallLog = apps.get_model('leads', 'CallLog')
    LeadCapture = apps.get_model('leads', 'LeadCapture')

    for log in CallLog.objects.all():
        changed = False
        if log.call_outcome == 'Not Reachable':
            log.call_type = 'did_not_connect'
            log.duration = 0
            changed = True
        if log.lead_id is None and log.lead_name:
            matches = list(LeadCapture.objects.filter(lead_name__iexact=log.lead_name.strip())[:2])
            if len(matches) == 1:
                log.lead_id = matches[0].id
                changed = True
        if changed:
            log.save()


class Migration(migrations.Migration):

    dependencies = [
        ('leads', '0015_leadcapturetarget'),
    ]

    operations = [
        migrations.AddField(
            model_name='calllog',
            name='lead',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='calls', to='leads.leadcapture'),
        ),
        migrations.AddField(
            model_name='calllog',
            name='call_type',
            field=models.CharField(choices=[('outgoing', 'Outgoing'), ('answered', 'Answered'), ('did_not_connect', 'Did not connect')], default='outgoing', max_length=20),
        ),
        migrations.AddField(
            model_name='calllog',
            name='duration_seconds',
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.RunPython(backfill, migrations.RunPython.noop),
    ]
