from django.db import models

from wagtail.core.models import Page
from wagtail.core.fields import RichTextField
from wagtail.admin.edit_handlers import FieldPanel

from wagtail.images.models import Image
from wagtail.images.edit_handlers import ImageChooserPanel

class Blog(Page):
    templates = "web/blog.html"
    main_image = models.ForeignKey(
        'wagtailimages.Image',
        related_name='+',
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )
    images = models.ManyToManyField(
        'wagtailimages.Image',
        related_name='+',
    )
    body = RichTextField()
    content_panels = Page.content_panels + [
        FieldPanel('body', classname="full"),
        # ImageChooserPanel("blog_image")
    ]
     


#postgres command: psql -h 127.0.0.1 -p 25432 -U postgres