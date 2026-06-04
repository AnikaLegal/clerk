import django_cleanup.cleanup as cleanup
from auditlog.registry import auditlog
from django.core.exceptions import ValidationError
from django.db import models
from wagtail.admin.panels import FieldPanel
from wagtail.documents import get_document_model
from wagtail.models import DraftStateMixin, RevisionMixin


class Impact(DraftStateMixin, RevisionMixin, models.Model):
    title = models.CharField(max_length=255)
    pdf = models.ForeignKey(
        get_document_model(),
        on_delete=models.PROTECT,
        help_text="PDF document to extract pages from.",
    )
    page_range_start = models.PositiveIntegerField(
        help_text="First page to extract (1-indexed).",
        null=True,
        blank=True,
    )
    page_range_end = models.PositiveIntegerField(
        help_text="Last page to extract (1-indexed, inclusive).",
        null=True,
        blank=True,
    )

    panels = [
        FieldPanel("title"),
        FieldPanel("pdf"),
        FieldPanel("page_range_start"),
        FieldPanel("page_range_end"),
    ]

    def __str__(self):
        return self.title

    def clean(self):
        super().clean()
        if self.page_range_start is not None:
            if self.page_range_start < 1:
                raise ValidationError(
                    {"page_range_start": "Start page must be at least 1."}
                )
            if self.page_range_end is not None:
                if self.page_range_end < self.page_range_start:
                    raise ValidationError(
                        {
                            "page_range_end": "End page must be greater than or equal to start page."
                        }
                    )

    def save(self, *args, **kwargs):
        # Ensure only one live impact exists.
        if self.live:
            Impact.objects.filter(live=True).exclude(pk=self.pk).update(live=False)
        super().save(*args, **kwargs)


@cleanup.select
class ImpactImage(models.Model):
    impact = models.ForeignKey(
        Impact,
        on_delete=models.CASCADE,
        related_name="images",
    )
    page_number = models.PositiveIntegerField()
    image = models.ImageField(upload_to="impact_images/")

    class Meta:
        ordering = ["page_number"]

    def __str__(self):
        return f"{self.impact.title} – page {self.page_number}"


auditlog.register(Impact)
