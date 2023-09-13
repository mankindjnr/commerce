# mpesa daraja api
## ===================================================
setup your django application

__Next, head over to developer.safaricom.co.ke  website and signup/login to your developer account__

__Create an app and generate your app keys.__

- Go to _MY APPS 
- CREATE NEW APP
- GIVE YOUR APP A NAME
- SELECT ALL THE PRODUCTS
- CLICK ON CREATE APP

__You will get a consumer key and a consumer secret key__

__Copy the keys and paste them in your .env file__

## --------------------------------------------------
## Access Token
To use the daraja api, according to the docs, you'll need to have an access token.

The following function will help you get the access token.
inside a file called __generateAccessToken.py__, add the following code
```python
import requests
from django.http import JsonResponse

def get_access_token(request):
    consumer_key = "B2JNQ0jXldRaVNrSNf7PIhZCw8u6DUAE"  
    consumer_secret = "vmDhsm56BY5Afqva"  
    access_token_url = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
    headers = {'Content-Type': 'application/json'}
    auth = (consumer_key, consumer_secret)
    try:
        response = requests.get(access_token_url, headers=headers, auth=auth)
        response.raise_for_status() 
        result = response.json()
        access_token = result['access_token']
        return JsonResponse({'access_token': access_token})
    except requests.exceptions.RequestException as e:
        return JsonResponse({'error': str(e)})
```
Remember to pass your own credentials of consumer_key and consumer_secret to the function.

inside your views.py file, add the following code
```python
from .generateAccessToken import get_access_token
```
and now

inside your __urls.py__ file, add it to your urls
```python
urlpatterns = [
    path('get_access_token/', get_access_token, name='get_access_token'),
]
```

you can now run the server and go to the url http://127.0.0.1:8000/get_access_token/ to see the access token in your browser

## --------------------------------------------------
## STK PUSH
stk push is registered under the API of M-Pesa Express
You can trigger the stk push to the user allowing them to input their mpesa pin and complete the transaction.

__stkpush.py__

with the stk push, you'll need to pass parameters to the api.
To get them, go to API's tab on developer portal click on the simulate button of mpesa express.

on the next page, click the simulator dialog box and choose your app from the dropdown list.

## --------------------------------------------------
# query
You can use the request CheckOutRequestId to check the status of a transaction.