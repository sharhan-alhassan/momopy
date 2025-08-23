import uuid
import requests
import os
from mtn.base import Base
import mtn
from datetime import datetime, timedelta

class Sandbox(Base):
    """
    Sandbox class for interacting with MTN MoMo Sandbox API.
    This class replicates the exact working logic from the Jupyter notebook.
    """

    def __init__(self):
        # Initialize global variables like in the Jupyter notebook
        self.api_user = None
        self.api_key = None
        self.token = None
        self.token_expiry_time = None
        self.token_expired = False

    def create_api_user_sandbox(self, subscription_key):
        """
        Create an API user in the MTN MoMo Sandbox environment.
        Exact replica of the working Jupyter notebook function.
        """
        self.api_user = str(uuid.uuid4())
        print(f"Api_User: {self.api_user}")
        
        url = f"{mtn.BASE_API_URL}/v1_0/apiuser"
        headers = {
            "X-Reference-Id": self.api_user,
            "Ocp-Apim-Subscription-Key": subscription_key,
            "Content-Type": "application/json"
        }
        body = {
            "providerCallbackHost": os.getenv('CALLBACK_HOST', 'webhook.site')
        }
        
        try:
            resp = requests.request("post", url, json=body, headers=headers)
            if str(resp.status_code) == "201":
                print(f"HTTP Status Code: {resp.status_code}\n Api user Created: {self.api_user}")
                return True
            elif str(resp.status_code) == "401":
                print(f"{resp.status_code} {resp.text}")
                print("Ensure the subscription key is the primary")
                return False
            elif str(resp.status_code) == "400":
                print(f"{resp.status_code} {resp.text}")
                print("Ensure API User(X-Reference-Id) in the Headers is UUID Version 4")
                print("Ensure the Body contains the correct syntax \"providerCallbackHost\":\"Your CallBack URL HOST Eg \"webhook.site\"")
                return False
            else:
                print(f"{resp.status_code} {resp.text}")
                return False
        except TypeError:
            print("Body of the Request has to be Json Format")
            return False
        except Exception as e:
            print(f"Something Is Wrong: {e}")
            return False

    def create_api_key_sandbox(self, subscription_key):
        """
        Create an API key for the API user.
        Exact replica of the working Jupyter notebook function.
        """
        if not self.api_user:
            print("API_USER was not created, Please Run function create_api_user_sandbox() first")
            return False
            
        url = f"{mtn.BASE_API_URL}/v1_0/apiuser/{self.api_user}/apikey"
        headers = {
            "Ocp-Apim-Subscription-Key": subscription_key,
        }
        
        try:
            resp = requests.request("post", url, headers=headers)
            if str(resp.status_code) == "201":
                response = resp.json()
                self.api_key = response.get('apiKey')
                print(f"HTTP Status Code: {resp.status_code}\n Api User: {self.api_user} Api Key: {self.api_key}")
                return True
            elif str(resp.status_code) == "400":
                print(f"{resp.status_code} {resp.text} Validate the BaseURL \n And Ensure API_User is created, by calling the function create_api_user_sandbox()")
                return False
            elif str(resp.status_code) == "404":
                print(f"{resp.status_code} {resp.text} API_USER was not created, Please Run function create_api_user_sandbox()")
                return False
            else:
                print(f"{resp.status_code} {resp.text}")
                return False
        except TypeError:
            print("Body of the Request has to be Json Format or No Body")
            return False
        except Exception as e:
            print(f"Something Is Wrong: {e}")
            return False

    def get_token(self, subscription_key, product='collection'):
        """
        Generate token using the exact same logic as the working Jupyter notebook.
        """
        if not self.api_user or not self.api_key:
            print("API User and API Key must be created first")
            return None
            
        endpoint = f"{mtn.BASE_API_URL}/{product}/token/"
        headers = {
            "Ocp-Apim-Subscription-Key": subscription_key,
        }
        
        try:
            # Use the exact same approach as the working Jupyter notebook
            resp = requests.request("post", endpoint, auth=(self.api_user, self.api_key), headers=headers)
            response = resp.json()
            
            if str(resp.status_code) == "200":
                self.token = response.get('access_token')
                token_expiry = response.get('expires_in')
                self.token_expiry_time = datetime.now() + timedelta(seconds=int(token_expiry))
                print(f"New Token Generated Expiring at: {self.token_expiry_time}")
                print(f"Token: {self.token}\n Token_expiry: {token_expiry}\n Token_expiry_time: {self.token_expiry_time}\n")
                return self.token
            elif str(resp.status_code) == "500" or str(response.get("error")) == "login_failed":
                print(response)
                print("Ensure to Map the API User and API Key as (Username:Password) respectively")
                return None
            else:
                print(resp.text)
                return None
        except Exception as e:
            print(f"Something Is Wrong: {e}")
            return None

    def token_status(self):
        """
        Check token status and regenerate if expired.
        Exact replica of the working Jupyter notebook function.
        """
        if not self.token_expiry_time:
            print("No token expiry time set. Generate a token first.")
            return False
            
        if self.token_expiry_time >= datetime.now():
            self.token_expired = False
            print(f"Token not Expired: Expiring at {self.token_expiry_time}")
            print(self.token)
            return True
        else:
            self.token_expired = True
            print("Token expired, need to regenerate")
            return False

    # Keep the old method names for backward compatibility
    def create_api_user(self, subscription_key):
        """Backward compatibility method"""
        return self.create_api_user_sandbox(subscription_key)
    
    def generate_api_key(self, reference_id, subscription_key):
        """Backward compatibility method"""
        if reference_id != self.api_user:
            self.api_user = reference_id
        return self.create_api_key_sandbox(subscription_key)
    
    def generate_token(self, api_user, api_key, product, subscription_key):
        """Backward compatibility method"""
        if api_user != self.api_user:
            self.api_user = api_user
        if api_key != self.api_key:
            self.api_key = api_key
        return self.get_token(subscription_key, product)


