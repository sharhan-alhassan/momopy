from mtn.base import Base

class Disbursement(Base):
    """
    Disbursement class for interacting with MTN MoMo Disbursement API.
    """

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
