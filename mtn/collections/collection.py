import uuid
from mtn.base import Base

class Collection(Base):
    """
    MTN MoMo Collection API client.
    
    This class handles collection operations like requesting debit payments.
    """
    
    def __init__(self, api_user, api_key=None, subscription_key=None, callback_host=None, **kwargs):
        """
        Initialize Collection instance.
        
        Args:
            api_user (str): The API user UUID4 (required) - this is the only thing you should store
            api_key (str, optional): The API key. If not provided, will be auto-generated (RECOMMENDED)
            subscription_key (str): MTN MoMo subscription key
            callback_host (str): Callback host for webhooks
            **kwargs: Additional arguments passed to Base
        """
        super().__init__(**kwargs)
        self._product = 'collection'
        
        # Store the provided credentials
        self._api_user = api_user
        self._api_key = api_key  # Optional - will be auto-generated if not provided
        self._subscription_key = subscription_key
        self._callback_host = callback_host
        
        # Set environment variables for Base class
        if callback_host:
            import os
            os.environ['CALLBACK_HOST'] = callback_host
        
        # Auto-generate token if subscription_key is provided
        if self._subscription_key:
            print("🔄 Auto-generating collection token on instantiation...")
            # Only generate if no valid token exists
            if not hasattr(self, '_token') or not self._token:
                self.generate_collection_token()
            else:
                print("✅ Valid token already exists from previous initialization")
    
    def _ensure_token_available(self):
        """
        Internal method to ensure a valid token is available.
        Auto-generates token if needed or if current token is expired.
        """
        # Check if we have a valid token using the Base class logic
        if not self.token:
            print("ℹ️ No valid token found, generating new one...")
            self.generate_collection_token()
        else:
            print("✅ Valid token already available")
    
    # Remove the token property override - let Base class handle it
    # The Base class already has proper expiry checking logic
    
    @property
    def api_user(self):
        """Get the API user UUID."""
        return self._api_user
    
    @property
    def api_key(self):
        """Get the current API key (auto-generated if needed)."""
        # If no API key exists, generate one automatically
        if not self._api_key and self._subscription_key:
            print("🔄 Auto-generating API key...")
            self.create_api_key()
        return self._api_key
    
    @property
    def subscription_key(self):
        """Get the subscription key."""
        return self._subscription_key
    
    @property
    def callback_host(self):
        """Get the callback host."""
        return self._callback_host
    
    def create_api_key(self, subscription_key=None):
        """
        Create a new API key for the current API user.
        
        Args:
            subscription_key (str, optional): Subscription key. Uses instance default if not provided.
            
        Returns:
            str: The generated API key, or None if failed
        """
        if not subscription_key:
            subscription_key = self._subscription_key
            
        if not subscription_key:
            raise ValueError("Subscription key is required to create API key")
        
        print(f"🔄 Creating API key for API User: {self._api_user}")
        
        # First, ensure the API user exists (create if needed)
        print("🔄 Ensuring API user exists...")
        user_created = self._create_api_user(subscription_key)
        
        if not user_created:
            print("❌ Failed to create/verify API user")
            return None
        
        # Now create the API key
        print("🔄 Creating API key...")
        success = self._create_api_key(subscription_key)
        
        if success:
            # The API key is now stored in self._api_key by the Base class
            print(f"✅ API key created successfully: {self._api_key}")
            print("💾 Store this API key for future use!")
            return self._api_key
        else:
            print("❌ Failed to create API key")
            return None
    
    def generate_collection_token(self, subscription_key=None):
        """
        Generate a collection token.
        
        If api_key is not set, it will be generated first.
        
        Args:
            subscription_key (str, optional): Subscription key. Uses instance default if not provided.
            
        Returns:
            str: The generated token, or None if failed
        """
        if not subscription_key:
            subscription_key = self._subscription_key
            
        if not subscription_key:
            raise ValueError("Subscription key is required to generate token")
        
        # Check if we already have a valid token
        if hasattr(self, '_token') and self._token:
            # Check if token is still valid using Base class logic
            if self.token:  # This calls the Base class token property which checks expiry
                print("✅ Valid token already exists, no need to generate new one")
                return self._token
            else:
                print("ℹ️ Existing token has expired, generating new one...")
        
        print(f"🔄 Generating collection token for API User: {self._api_user}")
        
        # If no API key exists, create one first
        if not self._api_key:
            print("ℹ️ No API key found, creating one first...")
            api_key = self.create_api_key(subscription_key)
            if not api_key:
                print("❌ Failed to create API key, cannot generate token")
                return None
        
        # Now generate the token using the Base class method
        # Note: _generate_token takes subscription_key and optional product
        token = self._generate_token(subscription_key, 'collection')
        
        if token:
            self._token = token
            print(f"✅ Collection token generated successfully!")
            return token
        else:
            print("❌ Failed to generate collection token")
            return None
    
    def create_request_to_pay(self, msisdn, amount, subscription_key=None, callback_url=None):
        """
        Create a request to pay transaction (debit payment from mobile number).
        
        Args:
            msisdn (str): Mobile number to debit
            amount (str): Amount to debit (in cents)
            subscription_key (str, optional): Subscription key. Uses instance default if not provided.
            callback_url (str, optional): Callback URL for webhooks
            
        Returns:
            str: Reference ID if successful, None if failed
        """
        import requests
        
        # Generate unique reference ID for this request
        debit_request_ref_id = str(uuid.uuid4())
        
        url = f"{self._base_url}/collection/v1_0/requesttopay"
        headers = {
            "X-Reference-Id": debit_request_ref_id,
            "X-Target-Environment": self._environment,
            "Ocp-Apim-Subscription-Key": subscription_key or self._subscription_key,
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
        
        # Add callback URL if provided
        if callback_url:
            headers["X-Callback-Url"] = callback_url
        
        body = {
            "amount": amount,
            "currency": "EUR",  # Use EUR in SandBox
            "externalId": str(uuid.uuid1()),  # For reconciliation
            "payer": {
                "partyIdType": "MSISDN",  # EMAIL and ALIAS apply as well
                "partyId": msisdn
            },
            "payerMessage": "MoMo Debit API",
            "payeeNote": "MoMo Debit API"
        }
        
        try:
            resp = requests.post(url, json=body, headers=headers)
            
            if str(resp.status_code) == "202":
                print(f"✅ Debit request to MSISDN {msisdn} Amount {amount} Response Code {resp.status_code}")
                print(f"Request Reference ID: {debit_request_ref_id}")
                return debit_request_ref_id
                
            elif str(resp.status_code) == "404":
                print("❌ 404: Check The Base_URL")
                return None
                
            elif str(resp.status_code) == "400":
                print("❌ 400: Ensure no Special Characters like & in the Message and Notes")
                print("The X-Reference-Id in the header should be UUID Version 4")
                print(resp.text)
                return None
                
            elif str(resp.status_code) == "500":
                if resp.json().get("message", "").endswith("INVALID_CALLBACK_URL_HOST"):
                    print("❌ 500: INVALID_CALLBACK_URL_HOST")
                    print("Ensure the URL Host is the same with the one created when generating API_User function")
                    return None
                elif resp.json().get("message", "").endswith("Currency not supported."):
                    print("❌ 500: Currency not supported")
                    print("Verify and validate Currency for SandBox is EUR")
                    return None
                else:
                    print("❌ 500: API is not available")
                    print(resp.text)
                    return None
            else:
                print(f"❌ {resp.status_code}: {resp.text}")
                return None
                
        except TypeError:
            print("❌ Request Body should be Json Formatted")
            return None
        except Exception as e:
            print(f"❌ Something Is Wrong: {e}")
            return None

    def get_account_balance(self):
        """
        Get the account balance for the collection product.
        
        Returns:
            dict: Account balance information if successful, None if failed
        """
        import requests
        
        # Ensure we have a valid token
        if not self.token:
            print("❌ No valid token available. Generate token first.")
            return None
        
        url = f"{self._base_url}/collection/v1_0/account/balance"
        headers = {
            "X-Target-Environment": self._environment,
            "Ocp-Apim-Subscription-Key": self._subscription_key,
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
        
        try:
            resp = requests.get(url, headers=headers)
            
            if resp.status_code == 200:
                balance_info = resp.json()
                print("✅ Account balance retrieved successfully")
                return balance_info
            elif resp.status_code == 401:
                print("❌ 401: Unauthorized - Token may be expired")
                return None
            elif resp.status_code == 404:
                print("❌ 404: Account balance endpoint not found")
                return None
            else:
                print(f"❌ {resp.status_code}: {resp.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error getting account balance: {e}")
            return None

    def get_account_status(self, account_holder_id_type, account_holder_id):
        """
        Get the status of an account holder.
        
        Args:
            account_holder_id_type (str): Type of account holder ID (e.g., MSISDN, EMAIL, PARTY_CODE).
            account_holder_id (str): Account holder ID.
            
        Returns:
            dict: Account holder status information if successful, None if failed
        """
        import requests
        
        # Ensure we have a valid token
        if not self.token:
            print("❌ No valid token available. Generate token first.")
            return None
        
        url = f"{self._base_url}/collection/v1_0/accountholder/{account_holder_id_type}/{account_holder_id}/active"
        headers = {
            "X-Target-Environment": self._environment,
            "Ocp-Apim-Subscription-Key": self._subscription_key,
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
        
        try:
            resp = requests.get(url, headers=headers)
            
            if resp.status_code == 200:
                status_info = resp.json()
                print(f"✅ Account status retrieved for {account_holder_id_type}: {account_holder_id}")
                return status_info
            elif resp.status_code == 401:
                print("❌ 401: Unauthorized - Token may be expired")
                return None
            elif resp.status_code == 404:
                print(f"❌ 404: Account holder {account_holder_id} not found")
                return None
            else:
                print(f"❌ {resp.status_code}: {resp.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error getting account status: {e}")
            return None

    def get_request_to_pay_status(self, reference_id):
        """
        Get the status of a request to pay transaction.
        
        Args:
            reference_id (str): Reference ID of the request to pay transaction.
            
        Returns:
            dict: Transaction status information if successful, None if failed
        """
        import requests
        
        # Ensure we have a valid token
        if not self.token:
            print("❌ No valid token available. Generate token first.")
            return None
        
        url = f"{self._base_url}/collection/v1_0/requesttopay/{reference_id}"
        headers = {
            "X-Target-Environment": self._environment,
            "Ocp-Apim-Subscription-Key": self._subscription_key,
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
        
        try:
            resp = requests.get(url, headers=headers)
            
            if resp.status_code == 200:
                status_info = resp.json()
                print(f"✅ Request to pay status retrieved for reference: {reference_id}")
                return status_info
            elif resp.status_code == 401:
                print("❌ 401: Unauthorized - Token may be expired")
                return None
            elif resp.status_code == 404:
                print(f"❌ 404: Request to pay transaction {reference_id} not found")
                return None
            else:
                print(f"❌ {resp.status_code}: {resp.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error getting request to pay status: {e}")
            return None

    def cancel_request_to_pay(self, reference_id):
        """
        Cancel a request to pay transaction.
        
        Args:
            reference_id (str): Reference ID of the request to pay transaction to cancel.
            
        Returns:
            bool: True if cancellation successful, False otherwise
        """
        import requests
        
        # Ensure we have a valid token
        if not self.token:
            print("❌ No valid token available. Generate token first.")
            return False
        
        url = f"{self._base_url}/collection/v1_0/requesttopay/{reference_id}"
        headers = {
            "X-Target-Environment": self._environment,
            "Ocp-Apim-Subscription-Key": self._subscription_key,
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
        
        try:
            resp = requests.delete(url, headers=headers)
            
            if resp.status_code == 200:
                print(f"✅ Request to pay transaction {reference_id} cancelled successfully")
                return True
            elif resp.status_code == 401:
                print("❌ 401: Unauthorized - Token may be expired")
                return False
            elif resp.status_code == 404:
                print(f"❌ 404: Request to pay transaction {reference_id} not found")
                return False
            elif resp.status_code == 409:
                print(f"❌ 409: Cannot cancel transaction {reference_id} - already processed")
                return False
            else:
                print(f"❌ {resp.status_code}: {resp.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error cancelling request to pay: {e}")
            return False

    # Additional Collection API Endpoints
    
    def bc_authorize(self, **kwargs):
        """
        BC Authorize endpoint for collection.
        
        Args:
            **kwargs: Authorization parameters
            
        Returns:
            dict: Authorization response if successful, None if failed
        """
        import requests
        
        if not self.token:
            print("❌ No valid token available. Generate token first.")
            return None
        
        url = f"{self._base_url}/collection/v1_0/bc-authorize"
        headers = {
            "X-Target-Environment": self._environment,
            "Ocp-Apim-Subscription-Key": self._subscription_key,
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
        
        try:
            resp = requests.post(url, json=kwargs, headers=headers)
            
            if resp.status_code == 200:
                print("✅ BC Authorize successful")
                return resp.json()
            else:
                print(f"❌ {resp.status_code}: {resp.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error in BC Authorize: {e}")
            return None

    def cancel_invoice(self, reference_id):
        """
        Cancel an invoice.
        
        Args:
            reference_id (str): Reference ID of the invoice to cancel
            
        Returns:
            bool: True if cancellation successful, False otherwise
        """
        import requests
        
        if not self.token:
            print("❌ No valid token available. Generate token first.")
            return False
        
        url = f"{self._base_url}/collection/v1_0/invoice/{reference_id}"
        headers = {
            "X-Target-Environment": self._environment,
            "Ocp-Apim-Subscription-Key": self._subscription_key,
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
        
        try:
            resp = requests.delete(url, headers=headers)
            
            if resp.status_code == 200:
                print(f"✅ Invoice {reference_id} cancelled successfully")
                return True
            else:
                print(f"❌ {resp.status_code}: {resp.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error cancelling invoice: {e}")
            return False

    def cancel_pre_approval(self, reference_id):
        """
        Cancel a pre-approval.
        
        Args:
            reference_id (str): Reference ID of the pre-approval to cancel
            
        Returns:
            bool: True if cancellation successful, False otherwise
        """
        import requests
        
        if not self.token:
            print("❌ No valid token available. Generate token first.")
            return False
        
        url = f"{self._base_url}/collection/v1_0/preapproval/{reference_id}"
        headers = {
            "X-Target-Environment": self._environment,
            "Ocp-Apim-Subscription-Key": self._subscription_key,
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
        
        try:
            resp = requests.delete(url, headers=headers)
            
            if resp.status_code == 200:
                print(f"✅ Pre-approval {reference_id} cancelled successfully")
                return True
            else:
                print(f"❌ {resp.status_code}: {resp.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error cancelling pre-approval: {e}")
            return False

    def create_access_token(self, **kwargs):
        """
        Create an access token.
        
        Args:
            **kwargs: Access token parameters
            
        Returns:
            dict: Access token response if successful, None if failed
        """
        import requests
        
        if not self.token:
            print("❌ No valid token available. Generate token first.")
            return None
        
        url = f"{self._base_url}/collection/v1_0/access-token"
        headers = {
            "X-Target-Environment": self._environment,
            "Ocp-Apim-Subscription-Key": self._subscription_key,
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
        
        try:
            resp = requests.post(url, json=kwargs, headers=headers)
            
            if resp.status_code == 200:
                print("✅ Access token created successfully")
                return resp.json()
            else:
                print(f"❌ {resp.status_code}: {resp.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error creating access token: {e}")
            return None

    def create_invoice(self, **kwargs):
        """
        Create an invoice.
        
        Args:
            **kwargs: Invoice parameters
            
        Returns:
            dict: Invoice response if successful, None if failed
        """
        import requests
        
        if not self.token:
            print("❌ No valid token available. Generate token first.")
            return None
        
        url = f"{self._base_url}/collection/v1_0/invoice"
        headers = {
            "X-Target-Environment": self._environment,
            "Ocp-Apim-Subscription-Key": self._subscription_key,
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
        
        try:
            resp = requests.post(url, json=kwargs, headers=headers)
            
            if resp.status_code == 201:
                print("✅ Invoice created successfully")
                return resp.json()
            else:
                print(f"❌ {resp.status_code}: {resp.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error creating invoice: {e}")
            return None

    def create_oauth2_token(self, **kwargs):
        """
        Create an OAuth2 token.
        
        Args:
            **kwargs: OAuth2 token parameters
            
        Returns:
            dict: OAuth2 token response if successful, None if failed
        """
        import requests
        
        if not self.token:
            print("❌ No valid token available. Generate token first.")
            return None
        
        url = f"{self._base_url}/collection/v1_0/oauth2/token"
        headers = {
            "X-Target-Environment": self._environment,
            "Ocp-Apim-Subscription-Key": self._subscription_key,
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
        
        try:
            resp = requests.post(url, json=kwargs, headers=headers)
            
            if resp.status_code == 200:
                print("✅ OAuth2 token created successfully")
                return resp.json()
            else:
                print(f"❌ {resp.status_code}: {resp.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error creating OAuth2 token: {e}")
            return None

    def create_payments(self, **kwargs):
        """
        Create payments.
        
        Args:
            **kwargs: Payment parameters
            
        Returns:
            dict: Payment response if successful, None if failed
        """
        import requests
        
        if not self.token:
            print("❌ No valid token available. Generate token first.")
            return None
        
        url = f"{self._base_url}/collection/v1_0/payments"
        headers = {
            "X-Target-Environment": self._environment,
            "Ocp-Apim-Subscription-Key": self._subscription_key,
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
        
        try:
            resp = requests.post(url, json=kwargs, headers=headers)
            
            if resp.status_code == 201:
                print("✅ Payments created successfully")
                return resp.json()
            else:
                print(f"❌ {resp.status_code}: {resp.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error creating payments: {e}")
            return None

    def get_account_balance_in_specific_currency(self, currency):
        """
        Get account balance in a specific currency.
        
        Args:
            currency (str): Currency code (e.g., 'EUR', 'USD')
            
        Returns:
            dict: Account balance in specific currency if successful, None if failed
        """
        import requests
        
        if not self.token:
            print("❌ No valid token available. Generate token first.")
            return None
        
        url = f"{self._base_url}/collection/v1_0/account/balance/{currency}"
        headers = {
            "X-Target-Environment": self._environment,
            "Ocp-Apim-Subscription-Key": self._subscription_key,
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
        
        try:
            resp = requests.get(url, headers=headers)
            
            if resp.status_code == 200:
                print(f"✅ Account balance in {currency} retrieved successfully")
                return resp.json()
            else:
                print(f"❌ {resp.status_code}: {resp.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error getting account balance in {currency}: {e}")
            return None

    def get_approved_pre_approvals(self):
        """
        Get approved pre-approvals.
        
        Returns:
            dict: Approved pre-approvals if successful, None if failed
        """
        import requests
        
        if not self.token:
            print("❌ No valid token available. Generate token first.")
            return None
        
        url = f"{self._base_url}/collection/v1_0/preapproval"
        headers = {
            "X-Target-Environment": self._environment,
            "Ocp-Apim-Subscription-Key": self._subscription_key,
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
        
        try:
            resp = requests.get(url, headers=headers)
            
            if resp.status_code == 200:
                print("✅ Approved pre-approvals retrieved successfully")
                return resp.json()
            else:
                print(f"❌ {resp.status_code}: {resp.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error getting approved pre-approvals: {e}")
            return None

    def get_basic_userinfo(self):
        """
        Get basic user information.
        
        Returns:
            dict: Basic user information if successful, None if failed
        """
        import requests
        
        if not self.token:
            print("❌ No valid token available. Generate token first.")
            return None
        
        url = f"{self._base_url}/collection/v1_0/userinfo"
        headers = {
            "X-Target-Environment": self._environment,
            "Ocp-Apim-Subscription-Key": self._subscription_key,
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
        
        try:
            resp = requests.get(url, headers=headers)
            
            if resp.status_code == 200:
                print("✅ Basic user information retrieved successfully")
                return resp.json()
            else:
                print(f"❌ {resp.status_code}: {resp.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error getting basic user information: {e}")
            return None

    def get_invoice_status(self, reference_id):
        """
        Get invoice status.
        
        Args:
            reference_id (str): Reference ID of the invoice
            
        Returns:
            dict: Invoice status if successful, None if failed
        """
        import requests
        
        if not self.token:
            print("❌ No valid token available. Generate token first.")
            return None
        
        url = f"{self._base_url}/collection/v1_0/invoice/{reference_id}"
        headers = {
            "X-Target-Environment": self._environment,
            "Ocp-Apim-Subscription-Key": self._subscription_key,
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
        
        try:
            resp = requests.get(url, headers=headers)
            
            if resp.status_code == 200:
                print(f"✅ Invoice status for {reference_id} retrieved successfully")
                return resp.json()
            else:
                print(f"❌ {resp.status_code}: {resp.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error getting invoice status: {e}")
            return None

    def get_payment_status(self, reference_id):
        """
        Get payment status.
        
        Args:
            reference_id (str): Reference ID of the payment
            
        Returns:
            dict: Payment status if successful, None if failed
        """
        import requests
        
        if not self.token:
            print("❌ No valid token available. Generate token first.")
            return None
        
        url = f"{self._base_url}/collection/v1_0/payments/{reference_id}"
        headers = {
            "X-Target-Environment": self._environment,
            "Ocp-Apim-Subscription-Key": self._subscription_key,
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
        
        try:
            resp = requests.get(url, headers=headers)
            
            if resp.status_code == 200:
                print(f"✅ Payment status for {reference_id} retrieved successfully")
                return resp.json()
            else:
                print(f"❌ {resp.status_code}: {resp.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error getting payment status: {e}")
            return None

    def get_pre_approval_status(self, reference_id):
        """
        Get pre-approval status.
        
        Args:
            reference_id (str): Reference ID of the pre-approval
            
        Returns:
            dict: Pre-approval status if successful, None if failed
        """
        import requests
        
        if not self.token:
            print("❌ No valid token available. Generate token first.")
            return None
        
        url = f"{self._base_url}/collection/v1_0/preapproval/{reference_id}"
        headers = {
            "X-Target-Environment": self._environment,
            "Ocp-Apim-Subscription-Key": self._subscription_key,
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
        
        try:
            resp = requests.get(url, headers=headers)
            
            if resp.status_code == 200:
                print(f"✅ Pre-approval status for {reference_id} retrieved successfully")
                return resp.json()
            else:
                print(f"❌ {resp.status_code}: {resp.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error getting pre-approval status: {e}")
            return None

    def get_user_info_with_consent(self, **kwargs):
        """
        Get user information with consent.
        
        Args:
            **kwargs: Consent parameters
            
        Returns:
            dict: User information with consent if successful, None if failed
        """
        import requests
        
        if not self.token:
            print("❌ No valid token available. Generate token first.")
            return None
        
        url = f"{self._base_url}/collection/v1_0/userinfo"
        headers = {
            "X-Target-Environment": self._environment,
            "Ocp-Apim-Subscription-Key": self._subscription_key,
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
        
        try:
            resp = requests.post(url, json=kwargs, headers=headers)
            
            if resp.status_code == 200:
                print("✅ User information with consent retrieved successfully")
                return resp.json()
            else:
                print(f"❌ {resp.status_code}: {resp.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error getting user information with consent: {e}")
            return None

    def pre_approval(self, **kwargs):
        """
        Create a pre-approval.
        
        Args:
            **kwargs: Pre-approval parameters
            
        Returns:
            dict: Pre-approval response if successful, None if failed
        """
        import requests
        
        if not self.token:
            print("❌ No valid token available. Generate token first.")
            return None
        
        url = f"{self._base_url}/collection/v1_0/preapproval"
        headers = {
            "X-Target-Environment": self._environment,
            "Ocp-Apim-Subscription-Key": self._subscription_key,
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
        
        try:
            resp = requests.post(url, json=kwargs, headers=headers)
            
            if resp.status_code == 201:
                print("✅ Pre-approval created successfully")
                return resp.json()
            else:
                print(f"❌ {resp.status_code}: {resp.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error creating pre-approval: {e}")
            return None

    def request_to_pay_delivery_notification(self, reference_id, **kwargs):
        """
        Send request to pay delivery notification.
        
        Args:
            reference_id (str): Reference ID of the request to pay
            **kwargs: Notification parameters
            
        Returns:
            bool: True if notification sent successfully, False otherwise
        """
        import requests
        
        if not self.token:
            print("❌ No valid token available. Generate token first.")
            return False
        
        url = f"{self._base_url}/collection/v1_0/requesttopay/{reference_id}/deliverynotification"
        headers = {
            "X-Target-Environment": self._environment,
            "Ocp-Apim-Subscription-Key": self._subscription_key,
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
        
        try:
            resp = requests.post(url, json=kwargs, headers=headers)
            
            if resp.status_code == 200:
                print(f"✅ Delivery notification sent for {reference_id}")
                return True
            else:
                print(f"❌ {resp.status_code}: {resp.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error sending delivery notification: {e}")
            return False

    def request_to_pay_transaction_status(self, reference_id):
        """
        Get request to pay transaction status.
        
        Args:
            reference_id (str): Reference ID of the request to pay
            
        Returns:
            dict: Transaction status if successful, None if failed
        """
        import requests
        
        if not self.token:
            print("❌ No valid token available. Generate token first.")
            return None
        
        url = f"{self._base_url}/collection/v1_0/requesttopay/{reference_id}/transactionstatus"
        headers = {
            "X-Target-Environment": self._environment,
            "Ocp-Apim-Subscription-Key": self._subscription_key,
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
        
        try:
            resp = requests.get(url, headers=headers)
            
            if resp.status_code == 200:
                print(f"✅ Transaction status for {reference_id} retrieved successfully")
                return resp.json()
            else:
                print(f"❌ {resp.status_code}: {resp.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error getting transaction status: {e}")
            return None

    def request_to_withdraw_transaction_status(self, reference_id):
        """
        Get request to withdraw transaction status.
        
        Args:
            reference_id (str): Reference ID of the withdraw request
            
        Returns:
            dict: Withdraw transaction status if successful, None if failed
        """
        import requests
        
        if not self.token:
            print("❌ No valid token available. Generate token first.")
            return None
        
        url = f"{self._base_url}/collection/v1_0/withdraw/{reference_id}/transactionstatus"
        headers = {
            "X-Target-Environment": self._environment,
            "Ocp-Apim-Subscription-Key": self._subscription_key,
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
        
        try:
            resp = requests.get(url, headers=headers)
            
            if resp.status_code == 200:
                print(f"✅ Withdraw transaction status for {reference_id} retrieved successfully")
                return resp.json()
            else:
                print(f"❌ {resp.status_code}: {resp.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error getting withdraw transaction status: {e}")
            return None

    def request_to_withdraw_v1(self, **kwargs):
        """
        Request to withdraw (V1).
        
        Args:
            **kwargs: Withdraw parameters
            
        Returns:
            dict: Withdraw response if successful, None if failed
        """
        import requests
        
        if not self.token:
            print("❌ No valid token available. Generate token first.")
            return None
        
        url = f"{self._base_url}/collection/v1_0/withdraw"
        headers = {
            "X-Target-Environment": self._environment,
            "Ocp-Apim-Subscription-Key": self._subscription_key,
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
        
        try:
            resp = requests.post(url, json=kwargs, headers=headers)
            
            if resp.status_code == 201:
                print("✅ Withdraw request (V1) created successfully")
                return resp.json()
            else:
                print(f"❌ {resp.status_code}: {resp.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error creating withdraw request (V1): {e}")
            return None

    def request_to_withdraw_v2(self, **kwargs):
        """
        Request to withdraw (V2).
        
        Args:
            **kwargs: Withdraw parameters
            
        Returns:
            dict: Withdraw response if successful, None if failed
        """
        import requests
        
        if not self.token:
            print("❌ No valid token available. Generate token first.")
            return None
        
        url = f"{self._base_url}/collection/v2_0/withdraw"
        headers = {
            "X-Target-Environment": self._environment,
            "Ocp-Apim-Subscription-Key": self._subscription_key,
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
        
        try:
            resp = requests.post(url, json=kwargs, headers=headers)
            
            if resp.status_code == 201:
                print("✅ Withdraw request (V2) created successfully")
                return resp.json()
            else:
                print(f"❌ {resp.status_code}: {resp.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error creating withdraw request (V2): {e}")
            return None

    def validate_account_holder_status(self, account_holder_id_type, account_holder_id):
        """
        Validate account holder status.
        
        Args:
            account_holder_id_type (str): Type of account holder ID (e.g., MSISDN, EMAIL, PARTY_CODE)
            account_holder_id (str): Account holder ID
            
        Returns:
            dict: Account holder validation status if successful, None if failed
        """
        import requests
        
        if not self.token:
            print("❌ No valid token available. Generate token first.")
            return None
        
        url = f"{self._base_url}/collection/v1_0/accountholder/{account_holder_id_type}/{account_holder_id}/active"
        headers = {
            "X-Target-Environment": self._environment,
            "Ocp-Apim-Subscription-Key": self._subscription_key,
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
        
        try:
            resp = requests.get(url, headers=headers)
            
            if resp.status_code == 200:
                print(f"✅ Account holder {account_holder_id} validation successful")
                return resp.json()
            else:
                print(f"❌ {resp.status_code}: {resp.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error validating account holder status: {e}")
            return None