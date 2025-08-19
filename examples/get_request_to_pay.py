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
        response = collection.create_request_to_pay(
            amount="1000",
            currency="EUR",
            external_id="123456789",
            payer_party_id_type="MSISDN",
            payer_party_id="46733123453",
            payer_message="Payment message",
            payee_note="Payment note"
        )
        print(f"response_status_code: {response.status_code}")
        print(f"Request to Pay Response: {response}")
    except MoMoAPIError as e:
        print(f"Error creating request to pay: {str(e)}")
        print(f"Status Code: {e.status_code}")
        print(f"Details: {e.details}")


if __name__ == "__main__":
    main()