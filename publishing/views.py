"""
GARL Publishing Center Views
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone

from .models import Publication, Submission, Review, Revision, Book, Journal, PublicationType
from core.utils import paginate_queryset, log_action, track_activity
from core.decorators import publisher_required, reviewer_required
from notifications.models import send_notification


# ──────────────────────────────────────────────────────────────────────────────
# Publishing home
# ──────────────────────────────────────────────────────────────────────────────
def publishing_home(request):
    pub_types = PublicationType.objects.filter(is_active=True)
    journals  = Journal.objects.filter(is_active=True).order_by('title')[:10]
    recent    = Publication.objects.filter(status='published').order_by('-published_at')[:8]
    return render(request, 'publishing/home.html', {
        'pub_types': pub_types,
        'journals':  journals,
        'recent':    recent,
    })


# ──────────────────────────────────────────────────────────────────────────────
# Publication list
# ──────────────────────────────────────────────────────────────────────────────
def publication_list(request):
    pubs = Publication.objects.filter(status='published').select_related('created_by', 'pub_type')

    q       = request.GET.get('q', '')
    type_id = request.GET.get('type')
    journal = request.GET.get('journal')

    if q:
        pubs = pubs.filter(Q(title__icontains=q) | Q(abstract__icontains=q) | Q(keywords__icontains=q))
    if type_id:
        pubs = pubs.filter(pub_type_id=type_id)
    if journal:
        pubs = pubs.filter(journal_id=journal)

    pubs     = pubs.order_by('-published_at')
    page_obj = paginate_queryset(pubs, request, 15)
    pub_types = PublicationType.objects.filter(is_active=True)
    journals  = Journal.objects.filter(is_active=True)

    return render(request, 'publishing/publication_list.html', {
        'page_obj':  page_obj,
        'pub_types': pub_types,
        'journals':  journals,
        'q':         q,
    })


# ──────────────────────────────────────────────────────────────────────────────
# Publication detail
# ──────────────────────────────────────────────────────────────────────────────
def publication_detail(request, slug):
    pub = get_object_or_404(Publication, slug=slug, status='published')
    Publication.objects.filter(pk=pub.pk).update(view_count=pub.view_count + 1)
    track_activity(request.user, 'book', pub.pk, pub.title)
    authors = pub.publication_authors.all().order_by('order')

    # Payment context
    from payments.models import ContentPrice, AccessGrant
    pub_price  = None
    has_access = pub.is_open_access  # open access = always accessible
    try:
        pub_price = ContentPrice.objects.get(content_type='publication', object_id=pub.pk, is_active=True)
        if not has_access and pub_price.is_free:
            has_access = True
        if not has_access and request.user.is_authenticated:
            has_access = AccessGrant.objects.filter(
                buyer=request.user, content_type='publication', object_id=pub.pk
            ).exists()
    except ContentPrice.DoesNotExist:
        has_access = True  # no price configured → treat as free

    # Send access notification to publisher/author
    if has_access and pub.created_by and request.user.is_authenticated:
        from payments.emails import send_access_notification
        send_access_notification(
            content_owner = pub.created_by,
            content_title = pub.title,
            content_type  = pub.pub_type.name if pub.pub_type else 'Publication',
            accessor_name = request.user.get_full_name() or request.user.username,
        )

    return render(request, 'publishing/publication_detail.html', {
        'publication': pub,
        'authors':     authors,
        'pub_price':   pub_price,
        'has_access':  has_access,
    })


# ──────────────────────────────────────────────────────────────────────────────
# Submit publication
# ──────────────────────────────────────────────────────────────────────────────
@login_required
@publisher_required
def submit_publication(request):
    from .forms import PublicationSubmitForm
    if request.method == 'POST':
        form = PublicationSubmitForm(request.POST, request.FILES)
        if form.is_valid():
            pub = form.save(commit=False)
            pub.created_by  = request.user
            pub.status      = Publication.StatusChoice.SUBMITTED
            pub.submitted_at = timezone.now()
            pub.save()
            form.save_m2m()
            Submission.objects.create(publication=pub, submitted_by=request.user)
            log_action(request, 'create', Publication, pub.pk, pub.title, 'Publication submitted')
            messages.success(request, 'Publication submitted successfully.')
            return redirect('publishing:my_submissions')
    else:
        form = PublicationSubmitForm()
    return render(request, 'publishing/submit.html', {'form': form})


# ──────────────────────────────────────────────────────────────────────────────
# Author: my submissions
# ──────────────────────────────────────────────────────────────────────────────
@login_required
def my_submissions(request):
    pubs = Publication.objects.filter(created_by=request.user).order_by('-created_at')
    return render(request, 'publishing/my_submissions.html', {'publications': pubs})


# ──────────────────────────────────────────────────────────────────────────────
# Editor: manage submissions
# ──────────────────────────────────────────────────────────────────────────────
@login_required
def editor_dashboard(request):
    if not (request.user.is_editor() or request.user.is_any_admin()):
        messages.error(request, 'Editor access required.')
        return redirect('dashboard:home')

    pending = Submission.objects.filter(
        publication__status__in=['submitted', 'screening', 'under_review', 'revision_req', 'final_review']
    ).select_related('publication', 'submitted_by').order_by('-submitted_at')

    return render(request, 'publishing/editor_dashboard.html', {'submissions': pending})


@login_required
def approve_publication(request, pk):
    """Editor/Admin approves and publishes."""
    if not (request.user.is_editor() or request.user.is_any_admin()):
        messages.error(request, 'Permission denied.')
        return redirect('dashboard:home')

    pub = get_object_or_404(Publication, pk=pk)
    pub.status       = Publication.StatusChoice.PUBLISHED
    pub.published_at = timezone.now()
    pub.save(update_fields=['status', 'published_at'])

    log_action(request, 'approve', Publication, pub.pk, pub.title, 'Publication approved and published')

    if pub.created_by:
        send_notification(
            pub.created_by,
            'pub_approved',
            'Publication Approved',
            f'Your publication "{pub.title}" has been approved and published.',
            link=f'/publishing/publications/{pub.slug}/'
        )

    messages.success(request, f'"{pub.title}" published successfully.')
    return redirect('publishing:editor_dashboard')


@login_required
def reject_publication(request, pk):
    if not (request.user.is_editor() or request.user.is_any_admin()):
        messages.error(request, 'Permission denied.')
        return redirect('dashboard:home')

    pub = get_object_or_404(Publication, pk=pk)
    reason = request.POST.get('reason', '')
    pub.status = Publication.StatusChoice.REJECTED
    pub.rejection_reason = reason
    pub.save(update_fields=['status', 'rejection_reason'])

    log_action(request, 'reject', Publication, pub.pk, pub.title, 'Publication rejected')

    if pub.created_by:
        send_notification(
            pub.created_by,
            'pub_rejected',
            'Publication Decision',
            f'Your publication "{pub.title}" was not approved.',
            link='/publishing/my-submissions/'
        )

    messages.warning(request, f'"{pub.title}" rejected.')
    return redirect('publishing:editor_dashboard')


# ──────────────────────────────────────────────────────────────────────────────
# Reviewer: assigned reviews
# ──────────────────────────────────────────────────────────────────────────────
@login_required
@reviewer_required
def reviewer_dashboard(request):
    reviews = Review.objects.filter(
        reviewer=request.user, is_completed=False
    ).select_related('submission__publication').order_by('due_date')
    return render(request, 'publishing/reviewer_dashboard.html', {'reviews': reviews})


@login_required
@reviewer_required
def submit_review(request, pk):
    review = get_object_or_404(Review, pk=pk, reviewer=request.user)
    from .forms import ReviewForm
    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            r = form.save(commit=False)
            r.is_completed  = True
            r.submitted_at  = timezone.now()
            r.save()
            log_action(request, 'update', Review, r.pk, str(r), 'Review submitted')
            messages.success(request, 'Review submitted.')
            return redirect('publishing:reviewer_dashboard')
    else:
        form = ReviewForm(instance=review)
    return render(request, 'publishing/submit_review.html', {
        'form':   form,
        'review': review,
    })


# ──────────────────────────────────────────────────────────────────────────────
# Books
# ──────────────────────────────────────────────────────────────────────────────
def book_list(request):
    books = Book.objects.filter(is_published=True)
    q = request.GET.get('q', '')
    if q:
        books = books.filter(Q(title__icontains=q) | Q(description__icontains=q))
    books    = books.order_by('title')
    page_obj = paginate_queryset(books, request, 20)
    return render(request, 'publishing/book_list.html', {'page_obj': page_obj, 'q': q})


def book_detail(request, slug):
    book = get_object_or_404(Book, slug=slug, is_published=True)
    Book.objects.filter(pk=book.pk).update(view_count=book.view_count + 1)
    track_activity(request.user, 'book', book.pk, book.title)

    # Payment context
    from payments.models import ContentPrice, AccessGrant
    book_price = None
    has_access = book.is_free  # free books always accessible
    try:
        book_price = ContentPrice.objects.get(content_type='book', object_id=book.pk, is_active=True)
        if not has_access and request.user.is_authenticated:
            has_access = AccessGrant.objects.filter(
                buyer=request.user, content_type='book', object_id=book.pk
            ).exists()
    except ContentPrice.DoesNotExist:
        has_access = True  # no price set — treat as free

    # Send access notification if user has access and is viewing
    if has_access and book.added_by and request.user.is_authenticated:
        from payments.emails import send_access_notification
        send_access_notification(
            content_owner = book.added_by,
            content_title = book.title,
            content_type  = 'Book',
            accessor_name = request.user.get_full_name() or request.user.username,
        )

    return render(request, 'publishing/book_detail.html', {
        'book':       book,
        'book_price': book_price,
        'has_access': has_access,
    })


@login_required
def book_download(request, pk):
    book = get_object_or_404(Book, pk=pk, is_published=True)
    if not book.file:
        messages.error(request, 'No file available.')
        return redirect('publishing:book_detail', slug=book.slug)
    Book.objects.filter(pk=pk).update(download_count=book.download_count + 1)
    log_action(request, 'download', Book, book.pk, book.title, 'Book downloaded')
    from django.http import FileResponse
    return FileResponse(book.file.open(), as_attachment=True, filename=book.file.name.split('/')[-1])


# ──────────────────────────────────────────────────────────────────────────────
# Journals
# ──────────────────────────────────────────────────────────────────────────────
def journal_list(request):
    journals = Journal.objects.filter(is_active=True).order_by('title')
    q = request.GET.get('q', '')
    if q:
        journals = journals.filter(Q(title__icontains=q) | Q(description__icontains=q))
    page_obj = paginate_queryset(journals, request, 20)
    return render(request, 'publishing/journal_list.html', {'page_obj': page_obj, 'q': q})


def journal_detail(request, slug):
    journal = get_object_or_404(Journal, slug=slug, is_active=True)
    issues  = journal.issues.order_by('-year', '-volume', '-issue')
    return render(request, 'publishing/journal_detail.html', {
        'journal': journal,
        'issues':  issues,
    })


# ──────────────────────────────────────────────────────────────────────────────
# Catch-all slug redirect
# Handles old/bad links like /publishing/some-slug/ by finding the matching
# publication or book and redirecting to the correct canonical URL.
# ──────────────────────────────────────────────────────────────────────────────
def slug_redirect(request, slug):
    """
    Try to resolve a bare publishing slug to the correct content URL.
    Order: published Publication → Book → Journal → publishing home.
    """
    # 1. Try published publication
    try:
        pub = Publication.objects.get(slug=slug, status='published')
        return redirect('publishing:publication_detail', slug=pub.slug)
    except Publication.DoesNotExist:
        pass

    # 2. Try any publication regardless of status (author following their own link)
    try:
        pub = Publication.objects.get(slug=slug)
        return redirect('publishing:publication_detail', slug=pub.slug)
    except Publication.DoesNotExist:
        pass

    # 3. Try book
    try:
        book = Book.objects.get(slug=slug, is_published=True)
        return redirect('publishing:book_detail', slug=book.slug)
    except Book.DoesNotExist:
        pass

    # 4. Try journal
    try:
        journal = Journal.objects.get(slug=slug, is_active=True)
        return redirect('publishing:journal_detail', slug=journal.slug)
    except Journal.DoesNotExist:
        pass

    # 5. Fallback: go to publications list with a search
    messages.warning(request, f'The resource "{slug}" was not found. Showing all publications.')
    return redirect(f'/publishing/publications/?q={slug}')
