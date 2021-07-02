import random
from io import BytesIO
import json
import hashlib

import requests
from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils.text import slugify
from django.core.files.images import ImageFile
from faker import Factory
from wagtail.images import get_image_model
from django.db import transaction

WagtailImage = get_image_model()

from accounts.models import User
from web.models import BlogListPage, BlogPage, NewsListPage, NewsPage

NUM_BLOG_POSTS = 12
NUM_NEWS_POSTS = 5
NUM_IMAGES = 30


class Command(BaseCommand):
    help = "Setup test blog posts for the website"

    def handle(self, *args, **kwargs):
        assert settings.DEBUG, "NEVER RUN THIS IN PROD!"
        images = self._get_images()
        self._build_posts(images)

    @transaction.atomic
    def _get_images(self):
        if WagtailImage.objects.count() < NUM_IMAGES:
            images = [get_wagtail_image() for _ in range(NUM_IMAGES)]
        else:
            images = list(WagtailImage.objects.all())

        return images

    @transaction.atomic
    def _build_posts(self, images):
        u = User.objects.filter(first_name__isnull=False).last()
        fake = Factory.create("en_AU")
        get_img = lambda: {"type": "image", "value": random.choice(images).id}
        get_heading = lambda: {"type": "heading", "value": fake.sentence()}
        get_quote = lambda: {"type": "quote", "value": fake.sentence()}
        get_para = lambda: {
            "type": "paragraph",
            "value": fake.paragraph(nb_sentences=random.randint(7, 20)),
        }

        NewsPage.objects.all().delete()
        parent_page = NewsListPage.objects.last()
        for i in range(NUM_NEWS_POSTS):
            print("Creating news post", i)
            title = fake.sentence()
            model_data = {
                "title": title,
                "slug": slugify(title),
                "search_description": fake.sentence(),
                "owner_id": u.id,
                "body": json.dumps(
                    [
                        get_para(),
                        get_img(),
                        get_para(),
                        get_heading(),
                        get_para(),
                        get_quote(),
                        get_para(),
                        get_img(),
                        get_para(),
                    ]
                ),
            }
            article = NewsPage(**model_data)
            parent_page.add_child(instance=article)
            article.save_revision().publish()

        BlogPage.objects.all().delete()
        parent_page = BlogListPage.objects.last()
        for i in range(NUM_BLOG_POSTS):
            print("Creating blog post", i)
            title = fake.sentence()
            model_data = {
                "title": title,
                "slug": slugify(title),
                "main_image_id": random.choice(images).id,
                "search_description": fake.sentence(),
                "owner_id": u.id,
                "body": json.dumps(
                    [
                        get_para(),
                        get_img(),
                        get_para(),
                        get_heading(),
                        get_para(),
                        get_quote(),
                        get_para(),
                        get_img(),
                        get_para(),
                    ]
                ),
            }
            blog = BlogPage(**model_data)
            parent_page.add_child(instance=blog)
            blog.save_revision().publish()


def get_wagtail_image():
    print("Downloading a new image from unsplash...")
    width, height = (1280, 720)
    url = "https://source.unsplash.com/random/{w}x{h}".format(w=width, h=height)
    r = requests.get(url, stream=True)
    r.raise_for_status()
    img_bytes = r.content
    filename = "{}.jpg".format(hashlib.sha256(img_bytes).hexdigest())
    django_image = ImageFile(BytesIO(img_bytes), name=filename)
    return WagtailImage.objects.create(title=filename, file=django_image)
