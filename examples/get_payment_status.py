from mtn.sandbox.sandbox import Sandbox
from mtn.collections.collection import Collection
import os
from mtn.utils.exceptions import MoMoAPIError

def main():
    sandbox = Sandbox()
    collection_token = sandbox.get_token(os.getenv("PRODUCT_SUBSCRIPTION_KEY"), product='collection')

    print(f"Sandbox Token: {collection_token}")
    
    # Create a Collection instance with the token
    collection = Collection(token=collection_token)
    
    # Create a request to pay
    try:
        response = collection.get_payment_status(
            reference_id="e1da8546-17bf-4aab-8beb-13cc8ee52b56"
        )
        print(f"response_status_code: {response['status']}")
        print(f"Request to Pay Response: {response}")
    except MoMoAPIError as e:
        print(f"Error creating request to pay: {str(e)}")
        print(f"Status Code: {e.status_code}")
        print(f"Details: {e.details}")


if __name__ == "__main__":
    main()