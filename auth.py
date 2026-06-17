import pyrebase
import streamlit as st

# TODO: Replace this dictionary with your Firebase project configuration
firebaseConfig = {
  "apiKey": "AIzaSyCImpNKrKjPzY06JUa3Ghz6xh8CH0_fuLg",
  "authDomain": "end-of-the-day-4ac42.firebaseapp.com",
  "projectId": "end-of-the-day-4ac42",
  "storageBucket": "end-of-the-day-4ac42.firebasestorage.app",
  "messagingSenderId": "294394699613",
  "appId": "1:294394699613:web:9da382785cd8e181e3d2b4",
  "databaseURL": ""
}

try:
    firebase = pyrebase.initialize_app(firebaseConfig)
    auth = firebase.auth()
    is_configured = firebaseConfig["apiKey"] != "YOUR_API_KEY"
except Exception as e:
    auth = None
    is_configured = False
    print(f"Firebase not configured properly: {e}")

def sign_in(email, password):
    if not is_configured:
        return False, "Firebase is not configured. Please add your credentials in auth.py."
    try:
        user = auth.sign_in_with_email_and_password(email, password)
        return True, user
    except Exception as e:
        import json
        try:
            error_json = e.args[1]
            error_data = json.loads(error_json)
            message = error_data['error']['message']
            return False, f"Error: {message.replace('_', ' ')}"
        except:
            return False, "Invalid Credentials or user does not exist."

def sign_up(email, password):
    if not is_configured:
        return False, "Firebase is not configured. Please add your credentials in auth.py."
    try:
        user = auth.create_user_with_email_and_password(email, password)
        return True, user
    except Exception as e:
        import json
        try:
            error_json = e.args[1]
            error_data = json.loads(error_json)
            message = error_data['error']['message']
            return False, f"Error: {message.replace('_', ' ')}"
        except:
            return False, "Email already exists or password is too weak."
