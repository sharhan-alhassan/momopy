from mtn.base import Base

class Remittance(Base):
    """
    Remittance class for interacting with MTN MoMo Remittance API.
    """

    @classmethod
    def transfer(cls, **kwargs):
        """
        Transfer money to a recipient.

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
        return cls().requests.post('remittance/v1_0/transfer', data=kwargs)

    @classmethod
    def get_transfer_status(cls, reference_id):
        """
        Get the status of a transfer.

        Args:
            reference_id (str): Reference ID of the transfer.

        Returns:
            dict: JSON data from MTN MoMo API containing the status of the transfer.
        """
        return cls().requests.get(f'remittance/v1_0/transfer/{reference_id}')

    @classmethod
    def get_account_balance(cls):
        """
        Get the account balance.

        Returns:
            dict: JSON data from MTN MoMo API containing the account balance.
        """
        return cls().requests.get('remittance/v1_0/account/balance')
