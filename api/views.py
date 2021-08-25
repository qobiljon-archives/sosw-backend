from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods


@csrf_exempt
@require_http_methods(['POST', 'GET'])
def handle_submit_data_api(request):
    return JsonResponse(data={'success': True})
