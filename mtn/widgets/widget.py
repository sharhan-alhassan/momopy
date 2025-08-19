from mtn.base import Base

class Widget(Base):
    """
    Widget class for interacting with MTN MoMo Widget API.
    """

    @classmethod
    def create_widget(cls, **kwargs):
        """
        Create a widget.

        Args:
            name (str): Name of the widget.
            description (str): Description of the widget.
            url (str): URL for the widget.
            amount (str): Amount for the widget.
            currency (str): Currency of the transaction.

        Returns:
            dict: JSON data from MTN MoMo API containing the details of the widget.
        """
        return cls().requests.post('widget/v1_0/widgets', data=kwargs)

    @classmethod
    def get_widget(cls, widget_id):
        """
        Retrieve a widget by its ID.

        Args:
            widget_id (
                widget_id (str): ID of the widget.

        Returns:
            dict: JSON data from MTN MoMo API containing the details of the widget.
        """
        return cls().requests.get(f'widget/v1_0/widgets/{widget_id}')

    @classmethod
    def list_widgets(cls, **kwargs):
        """
        List all widgets, with optional filtering and pagination.

        Args:
            perPage (int, optional): Specify how many records you want to retrieve per page.
                                     Defaults to 50 if not specified.
            page (int, optional): Specify exactly which page you want to retrieve.
                                  Defaults to 1 if not specified.

        Returns:
            dict: JSON data from MTN MoMo API containing the list of widgets.
        """
        return cls().requests.get('widget/v1_0/widgets', params=kwargs)

    @classmethod
    def update_widget(cls, widget_id, **kwargs):
        """
        Update an existing widget by its ID.

        Args:
            widget_id (str): ID of the widget.
            name (str, optional): Name of the widget.
            description (str, optional): Description of the widget.
            url (str, optional): URL for the widget.
            amount (str, optional): Amount for the widget.
            currency (str, optional): Currency of the transaction.

        Returns:
            dict: JSON data from MTN MoMo API containing the updated widget details.
        """
        return cls().requests.put(f'widget/v1_0/widgets/{widget_id}', data=kwargs)
