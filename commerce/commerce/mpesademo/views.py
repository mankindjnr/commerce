from django.shortcuts import render
from django.http import JsonResponse
from .generateAccessToken import get_access_token
from .stkpush import initiate_stk_push
from .querystkstatus import query_stk_status

# Create your views here.
def index(request):
    return render(request, 'mpesademo/index.html')
