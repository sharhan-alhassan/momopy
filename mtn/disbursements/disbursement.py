from mtn.base import Base

class Disbursement(Base):
    """
    Disbursement class for interacting with MTN MoMo Disbursement API.
    """
    
    def __init__(self, token=None, **kwargs):
        """
        Initialize Disbursement with optional token and credentials.
        
        Args:
            token (str, optional): Existing Bearer token
            **kwargs: Additional arguments passed to Base class
                - api_user: Custom API user ID
                - api_key: Custom API key  
                - subscription_key: MTN MoMo subscription key
                - base_url: API base URL
                - environment: Target environment (sandbox/production)
                - callback_host: Callback host for webhooks
        """
        super().__init__(token=token, **kwargs)
        
        # Set default product for token generation
        self._product = 'disbursement'

    def generate_disbursement_token(self, subscription_key=None, api_user=None, api_key=None):
        """
        Generate disbursement token with smart caching.
        If token exists and is valid, reuse it. Otherwise, generate new one.
        
        Args:
            subscription_key (str, optional): MTN MoMo subscription key
            api_user (str, optional): Custom API user ID (generates UUID if not provided)
            api_key (str, optional): Custom API key
            
        Returns:
            str: Valid Bearer token for disbursement API
            
        Raises:
            ValueError: If subscription key is missing
            Exception: If token generation fails
        """
        # Override product for disbursement
        if not self._api_user or not self._api_key:
            # Need to create API user and key first
            if not self._create_api_user(subscription_key):
                raise Exception("Failed to create API user")
                
            if not self._create_api_key(subscription_key):
                raise Exception("Failed to create API key")
        
        return self._generate_token(subscription_key, 'disbursement')

    @classmethod
    def create_transfer(cls, **kwargs):
        """
        Create a transfer.

        Args:
            amount (str): Amount to be transferred.
            currency (str): Currency of the transaction.
            externalId (str): External ID for the transaction.
            payee (dict): Information about the payee.
            payerMessage (str): Message to the payer.
            payeeNote (str): Note to the payee.

        Returns:
            dict: JSON data from MTN MoMo API containing the details of the transfer.
        """
        return cls().requests.post('disbursement/v1_0/transfer', data=kwargs)

    @classmethod
    def get_transfer_status(cls, reference_id):
        """
        Get the status of a transfer.

        Args:
            reference_id (str): Reference ID of the transfer.

        Returns:
            dict: JSON data from MTN MoMo API containing the status of the transfer.
        """
        return cls().requests.get(f'disbursement/v1_0/transfer/{reference_id}')

    @classmethod
    def get_account_balance(cls):
        """
        Get the account balance.

        Returns:
            dict: JSON data from MTN MoMo API containing the account balance.
        """
        return cls().requests.get('disbursement/v1_0/account/balance')
