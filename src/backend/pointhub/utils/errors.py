class ApiError(Exception):
    """ An API error """

    ERRCODE_REQUEST_FORMAT = 1
    ERRCODE_INVALID_FIELD = 2
    ERRCODE_MISSING_FIELD = 3
    ERRCODE_OBJECT_NOT_FOUND = 4
    ERRCODE_OBJECT_ALREADY_EXISTS = 5

    def __init__(self, err_code, *args):
        super().__init__('API Error: {}'.format(err_code))
        self.err_code = err_code
        self.err_args = [str(arg) for arg in args]

    def serialize(self):
        """ Serialize the error """
        return {'error': self.err_code, 'errdata': self.err_args}
