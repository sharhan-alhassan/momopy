from mtn.base import Base
class Collection(Base):
    """
    Collection class for interacting with MTN MoMo Collection API.
    """
    def __init__(self, token=None, **kwargs):
        super().__init__(token=token, **kwargs)

    @classmethod
    def create_request_to_pay(cls, **kwargs):
        """
        Create a request to pay transaction.

        Args:
            amount (str): Amount to be paid.
            currency (str): Currency of the transaction.
            externalId (str): External ID for the transaction.
            payer (dict): Information about the payer.
            payerMessage (str): Message to the payer.
            payeeNote (str): Note to the payee.

        Returns:
            dict: JSON data from MTN MoMo API containing the details of the transaction.
        """
        payload = {
            "amount": kwargs.get("amount"),
            "currency": kwargs.get("currency"),
            "externalId": kwargs.get("external_id"),
            "payer": {
                "partyIdType": kwargs.get("payer_party_id_type"),
                "partyId": kwargs.get("payer_party_id")
            },
            "payerMessage": kwargs.get("payer_message"),
            "payeeNote": kwargs.get("payee_note")
        }
        instance = cls()
        return instance.requests.post('collection/v1_0/requesttopay', data=payload)

    @classmethod
    def get_transaction_status(cls, reference_id):
        """
        Get the status of a transaction.

        Args:
            reference_id (str): Reference ID of the transaction.

        Returns:
            dict: JSON data from MTN MoMo API containing the status of the transaction.
        """
        return cls().requests.get(f'collection/v1_0/requesttopay/{reference_id}')

    @classmethod
    def get_account_balance(cls):
        """
        Get the account balance.

        Returns:
            dict: JSON data from MTN MoMo API containing the account balance.
        """
        return cls().requests.get('collection/v1_0/account/balance')

    @classmethod
    def get_account_status(cls, account_holder_id_type, account_holder_id):
        """
        Get the status of an account holder.

        Args:
            account_holder_id_type (str): Type of account holder ID (e.g., MSISDN).
            account_holder_id (str): Account holder ID.

        Returns:
            dict: JSON data from MTN MoMo API containing the account holder's status.
        """
        return cls().requests.get(f'collection/v1_0/accountholder/{account_holder_id_type}/{account_holder_id}/active')

    @classmethod
    def get_payment_status(cls, reference_id):
        """
        Get the status of a payment
        """
        return cls().requests.get(f'collection/v2_0/payment/{reference_id}')