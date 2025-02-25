class LogDataMixin():
    """
    Associate additional data with a model instance that can be subsequently
    retrieved when processing the django-auditlog LogEntry object for that
    instance.
    """
    _log_data = {}

    def set_log_data(self, key, value):
        self._log_data[key] = value

    def get_log_data(self, key):
        self._log_data.get(key, None)

    def clear_log_data(self):
        self._log_data.clear()

    # NOTE: this method has to have this name.
    def get_additional_data(self):
        return self._log_data