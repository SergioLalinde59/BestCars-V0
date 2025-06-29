# Uncomment the imports below before you add the function code
import requests
import os
from dotenv import load_dotenv

load_dotenv()

backend_url = os.getenv(
    'backend_url', default="http://localhost:3030")
sentiment_analyzer_url = os.getenv(
    'sentiment_analyzer_url',
    default="http://localhost:5050/")

# def get_request(endpoint, **kwargs):
def get_request(endpoint, **kwargs):
    params = ""
    if(kwargs):
        for key,value in kwargs.items():
            params=params+key+"="+value+"&"

    request_url = backend_url+endpoint+"?"+params
    print("restapis.py - get_request from {} ".format(request_url))
    try:
        # Call get method of requests library with URL and parameters
        response = requests.get(request_url)
        return response.json()
    except:
        # If any error occurs
        print("restapis.py - get_request Network exception occurred")# Add code for get requests to back end


def analyze_review_sentiments(text):
    request_url = sentiment_analyzer_url+"analyze/"+text
    print("restapis.py - analyze_review_sentiments GET from {} ".format(request_url))
    try:
        # Call get method of requests library with URL and parameters
        response = requests.get(request_url)
        print("restapis.py - analyze_review_sentiments response.json(): {}".format(response.json()))

        return response.json()
    except:
        # If any error occurs
        print("restapis.py - analyze_review_sentiments Network exception occurred")
        return {"sentiment": "neutral"}

def post_review(data_dict):
    request_url = backend_url+"/insert_review"
    try:
        response = requests.post(request_url,json=data_dict)
        print("post_review response.json(): {}".format(response.json()))
        return response.json()
    except:
        print("Network exception occurred")
        return None