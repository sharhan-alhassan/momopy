from datetime import datetime, timedelta
import uuid
import requests

class Base:
    """
    Base Class used across all MTN MoMo models.
    This class manages global state for tokens, API users, and API keys.
    
    Attributes:
        requests (MomoBaseRequests): An instance of the MomoBaseRequests class for making API requests.
    """

    def __init__(self, token=None, **kwargs):
        """
        Initialize MTN MoMo with required credentials.
        """
        # Global state for token management
        self._token = token
        self._token_expiry_time = None
        self._api_user = kwargs.get('api_user')
        self._api_key = kwargs.get('api_key')
        self._subscription_key = kwargs.get('subscription_key')
        
        # Track if api_user was provided during initialization
        self._api_user_provided = 'api_user' in kwargs
        
        # Base configuration
        self._base_url = kwargs.get('base_url', 'https://sandbox.momodeveloper.mtn.com')
        self._environment = kwargs.get('environment', 'sandbox')
        self._callback_host = kwargs.get('callback_host', 'webhook.site')
        
        # Initialize headers
        self._headers = {
            'Content-Type': 'application/json',
            'X-Target-Environment': self._environment,
        }
        
        if self._subscription_key:
            self._headers['Ocp-Apim-Subscription-Key'] = self._subscription_key
            
        if self._token:
            self._headers['Authorization'] = f'Bearer {self._token}'

    @property
    def token(self):
        """Get current token if valid, otherwise return None"""
        if self._token and self._token_expiry_time and self._token_expiry_time > datetime.now():
            return self._token
        return None

    @property
    def api_user(self):
        """Get current API user"""
        return self._api_user

    @property
    def api_key(self):
        """Get current API key"""
        return self._api_key

    @property
    def subscription_key(self):
        """Get current subscription key"""
        return self._subscription_key

    def check_api_user_exists(self, api_user_id, subscription_key):
        """
        Check if an API user already exists.
        
        Args:
            api_user_id (str): The API user ID to check
            subscription_key (str): MTN MoMo subscription key
            
        Returns:
            bool: True if user exists, False otherwise
        """
        url = f"{self._base_url}/v1_0/apiuser/{api_user_id}"
        headers = {
            "Ocp-Apim-Subscription-Key": subscription_key,
        }
        
        try:
            resp = requests.get(url, headers=headers)
            if resp.status_code == 200:
                print(f"✅ API User {api_user_id} already exists")
                return True
            elif resp.status_code == 404:
                print(f"ℹ️ API User {api_user_id} does not exist")
                return False
            else:
                print(f"❌ Error checking API user: {resp.status_code} - {resp.text}")
                return False
        except Exception as e:
            print(f"❌ Error checking API user: {e}")
            return False

    def _create_api_user(self, subscription_key):
        """
        Create an API user in the MTN MoMo Sandbox environment.
        Only creates if the user doesn't already exist.
        """
        # If we already have an API user, check if it exists
        if self._api_user:
            if self.check_api_user_exists(self._api_user, subscription_key):
                print(f"✅ Using existing API User: {self._api_user}")
                return True
            else:
                print(f"ℹ️ API User {self._api_user} does not exist, creating it...")
                # Keep the existing UUID, don't generate a new one
        else:
            # Only generate new UUID if none was provided
            self._api_user = str(uuid.uuid4())
            print(f"🔄 Creating new API User: {self._api_user}")
        
        url = f"{self._base_url}/v1_0/apiuser"
        headers = {
            "X-Reference-Id": self._api_user,
            "Ocp-Apim-Subscription-Key": subscription_key,
            "Content-Type": "application/json"
        }
        body = {
            "providerCallbackHost": self._callback_host
        }
        
        try:
            resp = requests.post(url, json=body, headers=headers)
            if resp.status_code == 201:
                print(f"✅ API User created successfully: {self._api_user}")
                return True
            elif resp.status_code == 409:
                print(f"❌ 409: API User {self._api_user} already exists")
                print("This means the UUID was already used. Generating new UUID...")
                # Try with a new UUID only if we didn't have a specific one
                if not self._api_user_provided:
                    return self._create_api_user(subscription_key)
                else:
                    print("❌ Cannot create API user with specified UUID - it already exists")
                    return False
            elif resp.status_code == 401:
                print(f"❌ 401: {resp.text}")
                print("Ensure the subscription key is the primary")
                return False
            elif resp.status_code == 400:
                print(f"❌ 400: {resp.text}")
                print("Ensure API User(X-Reference-Id) is UUID Version 4")
                return False
            else:
                print(f"❌ {resp.status_code}: {resp.text}")
                return False
        except Exception as e:
            print(f"❌ Error creating API user: {e}")
            return False

    def _create_api_key(self, subscription_key):
        """
        Create an API key for the API user.
        Only creates if the key doesn't already exist.
        """
        if not self._api_user:
            print("❌ API User not created. Create API user first.")
            return False
            
        # Check if we already have an API key
        if self._api_key:
            print(f"✅ Using existing API Key: {self._api_key}")
            return True
            
        url = f"{self._base_url}/v1_0/apiuser/{self._api_user}/apikey"
        headers = {
            "Ocp-Apim-Subscription-Key": subscription_key,
        }
        
        try:
            resp = requests.post(url, headers=headers)
            if resp.status_code == 201:
                response = resp.json()
                self._api_key = response.get('apiKey')
                print(f"✅ API Key generated successfully: {self._api_key}")
                return True
            elif resp.status_code == 400:
                print(f"❌ 400: {resp.text}")
                print("Validate the BaseURL and ensure API_User is created")
                return False
            elif resp.status_code == 404:
                print(f"❌ 404: {resp.text}")
                print("API_USER was not created. Create API user first.")
                return False
            else:
                print(f"❌ {resp.status_code}: {resp.text}")
                return False
        except Exception as e:
            print(f"❌ Error generating API key: {e}")
            return False

    def _generate_token(self, subscription_key, product='collection'):
        """
        Generate token for a specific product.
        """
        if not self._api_user or not self._api_key:
            print("❌ API User and API Key must be created first")
            return None
            
        endpoint = f"{self._base_url}/{product}/token/"
        headers = {
            "Ocp-Apim-Subscription-Key": subscription_key,
        }
        
        try:
            resp = requests.post(endpoint, auth=(self._api_user, self._api_key), headers=headers)
            response = resp.json()
            
            if resp.status_code == 200:
                self._token = response.get('access_token')
                token_expiry = response.get('expires_in')
                self._token_expiry_time = datetime.now() + timedelta(seconds=int(token_expiry))
                print(f"✅ Token generated successfully, expires at: {self._token_expiry_time}")
                return self._token
            elif resp.status_code == 500 or response.get("error") == "login_failed":
                print(f"❌ 500: {response}")
                print("Ensure API User and API Key are mapped correctly")
                return None
            else:
                print(f"❌ {resp.status_code}: {resp.text}")
                return None
        except Exception as e:
            print(f"❌ Error generating token: {e}")
            return None

    def get_api_user_info(self, api_user_id, subscription_key):
        """
        Get detailed information about an existing API user.
        
        Args:
            api_user_id (str): The API user ID to retrieve
            subscription_key (str): MTN MoMo subscription key
            
        Returns:
            dict: API user information if successful, None otherwise
        """
        url = f"{self._base_url}/v1_0/apiuser/{api_user_id}"
        headers = {
            "Ocp-Apim-Subscription-Key": subscription_key,
        }
        
        try:
            resp = requests.get(url, headers=headers)
            if resp.status_code == 200:
                user_info = resp.json()
                print(f"✅ Retrieved API User info: {user_info}")
                return user_info
            elif resp.status_code == 404:
                print(f"ℹ️ API User {api_user_id} not found")
                return None
            else:
                print(f"❌ Error retrieving API user: {resp.status_code} - {resp.text}")
                return None
        except Exception as e:
            print(f"❌ Error retrieving API user: {e}")
            return None

    def setup_api_credentials(self, subscription_key, api_user_id=None, api_key=None):
        """
        Set up API credentials with proper lifecycle management.
        
        Args:
            subscription_key (str): MTN MoMo subscription key
            api_user_id (str, optional): Existing API user ID to reuse
            api_key (str, optional): Existing API key to reuse
            
        Returns:
            bool: True if setup successful, False otherwise
        """
        print("🔄 Setting up API credentials...")
        
        # If provided with existing credentials, verify they work
        if api_user_id and api_key:
            self._api_user = api_user_id
            self._api_key = api_key
            
            # Test if the credentials work by trying to generate a token
            test_token = self._generate_token(subscription_key, 'collection')
            if test_token:
                print("✅ Existing API credentials verified and working")
                return True
            else:
                print("❌ Existing API credentials failed verification")
                # Fall back to creating new ones
        
        # Create new API user and key
        if not self._create_api_user(subscription_key):
            return False
            
        if not self._create_api_key(subscription_key):
            return False
            
        print("✅ API credentials setup completed")
        return True

    def token_status(self):
        """
        Check token status and show expiry information.
        """
        if not self._token_expiry_time:
            print("ℹ️ No token expiry time set. Generate a token first.")
            return False
            
        if self._token_expiry_time > datetime.now():
            remaining = self._token_expiry_time - datetime.now()
            print(f"✅ Token valid, expires in: {remaining}")
            return True
        else:
            print("❌ Token expired")
            return False
