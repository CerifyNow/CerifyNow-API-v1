from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def handler404(request, exception):
    """Custom 404 handler"""
    return JsonResponse({
        'error': 'Sahifa topilmadi',
        'status_code': 404,
        'message': 'So\'ralgan resurs mavjud emas'
    }, status=404)

@csrf_exempt
def handler500(request):
    """Custom 500 handler"""
    return JsonResponse({
        'error': 'Server xatosi',
        'status_code': 500,
        'message': 'Ichki server xatosi yuz berdi'
    }, status=500)
