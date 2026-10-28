from django.db import migrations

EMOTIONS = [
    ('Joy', '😊', 'positive', 'A bright, lifted feeling — things feel good right now.'),
    ('Gratitude', '🙏', 'positive', 'Appreciating something or someone in your life.'),
    ('Calm', '😌', 'positive', 'A settled, steady, peaceful state.'),
    ('Hopeful', '🌱', 'positive', 'Looking ahead with a sense of possibility.'),
    ('Content', '🙂', 'positive', 'Quietly satisfied with how things are.'),
    ('Neutral', '😐', 'neutral', 'Neither good nor bad — just steady.'),
    ('Tired', '😴', 'neutral', 'Low on energy and ready to rest.'),
    ('Anxious', '😰', 'negative', 'Uneasy and bracing for something uncertain.'),
    ('Sad', '😢', 'negative', 'A heavy, low feeling that asks for care.'),
    ('Angry', '😠', 'negative', 'Frustration or injustice that wants to be heard.'),
    ('Lonely', '😔', 'negative', 'Missing connection with others.'),
    ('Overwhelmed', '😵', 'negative', 'Too much at once, and hard to keep up.'),
]


def seed_emotions(apps, schema_editor):
    Emotion = apps.get_model('emotion', 'Emotion')
    for name, emoji, tone, description in EMOTIONS:
        Emotion.objects.get_or_create(
            name=name,
            defaults={'emoji': emoji, 'tone': tone, 'description': description},
        )


def unseed_emotions(apps, schema_editor):
    Emotion = apps.get_model('emotion', 'Emotion')
    Emotion.objects.filter(name__in=[name for name, *_ in EMOTIONS]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('emotion', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_emotions, unseed_emotions),
    ]
