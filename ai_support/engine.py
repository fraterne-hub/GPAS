"""
GARL AI Support Engine
──────────────────────
Answers user questions by searching across GARL's own database content.
No external API required — works entirely on the site's data.

Architecture:
  1. Parse the user's question into intent + keywords.
  2. Run targeted DB queries across relevant modules.
  3. Score and rank results by relevance.
  4. Build a structured natural-language answer from the results.
  5. Optionally enhance the answer via an optional LLM API (OpenAI-compatible)
     if GARL_AI_API_KEY is set in .env — falls back gracefully if not.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional
from django.conf import settings


# ──────────────────────────────────────────────────────────────────────────────
# Intent detection helpers
# ──────────────────────────────────────────────────────────────────────────────

INTENTS = {
    'course':       r'\b(course|learn|lesson|enroll|certificate|tutorial|class|study)\b',
    'publication':  r'\b(publish|publication|journal|article|paper|submit|manuscript|book|thesis)\b',
    'research':     r'\b(research|paper|dataset|project|methodology|citation|reference)\b',
    'event':        r'\b(event|conference|seminar|workshop|webinar|register|upcoming)\b',
    'institution':  r'\b(university|institution|college|library|organization|institute)\b',
    'researcher':   r'\b(researcher|author|professor|lecturer|scientist|faculty)\b',
    'health':       r'\b(nursing|medicine|pharmacy|health|clinical|medical|midwifery|dentistry|biomedical)\b',
    'innovation':   r'\b(innovation|project|startup|prototype|patent|idea|invention)\b',
    'support':      r'\b(help|support|ticket|contact|problem|issue|faq|question|how to)\b',
    'account':      r'\b(account|login|register|password|profile|sign in|sign up)\b',
    'search':       r'\b(find|search|look|where|who|what|how many|list)\b',
}


def detect_intents(text: str) -> list[str]:
    text_lower = text.lower()
    found = []
    for intent, pattern in INTENTS.items():
        if re.search(pattern, text_lower):
            found.append(intent)
    return found or ['general']


def extract_keywords(text: str) -> list[str]:
    """Extract meaningful keywords from the user query."""
    # Remove common stop words
    stop = {
        'a','an','the','is','are','was','were','be','been','being',
        'have','has','had','do','does','did','will','would','could',
        'should','may','might','must','can','i','you','we','they',
        'he','she','it','this','that','these','those','in','on','at',
        'to','for','of','with','by','from','up','about','into','than',
        'more','also','just','how','what','where','when','who','which',
        'me','my','your','our','their','its','and','or','but','not',
        'no','yes','please','tell','show','give','want','need','like',
        'know','get','find','look','help','use','make','go','see',
    }
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
    return [w for w in words if w not in stop]


# ──────────────────────────────────────────────────────────────────────────────
# Data retrieval functions (each queries one GARL module)
# ──────────────────────────────────────────────────────────────────────────────

def search_faqs(keywords: list[str], limit: int = 5) -> list[dict]:
    from support.models import FAQ
    from django.db.models import Q
    if not keywords:
        return []
    q = Q()
    for kw in keywords:
        q |= Q(question__icontains=kw) | Q(answer__icontains=kw)
    results = FAQ.objects.filter(is_published=True).filter(q)[:limit]
    return [{'type': 'faq', 'title': r.question, 'body': r.answer, 'url': '/support/faq/'} for r in results]


def search_courses(keywords: list[str], limit: int = 5) -> list[dict]:
    from learning.models import Course
    from django.db.models import Q
    if not keywords:
        return []
    q = Q()
    for kw in keywords:
        q |= Q(title__icontains=kw) | Q(description__icontains=kw)
    results = Course.objects.filter(is_published=True).filter(q)[:limit]
    return [
        {
            'type': 'course',
            'title': r.title,
            'body': (r.description or '')[:200],
            'url': f'/learning/courses/{r.slug}/',
            'level': r.get_level_display(),
            'free': r.is_free,
            'cert': r.has_certificate,
        }
        for r in results
    ]


def search_publications(keywords: list[str], limit: int = 5) -> list[dict]:
    from publishing.models import Publication
    from django.db.models import Q
    if not keywords:
        return []
    q = Q()
    for kw in keywords:
        q |= Q(title__icontains=kw) | Q(abstract__icontains=kw) | Q(keywords__icontains=kw)
    results = Publication.objects.filter(status='published').filter(q)[:limit]
    return [
        {
            'type': 'publication',
            'title': r.title,
            'body': (r.abstract or '')[:200],
            'url': f'/publishing/publications/{r.slug}/',
            'pub_type': r.pub_type.name if r.pub_type else '',
        }
        for r in results
    ]


def search_research_papers(keywords: list[str], limit: int = 5) -> list[dict]:
    from research.models import ResearchPaper
    from django.db.models import Q
    if not keywords:
        return []
    q = Q()
    for kw in keywords:
        q |= Q(title__icontains=kw) | Q(abstract__icontains=kw) | Q(keywords__icontains=kw)
    results = ResearchPaper.objects.filter(status='published').filter(q)[:limit]
    return [
        {
            'type': 'paper',
            'title': r.title,
            'body': (r.abstract or '')[:200],
            'url': f'/research/papers/{r.slug}/',
            'year': r.publication_year,
            'journal': r.journal_name,
        }
        for r in results
    ]


def search_events(keywords: list[str], limit: int = 5) -> list[dict]:
    from events.models import Event
    from django.db.models import Q
    from django.utils import timezone
    if not keywords:
        return []
    q = Q()
    for kw in keywords:
        q |= Q(title__icontains=kw) | Q(description__icontains=kw)
    results = Event.objects.filter(
        is_published=True,
        start_date__gte=timezone.now()
    ).filter(q).order_by('start_date')[:limit]
    return [
        {
            'type': 'event',
            'title': r.title,
            'body': (r.description or '')[:150],
            'url': f'/events/{r.slug}/',
            'date': r.start_date.strftime('%B %d, %Y'),
            'location': r.location or 'Online',
            'free': r.is_free,
        }
        for r in results
    ]


def search_institutions(keywords: list[str], limit: int = 5) -> list[dict]:
    from community.models import Institution
    from django.db.models import Q
    if not keywords:
        return []
    q = Q()
    for kw in keywords:
        q |= Q(name__icontains=kw) | Q(description__icontains=kw) | Q(country__icontains=kw)
    results = Institution.objects.filter(is_published=True).filter(q)[:limit]
    return [
        {
            'type': 'institution',
            'title': r.name,
            'body': f'{r.city}, {r.country}' if r.city else r.country,
            'url': f'/community/institutions/{r.slug}/',
        }
        for r in results
    ]


def search_health_resources(keywords: list[str], limit: int = 5) -> list[dict]:
    from health_science.models import HealthResource
    from django.db.models import Q
    if not keywords:
        return []
    q = Q()
    for kw in keywords:
        q |= Q(title__icontains=kw) | Q(description__icontains=kw)
    results = HealthResource.objects.filter(is_published=True).filter(q)[:limit]
    return [
        {
            'type': 'health',
            'title': r.title,
            'body': (r.description or '')[:200],
            'url': f'/health/resources/{r.slug}/',
            'discipline': r.category.get_discipline_display() if r.category else '',
        }
        for r in results
    ]


def search_innovation_projects(keywords: list[str], limit: int = 5) -> list[dict]:
    from innovation.models import InnovationProject
    from django.db.models import Q
    if not keywords:
        return []
    q = Q()
    for kw in keywords:
        q |= Q(title__icontains=kw) | Q(description__icontains=kw) | Q(technologies__icontains=kw)
    results = InnovationProject.objects.filter(status='published').filter(q)[:limit]
    return [
        {
            'type': 'innovation',
            'title': r.title,
            'body': (r.description or '')[:200],
            'url': f'/innovation/projects/{r.slug}/',
            'project_type': r.get_project_type_display(),
        }
        for r in results
    ]


def search_books(keywords: list[str], limit: int = 5) -> list[dict]:
    from publishing.models import Book
    from django.db.models import Q
    if not keywords:
        return []
    q = Q()
    for kw in keywords:
        q |= Q(title__icontains=kw) | Q(description__icontains=kw)
    results = Book.objects.filter(is_published=True).filter(q)[:limit]
    return [
        {
            'type': 'book',
            'title': r.title,
            'body': f'{r.publisher}, {r.year}' if r.publisher else '',
            'url': f'/publishing/books/{r.slug}/',
            'free': r.is_free,
        }
        for r in results
    ]


# ──────────────────────────────────────────────────────────────────────────────
# Platform facts — hardcoded context about GARL itself
# ──────────────────────────────────────────────────────────────────────────────

GARL_FACTS = {
    'about': (
        "GARL (Global Academic Research Library) is a centralized academic ecosystem "
        "that connects students, researchers, institutions, and innovators worldwide. "
        "It provides research papers, books, journals, online courses, innovation projects, "
        "health science resources, and academic collaboration tools — all in one platform."
    ),
    'modules': (
        "GARL has the following main sections: Research Center, Publishing Center, "
        "Innovation Hub, Learning Center, Health Science Hub, Library, Community & Directory, "
        "Events, and Support Center."
    ),
    'publishing': (
        "To publish on GARL: go to Publishing Center → Submit Publication. "
        "Your submission goes through: Draft → Submission → Editorial Screening → "
        "Peer Review → Revision (if needed) → Approval → Publication. "
        "You can track your submission status in your dashboard under 'My Submissions'."
    ),
    'courses': (
        "GARL offers free online courses with certificates. Go to Learning Center → "
        "Browse Courses to find courses by category and level. "
        "After enrolling, your progress is tracked automatically. "
        "Completing a course with certificate earns you a digital certificate."
    ),
    'account': (
        "To register: click Register in the top navigation. Choose your role "
        "(Student, Researcher, Author, Instructor, or General User). "
        "To reset your password: go to Login → Forgot Password. "
        "You can update your profile, avatar and preferences from your Account settings."
    ),
    'support': (
        "For support: go to Support Center → Open Support Ticket. "
        "You can also browse FAQs for instant answers. "
        "Support ticket statuses: Open → Assigned → In Progress → Resolved → Closed. "
        "You can track all your tickets under Support → My Tickets."
    ),
    'health': (
        "The Health Science Hub provides educational resources for Nursing, Medicine, "
        "Midwifery, Pharmacy, Dentistry, Public Health, Biomedical Science, and Allied Health. "
        "All resources are for educational and research purposes only and are not a "
        "substitute for professional medical advice."
    ),
    'innovation': (
        "The Innovation Hub showcases student projects, prototypes, startups, patents, "
        "and research innovations. Submit your project via Innovation → Submit Project. "
        "Projects go through admin moderation before publication."
    ),
    'research': (
        "The Research Center provides research papers, projects, datasets, topics, and tools. "
        "You can search papers by keyword, category, and year. "
        "Researchers can submit papers, manage citations, and collaborate on projects."
    ),
}


def get_platform_facts(intents: list[str]) -> list[dict]:
    """Return relevant hardcoded GARL platform facts based on detected intents."""
    results = []
    mapping = {
        'account':     ['account'],
        'course':      ['courses'],
        'publication': ['publishing'],
        'research':    ['research'],
        'health':      ['health'],
        'innovation':  ['innovation'],
        'support':     ['support'],
        'general':     ['about', 'modules'],
    }
    seen = set()
    for intent in intents:
        for key in mapping.get(intent, ['about']):
            if key not in seen and key in GARL_FACTS:
                results.append({'type': 'fact', 'title': f'About GARL — {key.title()}', 'body': GARL_FACTS[key], 'url': '/'})
                seen.add(key)
    if not results:
        results.append({'type': 'fact', 'title': 'About GARL', 'body': GARL_FACTS['about'], 'url': '/'})
    return results


# ──────────────────────────────────────────────────────────────────────────────
# Response builder — turns retrieved results into a friendly answer
# ──────────────────────────────────────────────────────────────────────────────

def build_answer(question: str, results: list[dict], intents: list[str], facts: list[dict]) -> dict:
    """
    Build a structured answer dict:
      answer_text — the main prose response
      sources     — list of result dicts with title/url/type for display
      confidence  — 'high' | 'medium' | 'low'
    """
    sources = results[:6]

    # Decide confidence
    if len(results) >= 3:
        confidence = 'high'
    elif len(results) >= 1:
        confidence = 'medium'
    else:
        confidence = 'low'

    # Build the prose answer
    lines = []

    # Open with platform fact if useful
    if facts:
        lines.append(facts[0]['body'])

    # Add result summaries
    if results:
        type_groups: dict[str, list] = {}
        for r in results[:6]:
            type_groups.setdefault(r['type'], []).append(r)

        type_labels = {
            'faq':         'FAQ answers',
            'course':      'courses',
            'publication': 'publications',
            'paper':       'research papers',
            'event':       'upcoming events',
            'institution': 'institutions',
            'health':      'health resources',
            'innovation':  'innovation projects',
            'book':        'books',
        }

        lines.append("\n\nHere is what I found on GARL:")
        for rtype, items in type_groups.items():
            label = type_labels.get(rtype, 'results')
            lines.append(f"\n**{label.title()}** ({len(items)} found):")
            for item in items[:3]:
                snippet = item.get('body', '')[:120].strip()
                extra_parts = []
                if item.get('level'):     extra_parts.append(item['level'])
                if item.get('free'):      extra_parts.append('Free')
                if item.get('cert'):      extra_parts.append('Certificate')
                if item.get('year'):      extra_parts.append(str(item['year']))
                if item.get('date'):      extra_parts.append(item['date'])
                if item.get('discipline'):extra_parts.append(item['discipline'])
                extra = ' · '.join(extra_parts)
                lines.append(f"  • **{item['title']}**{(' — ' + extra) if extra else ''}")
                if snippet:
                    lines.append(f"    {snippet}{'...' if len(item.get('body','')) > 120 else ''}")
    else:
        lines.append(
            "\n\nI couldn't find specific content matching your question on GARL right now. "
            "You can try the global search, browse the relevant section, or open a support ticket "
            "and a human agent will assist you."
        )

    # Close with navigation hint
    nav_hints = {
        'course':      'Browse all courses at Learning Center.',
        'publication': 'See all publications at Publishing Center.',
        'research':    'Explore the Research Center for papers and projects.',
        'event':       'Find all upcoming events at the Events page.',
        'health':      'Browse all health resources at the Health Science Hub.',
        'innovation':  'Discover projects at the Innovation Hub.',
        'support':     'For further help, open a support ticket or browse FAQs.',
        'account':     'Manage your account from your Profile & Preferences.',
        'institution': 'Explore all institutions in Community & Directory.',
    }
    for intent in intents:
        if intent in nav_hints:
            lines.append(f"\n\n💡 {nav_hints[intent]}")
            break

    answer_text = ''.join(lines).strip()

    return {
        'answer_text': answer_text,
        'sources':     sources,
        'confidence':  confidence,
        'intents':     intents,
    }


# ──────────────────────────────────────────────────────────────────────────────
# Optional LLM enhancement (OpenAI-compatible API)
# ──────────────────────────────────────────────────────────────────────────────

def _try_llm_enhancement(question: str, context_text: str, raw_answer: str) -> Optional[str]:
    """
    If GARL_AI_API_KEY is set in settings/.env, send a prompt to the
    OpenAI-compatible API to produce a more conversational response.
    Returns None if not configured or if the call fails — the raw_answer
    is always used as the fallback.
    """
    api_key = getattr(settings, 'GARL_AI_API_KEY', None) or ''
    if not api_key or api_key == 'your-api-key-here':
        return None

    api_url  = getattr(settings, 'GARL_AI_API_URL', 'https://api.openai.com/v1/chat/completions')
    model    = getattr(settings, 'GARL_AI_MODEL', 'gpt-3.5-turbo')

    system_prompt = (
        "You are GARL's AI support assistant. GARL is the Global Academic Research Library — "
        "a platform for research, publishing, learning, innovation, health science, and collaboration. "
        "Answer the user's question ONLY using the provided context from GARL's database. "
        "Be helpful, concise, and friendly. If the context doesn't answer the question, "
        "say so and suggest they open a support ticket. "
        "Do not invent information not present in the context."
    )

    user_message = (
        f"Context from GARL:\n{context_text}\n\n"
        f"User question: {question}\n\n"
        f"Please provide a helpful, conversational answer."
    )

    try:
        import urllib.request, json as _json
        payload = _json.dumps({
            'model': model,
            'messages': [
                {'role': 'system', 'content': system_prompt},
                {'role': 'user',   'content': user_message},
            ],
            'max_tokens': 600,
            'temperature': 0.4,
        }).encode('utf-8')

        req = urllib.request.Request(
            api_url,
            data=payload,
            headers={
                'Content-Type':  'application/json',
                'Authorization': f'Bearer {api_key}',
            },
            method='POST'
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = _json.loads(resp.read())
            return data['choices'][0]['message']['content'].strip()
    except Exception:
        return None


# ──────────────────────────────────────────────────────────────────────────────
# Main entry point
# ──────────────────────────────────────────────────────────────────────────────

def ask_garl_ai(question: str) -> dict:
    """
    Main function. Given a user question string, return:
      {
        answer_text: str,
        sources:     list[dict],
        confidence:  'high'|'medium'|'low',
        intents:     list[str],
        enhanced:    bool,   # True if LLM was used
      }
    """
    question = question.strip()
    if not question:
        return {
            'answer_text': "Please type a question and I'll do my best to help!",
            'sources': [], 'confidence': 'low', 'intents': [], 'enhanced': False
        }

    intents  = detect_intents(question)
    keywords = extract_keywords(question)
    facts    = get_platform_facts(intents)

    # Run all relevant searches based on detected intents
    all_results: list[dict] = []

    intent_search_map = {
        'course':       search_courses,
        'publication':  search_publications,
        'research':     search_research_papers,
        'event':        search_events,
        'institution':  search_institutions,
        'health':       search_health_resources,
        'innovation':   search_innovation_projects,
        'support':      search_faqs,
        'account':      search_faqs,
        'search':       search_publications,  # broad search
    }

    called = set()
    for intent in intents:
        fn = intent_search_map.get(intent)
        if fn and fn not in called:
            all_results.extend(fn(keywords))
            called.add(fn)

    # Always search FAQs — they often have the most direct answers
    if search_faqs not in called:
        all_results.extend(search_faqs(keywords, limit=3))

    # For general/broad questions search everything
    if 'general' in intents or 'search' in intents:
        all_results.extend(search_courses(keywords, limit=2))
        all_results.extend(search_books(keywords, limit=2))
        all_results.extend(search_research_papers(keywords, limit=2))

    # Deduplicate by title
    seen_titles = set()
    unique_results = []
    for r in all_results:
        key = (r['type'], r['title'])
        if key not in seen_titles:
            seen_titles.add(key)
            unique_results.append(r)

    answer = build_answer(question, unique_results, intents, facts)

    # Try LLM enhancement — builds context from retrieved data
    context_parts = [f['body'] for f in facts[:2]]
    for r in unique_results[:5]:
        context_parts.append(f"{r['title']}: {r.get('body', '')[:200]}")
    context_text = '\n'.join(context_parts)

    enhanced_text = _try_llm_enhancement(question, context_text, answer['answer_text'])

    return {
        'answer_text': enhanced_text if enhanced_text else answer['answer_text'],
        'sources':     answer['sources'],
        'confidence':  answer['confidence'],
        'intents':     answer['intents'],
        'enhanced':    enhanced_text is not None,
    }
