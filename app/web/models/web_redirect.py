from django.db import models


class WebRedirect(models.Model):
    class Meta:
        unique_together = ["source_path", "destination_path"]

    source_path = models.CharField(max_length=2048)
    destination_path = models.CharField(max_length=2048)
    is_permanent = models.BooleanField()

    def normalise_paths(self):
        self.source_path = self.source_path.strip("/")
        self.destination_path = "/" + self.destination_path.strip("/") + "/"
        if self.destination_path == "//":
            self.destination_path = "/"

    def save(self, *args, **kwargs):
        self.normalise_paths()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"from {self.source_path} to {self.destination_path}"
