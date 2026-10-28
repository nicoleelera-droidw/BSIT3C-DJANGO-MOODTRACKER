from django.db import migrations

EMOTIONS = [
    ('Happy', '😊', 'positive', 'A light, cheerful mood.'),
    ('Joyful', '😄', 'positive', 'Brimming with good energy.'),
    ('Excited', '🤩', 'positive', 'Looking forward to something.'),
    ('Loved', '🥰', 'positive', 'Feeling cared for and connected.'),
    ('Blessed', '😇', 'positive', 'Grateful for what you have.'),
    ('Grateful', '🙏', 'positive', 'Appreciating someone or something.'),
    ('Energetic', '⚡', 'positive', 'Full of drive and momentum.'),
    ('Focused', '🎯', 'positive', 'Clear and locked in.'),
    ('Motivated', '💪', 'positive', 'Ready to take on the day.'),
    ('Peaceful', '🕊️', 'positive', 'A quiet, settled calm.'),
    ('Relieved', '😮‍💨', 'neutral', 'Tension easing after something passes.'),
    ('Empty', '😶', 'neutral', 'Feeling hollow or numb.'),
    ('Thoughtful', '🤔', 'neutral', 'Turning something over in your mind.'),
    ('Confused', '😕', 'neutral', 'Unsure of what is going on.'),
    ('Bored', '🥱', 'neutral', 'Restless and unengaged.'),
    ('Stressed', '😫', 'negative', 'Carrying too much pressure.'),
    ('Frustrated', '😤', 'negative', 'Blocked and simmering.'),
    ('Disappointed', '😞', 'negative', 'Let down by how things turned out.'),
    ('Annoyed', '😒', 'negative', 'Mildly irritated.'),
    ('Embarrassed', '😳', 'negative', 'Self-conscious and exposed.'),
]


def expand_emotions(apps, schema_editor):
    Emotion = apps.get_model('emotion', 'Emotion')
    for name, emoji, tone, description in EMOTIONS:
        Emotion.objects.get_or_create(
            name=name,
            defaults={'emoji': emoji, 'tone': tone, 'description': description},
        )


def shrink_emotions(apps, schema_editor):
    Emotion = apps.get_model('emotion', 'Emotion')
    Emotion.objects.filter(name__in=[name for name, *_ in EMOTIONS]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('emotion', '0002_seed_emotions'),
    ]

    operations = [
        migrations.RunPython(expand_emotions, shrink_emotions),
    ]
