# momopy
API Wrapper for MTN Mobile Money 

# Sanbox Keys Generation
```sh
1. First create an API USER at /apiuser {POST} using headers
- X-Reference-Id -- A UUID
- Ocp-Apim-Subscription-Key -- Your subscription (Primary or Secondary)

2. Use API USER to then generate an API KEY

3. Then proceed to use the API KEY to generate a "TOKEN" for the Bearer Token you want to use in any of the product

The API KEY expires in 3600 seconds, and you need to dynamically check and regenerate one if it expires on the fly

# Contributing
```sh
pip install -e . --no-deps

```


## MTN MoMo API Resource Lifecycle:

1. API User (X-Reference-Id)
Created: ONCE when you first set up your integration
Reused: ALWAYS - this is your permanent user ID
Stored: In your database/config for reuse
Purpose: Identifies your application to MTN MoMo

2. API Key
Created: ONCE per API User
Reused: ALWAYS - this is your permanent secret
Stored: In your database/config for reuse
Purpose: Authenticates your application

3. Bearer Token
Created: ON DEMAND when needed
Reused: UNTIL EXPIRY (usually 1 hour)
Stored: In memory/cache temporarily
Purpose: Authorizes individual API requests

## Summary 
🔄 What Happens ONCE (Setup Phase):
API User Creation - Creates permanent user ID in MTN system
API Key Generation - Creates permanent secret for that user
Stored in Your DB - Save these for reuse

🔄 What Happens REPEATEDLY (Runtime):
Bearer Token Generation - Every hour or when expired
API Calls - Using the valid bearer token

🔄 What Happens CONDITIONALLY:
API User Recreation - Only if you lose your stored credentials
API Key Recreation - Only if you lose your stored credentials
