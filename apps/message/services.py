from apps.message.models import Message


KEYWORD_MESSAGES = {
    'happy': [
        'It is good to honor moments of joy. Let this feeling remind you that brighter days can grow from small wins.',
        'Your happiness matters. Take a breath and enjoy what is going well for you today.',
    ],
    'joy': [
        'Hold on to this joyful moment and let it inspire the rest of your day.',
    ],
    'sad': [
        'It is okay to feel sad. Your emotions are valid, and this difficult moment will not last forever.',
        'Be gentle with yourself today. Small steps still count, even when your heart feels heavy.',
    ],
    'lonely': [
        'Feeling lonely can be painful, but you are still worthy of care, connection, and kindness.',
        'You are not less important because you feel alone right now. Your feelings deserve space and compassion.',
    ],
    'alone': [
        'Even in quiet moments, your feelings matter. Reach for rest, reflection, or someone you trust if you can.',
    ],
    'stress': [
        'Stress can make everything feel urgent. Pause, breathe slowly, and take the next step one task at a time.',
        'You do not have to solve everything at once. Focus on one manageable step and give yourself credit for it.',
    ],
    'stressed': [
        'You are carrying a lot right now. Slow down, breathe, and handle what you can in this moment.',
    ],
    'anxious': [
        'Anxiety can feel overwhelming, but you are here and you are trying. Ground yourself in one calm breath at a time.',
        'You do not need all the answers right now. Give yourself permission to move gently through this moment.',
    ],
    'anger': [
        'Anger is a signal, not your identity. Give yourself room to cool down before deciding what comes next.',
        'You can acknowledge this anger without letting it control your next step.',
    ],
    'angry': [
        'Take a pause before reacting. Space can help turn strong emotion into a steadier response.',
    ],
    'discouraged': [
        'Feeling discouraged does not erase your effort. Progress is still real, even when it feels slow.',
    ],
    'overwhelmed': [
        'When everything feels heavy, shrink the moment. One breath, one choice, one task is enough to start.',
    ],
    'tired': [
        'Rest is productive too. Listen to your body and give yourself permission to slow down.',
    ],
}

FALLBACK_MESSAGES = {
    'positive': 'You are doing well today. Keep holding on to what gives you peace, gratitude, or motivation.',
    'neutral': 'Your feelings matter. Taking time to reflect on them is already a meaningful step.',
    'supportive': 'This moment may be difficult, but you do not have to carry it without kindness toward yourself.',
}


def _pick_message(options, mood_entry):
    index = (mood_entry.pk or 0) % len(options)
    return options[index]


def build_support_message(mood_entry):
    category_name = (mood_entry.category.name if mood_entry.category else '').strip().lower()

    for keyword, options in KEYWORD_MESSAGES.items():
        if keyword in category_name:
            return _pick_message(options, mood_entry)

    if mood_entry.rating is not None:
        if mood_entry.rating >= 8:
            return FALLBACK_MESSAGES['positive']
        if mood_entry.rating <= 4:
            return FALLBACK_MESSAGES['supportive']

    return FALLBACK_MESSAGES['neutral']


def sync_message_for_entry(mood_entry):
    body = build_support_message(mood_entry)
    message = mood_entry.messages.order_by('id').first()

    if message is None:
        return Message.objects.create(mood_entry=mood_entry, body=body)

    if message.body != body:
        message.body = body
        message.save(update_fields=['body', 'updated_at'])

    return message
