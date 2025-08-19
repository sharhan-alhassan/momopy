
import os
from mtn.sandbox.sandbox import Sandbox
from mtn.collections.collection import Collection

# Set environment variables (this would typically be done in your environment or a configuration file)
# os.environ['ENVIRONMENT'] = 'development'  # or 'production'
# os.environ['SUBSCRIPTION_KEY'] = 'YOUR_SUBSCRIPTION_KEY'
# os.environ['CALLBACK_HOST'] = 'YOUR_CALLBACK_HOST'

# def get_token():
#     environment = os.getenv('ENVIRONMENT')
    
#     if environment == 'development':
#         sandbox = Sandbox()
#         return sandbox.get_token()
#     elif environment == 'production':
#         # Use the provided API key and token from the MTN OVA management dashboard
#         api_key = os.getenv('API_KEY')
#         token = os.getenv('USER_TOKEN')
#         return f'Bearer {token}'
#     else:
#         raise ValueError("Invalid environment specified")

def main():
    sandbox = Sandbox()
    token = sandbox.get_token()
    # headers = {
    #     'Authorization': token,
    #     'Ocp-Apim-Subscription-Key': os.getenv('SUBSCRIPTION_KEY')
    # }
    
    print(f"Sandbox Token: {token}")
    # Example usage of Collection in production or sandbox environment
    # Example of listing collections
    collections = Collection.get_account_balance()
    print(collections)

if __name__ == "__main__":
    main()
