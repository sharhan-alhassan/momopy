import logging
import requests

logging.basicConfig(level=logging.DEBUG)

from mtn.sandbox.sandbox import Sandbox
import os

sandbox = Sandbox()
collection_token = sandbox.get_token(os.getenv("PRODUCT_SUBSCRIPTION_KEY"), product='collection')
    
response = requests.post(
    url='https://sandbox.momodeveloper.mtn.com/collection/v1_0/requesttopay',
    headers={
        'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSMjU2In0.eyJjbGllbnRJZCI6Ijk5Zjg5OTYyLWI1NGYtNDg2OS1hYzc0LWE2MzAxZDZhZjc3NSIsImV4cGlyZXMiOiIyMDI0LTA4LTA1VDE5OjIxOjUxLjA1MiIsInNlc3Npb25JZCI6ImQyYjQwMzljLWMwNDgtNGU0Yy1iZTY5LWUwNDQ3NTUzYmI0ZCJ9.Q3NGHXBh8klOHsNoZ2aHfd7_UFX9f__57NwjIiqNPRxccUoQpC_Jwx5gRBZW0R9oq267du4RCrQNllLpLB7DZRMFxAS_iKnWHhloI1V7eXq5wQuE7A3yRU0lLlyqLK6rjQkkzaIkTZXO3mXIa76CEArdMcqTALIUe2-CGb8L61cZzfIXiXOhgkkha-LmcZXR3GFTukZKUZu4FgyRdjnAdneu-SXNm4AOw3mOfTnWlxxR4SxQkwNKxTjg-clFguNi-Bx45Y9CuRMk-r7753yJo_C32UJaLh-XlgJXyoKE0vkZuQfWN0qK-7XjwqigfxE9dhY1_wGgHXHqRWdFn8gnTw',
        'X-Reference-Id': f'{collection_token}',
        'Content-Type': 'application/json',
        'Ocp-Apim-Subscription-Key': 'd604fb7fc92e47a295add943ac004a09',
        'X-Target-Environment': 'sandbox',
    },
    json={
        "amount": "1000",
        "currency": "EUR",
        "externalId": "123456789",
        "payer": {
            "partyIdType": "MSISDN",
            "partyId": "46733123453",
        },
        "payerMessage": "Payment Message",
        "payeeNote": "Payment note"
    }
)

print(response.status_code)
print(response.text)
