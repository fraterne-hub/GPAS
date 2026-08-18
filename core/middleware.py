"""
GARL Core Middleware
"""


class AuditLogMiddleware:
    """
    Lightweight middleware — stores IP on request for use in views.
    Heavy audit logging is done explicitly in views, not here,
    to avoid logging every single page view.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            request.client_ip = x_forwarded_for.split(',')[0].strip()
        else:
            request.client_ip = request.META.get('REMOTE_ADDR', '')

        response = self.get_response(request)
        return response
