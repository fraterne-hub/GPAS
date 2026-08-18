"""
GARL AI Support Views
"""

import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.utils import timezone

from .models import AIChatSession, AIChatMessage, AIChatFeedback
from .engine import ask_garl_ai


def ai_chat_page(request):
    """Full-page AI chat interface."""
    session     = AIChatSession.get_or_create_for_request(request)
    history     = session.messages.order_by('timestamp')[:50]

    # Suggested starter questions
    suggestions = [
        "How do I submit a research paper?",
        "What courses are available on GARL?",
        "How does the peer review process work?",
        "How do I register on GARL?",
        "What health science resources are available?",
        "How do I find upcoming events?",
        "Can I get a certificate from GARL courses?",
        "How do I contact support?",
    ]

    return render(request, 'ai_support/chat.html', {
        'session':     session,
        'history':     history,
        'suggestions': suggestions,
    })


@require_POST
def ai_chat_send(request):
    """AJAX endpoint — receive a message, return AI answer as JSON."""
    try:
        data     = json.loads(request.body)
        question = data.get('message', '').strip()
    except (json.JSONDecodeError, KeyError):
        return JsonResponse({'error': 'Invalid request'}, status=400)

    if not question:
        return JsonResponse({'error': 'Empty message'}, status=400)

    if len(question) > 1000:
        return JsonResponse({'error': 'Message too long (max 1000 characters).'}, status=400)

    # Get or create chat session
    session = AIChatSession.get_or_create_for_request(request)

    # Save user message
    AIChatMessage.objects.create(
        session = session,
        role    = AIChatMessage.ROLE_USER,
        content = question,
    )

    # Get AI answer
    result = ask_garl_ai(question)

    # Save assistant message
    assistant_msg = AIChatMessage.objects.create(
        session    = session,
        role       = AIChatMessage.ROLE_ASSISTANT,
        content    = result['answer_text'],
        sources    = result['sources'],
        confidence = result['confidence'],
        intents    = result['intents'],
        enhanced   = result['enhanced'],
    )

    # Update session counter
    AIChatSession.objects.filter(pk=session.pk).update(
        message_count=session.message_count + 2
    )

    return JsonResponse({
        'message_id': assistant_msg.pk,
        'answer':     result['answer_text'],
        'sources':    result['sources'],
        'confidence': result['confidence'],
        'intents':    result['intents'],
        'enhanced':   result['enhanced'],
    })


@require_POST
def ai_chat_feedback(request, message_id):
    """AJAX endpoint — save thumbs up/down feedback."""
    try:
        msg  = AIChatMessage.objects.get(pk=message_id, role=AIChatMessage.ROLE_ASSISTANT)
        data = json.loads(request.body)
        rating  = data.get('rating', '')
        comment = data.get('comment', '')

        if rating not in ('helpful', 'unhelpful'):
            return JsonResponse({'error': 'Invalid rating'}, status=400)

        AIChatFeedback.objects.update_or_create(
            message=msg,
            defaults={'rating': rating, 'comment': comment}
        )
        return JsonResponse({'status': 'ok'})
    except AIChatMessage.DoesNotExist:
        return JsonResponse({'error': 'Message not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_GET
def ai_chat_history(request):
    """AJAX endpoint — return last N messages for a session."""
    session  = AIChatSession.get_or_create_for_request(request)
    messages = session.messages.order_by('-timestamp')[:20]
    data = [
        {
            'id':         m.pk,
            'role':       m.role,
            'content':    m.content,
            'sources':    m.sources or [],
            'confidence': m.confidence,
            'timestamp':  m.timestamp.isoformat(),
        }
        for m in reversed(list(messages))
    ]
    return JsonResponse({'messages': data})


@require_POST
def ai_chat_clear(request):
    """Clear the current chat session history."""
    session = AIChatSession.get_or_create_for_request(request)
    session.messages.all().delete()
    AIChatSession.objects.filter(pk=session.pk).update(message_count=0)
    return JsonResponse({'status': 'cleared'})
