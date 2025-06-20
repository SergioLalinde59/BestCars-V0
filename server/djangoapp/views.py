# Uncomment the required imports before adding the code
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import logout
from django.contrib import messages
from datetime import datetime
from django.http import JsonResponse
from django.contrib.auth import login, authenticate
import logging
import json
from django.views.decorators.csrf import csrf_exempt
from .populate import initiate
from .models import CarMake, CarModel
from .restapis import get_request, analyze_review_sentiments, post_review

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.
def get_cars(request):
    print(f"djangoapp/views.py - get_cars path: {request.path}")
    # Check if the database is empty, if so, initiate it
    count = CarMake.objects.filter().count()
    print(count)
    if(count == 0):
        initiate()
    car_models = CarModel.objects.select_related('car_make')
    cars = []
    for car_model in car_models:
        cars.append({"CarModel": car_model.name, "CarMake": car_model.car_make.name})
    return JsonResponse({"CarModels":cars})
    
# Create a `login_request` view to handle sign in request
@csrf_exempt
def login_user(request):
    print(f"djangoapp/views.py - login_user path: {request.path}")
    # Solo procesar la autenticación para solicitudes POST
    if request.method == 'POST':
        try:
            # Get username and password from request.POST dictionary
            data = json.loads(request.body)
            username = data['userName']
            password = data['password']
            # Try to check if provide credential can be authenticated
            user = authenticate(username=username, password=password)
            data = {"userName": username}
            if user is not None:
                # If user is valid, call login method to login current user
                login(request, user)
                data = {"userName": username, "status": "Authenticated"}
            return JsonResponse(data)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)
        except KeyError:
            return JsonResponse({"error": "Missing username or password"}, status=400)
    # Para solicitudes GET, simplemente devolver un mensaje informativo
    return JsonResponse({"message": "Please use POST request for login"}, status=200)
    return JsonResponse(data)

# Create a `logout_request` view to handle sign out request
@csrf_exempt
def logout_request(request):
    print(f"djangoapp/views.py - logout_request path: {request.path}")
    logout(request)  # Termina la sesión del usuario
    data = {"userName": "", "status": "Logged out"}  # Devuelve el username vacío y un status
    return JsonResponse(data)

# Create a `registration` view to handle sign up request
@csrf_exempt
def registration(request):
    print(f"djangoapp/views.py - registration path: {request.path}")
    context = {}

    # Load JSON data from the request body
    data = json.loads(request.body)
    username = data['userName']
    password = data['password']
    first_name = data['firstName']
    last_name = data['lastName']
    email = data['email']
    username_exist = False
    email_exist = False
    try:
        # Check if user already exists
        User.objects.get(username=username)
        username_exist = True
    except:
        # If not, simply log this is a new user
        logger.debug("{} is new user".format(username))

    # If it is a new user
    if not username_exist:
        # Create user in auth_user table
        user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,password=password, email=email)
        # Login the user and redirect to list page
        login(request, user)
        data = {"userName":username,"status":"Authenticated"}
        return JsonResponse(data)
    else :
        data = {"userName":username,"error":"Already Registered"}
        return JsonResponse(data)
# ...

# # Update the `get_dealerships` view to render the index page with
# a list of dealerships
def get_dealerships(request, state="All"):
    print(f"djangoapp/views.py - get_dealerships state: {state}")
    if state == "All":
        endpoint = "/fetchDealers"
    else:
        endpoint = f"/fetchDealers/{state}"
    
    dealerships = get_request(endpoint)
    
    # Asegurar que dealerships es una lista (array)
    if dealerships is None:
        dealerships = []
    
    # Log para debug
    print(f"djangoapp/views.py - get_dealerships - No concesionarios = {len(dealerships)} ")
    
    # Formato consistente para la respuesta
    return JsonResponse({
        "status": 200,
        "dealers": dealerships
    }, safe=False)

# Get dealer details by ID
def get_dealer_details(request, dealer_id):
    print(f"djangoapp/views.py - get_dealer_details dealer_id: {dealer_id}")
    if(dealer_id):
        endpoint = "/fetchDealer/"+str(dealer_id)
        dealership = get_request(endpoint)
        return JsonResponse({"status":200,"dealer":dealership})
    else:
        return JsonResponse({"status":400,"message":"Bad Request"})

# Get dealer reviews and analyze sentiments
def get_dealer_reviews(request, dealer_id):
    print(f"djangoapp/views.py - get_dealer_reviews dealer_id: {dealer_id}")
    if dealer_id:
        endpoint = f"/fetchReviews/dealer/{dealer_id}"
        reviews = get_request(endpoint)
        print(f"djangoapp/views.py - get_dealer_reviews - No Reviews {len(reviews)}")
        for review_detail in reviews:
            response = analyze_review_sentiments(review_detail['review'])
            review_detail['sentiment'] = response['sentiment']
        return JsonResponse({"status": 200, "reviews": reviews})
    else:
        return JsonResponse({"status": 400, "message": "Bad Request"})

@csrf_exempt
def add_review(request):
    print(f"djangoapp/views.py - add_review path: {request.path}")
    if request.method == "POST":
        if request.user.is_anonymous == False:
            data = json.loads(request.body)
            try:
                response = post_review(data)
                return JsonResponse({"status": 200})
            except Exception as e:
                return JsonResponse({"status": 401, "message": "Error in posting review"})
        else:
            return JsonResponse({"status": 403, "message": "Unauthorized"})
    else:
        return JsonResponse({"status": 405, "message": "Method not allowed"})
