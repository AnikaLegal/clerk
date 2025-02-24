from django.db import models

class AdditionalLogDataModel(models.Model):
    log_data = {}

    def set_log_data(self, key, value):
        self.log_data[key] = value

    def get_log_data(self, key):
        self.log_data.get(key, None)

    def clear_log_data(self):
        self.log_data.clear()

    # NOTE: this method has to have this name.
    def get_additional_data(self):
        return self.log_data

    class Meta:
        abstract = True
