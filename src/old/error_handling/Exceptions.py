



class ParamExistsException(Exception):
    """Raised when a param cannot be found in ParamRegister"""
    def __init__(self, query_key: str) -> None:
        message = f'Could not find {query_key} in param register'
        super().__init__(message)