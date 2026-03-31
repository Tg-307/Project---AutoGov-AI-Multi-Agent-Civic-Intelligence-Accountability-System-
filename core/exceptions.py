from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import traceback


def json_exception_handler(exc, context):
    """
    Always return JSON from API endpoints — never Django HTML error pages.
    """
    # Call DRF's default handler first
    response = exception_handler(exc, context)

    if response is not None:
        return response

    # Unhandled exception — return JSON 500
    traceback.print_exc()
    return Response(
        {'error': str(exc), 'type': type(exc).__name__},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
