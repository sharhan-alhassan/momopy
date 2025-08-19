from mtn.sandbox.sandbox import Sandbox
from mtn.collections.collection import Collection
import os

def main():
    sandbox = Sandbox()
    collection_token = sandbox.get_token(os.getenv("PRODUCT_SUBSCRIPTION_KEY"), product='collection')
    
    # Create a Collection instance with the token
    collection = Collection(token=collection_token)
    
    # Get the account balance
    try:
        balance = collection.get_account_balance()
        print(f"Account Balance: {balance}")
    except Exception as e:
        print(f"Error getting account balance: {str(e)}")

if __name__ == "__main__":
    main()