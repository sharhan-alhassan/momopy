
class MoMoAPIError(Exception):
    def __init__(self, status_code, error_message, details=None):
        self.status_code = status_code
        self.error_message = error_message
        self.details = details
        super().__init__(self.error_message)

    def __str__(self):
        return f"HTTP {self.status_code}: {self.error_message}\nDetails: {self.details}"