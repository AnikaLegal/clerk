from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.core.exceptions import ValidationError
from wagtail.admin.panels import FieldPanel, PublishingPanel, MultiFieldPanel
from wagtail.documents import get_document_model
from wagtail.models import DraftStateMixin, RevisionMixin


class Report(DraftStateMixin, RevisionMixin, models.Model):  # pyright: ignore[reportIncompatibleVariableOverride]
    """
    Represents a report which can be either a document or a blog page, but not both.
    """

    title = models.CharField()
    description = models.TextField(blank=True)
    document = models.ForeignKey(
        get_document_model(),
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )
    accessible_document = models.ForeignKey(
        get_document_model(),
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="+",
        help_text="An accessible version of the report document (e.g., tagged PDF or Word document). Optional.",
    )
    blog_page = models.ForeignKey(
        "web.BlogPage",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )

    is_featured = models.BooleanField(
        default=False,
        help_text="Whether to feature this report prominently on the reports page. Only one report can be featured at a time.",
    )

    _revisions = GenericRelation("wagtailcore.Revision")

    panels = [
        FieldPanel("title"),
        FieldPanel("description"),
        FieldPanel("is_featured"),
        MultiFieldPanel(
            [
                FieldPanel("document"),
                FieldPanel("accessible_document"),
                FieldPanel("blog_page"),
            ],
            heading="Report content",
            help_text="Choose a document (including an optional accessible version) OR a blog post as the report content. Not both.",
        ),
        PublishingPanel(),
    ]

    def save(self, *args, **kwargs):
        # Ensure only one featured report exists at a time.
        if self.is_featured:
            Report.objects.filter(is_featured=True).exclude(pk=self.pk).update(
                is_featured=False
            )
        super().save(*args, **kwargs)

    def clean(self) -> None:
        if self.document and self.blog_page:
            raise ValidationError(
                "Please choose either a document or a blog page as the report content, not both."
            )
        if not self.document and not self.blog_page:
            raise ValidationError(
                "Please choose a document or a blog page as the report content."
            )
        return super().clean()

    @property
    def revisions(self):
        return self._revisions

    def __str__(self):
        return self.title
