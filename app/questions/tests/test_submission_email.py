from unittest import mock

import pytest

from questions.services.submission import send_submission_email
from questions.tests.factories import ImageUploadFactory, SubmissionFactory


@mock.patch("questions.services.submission.EmailMultiAlternatives")
@pytest.mark.django_db
def test_submission_email(mock_email_cls):
    image_upload_1 = ImageUploadFactory()
    image_upload_2 = ImageUploadFactory()
    answers = [
        {"name": "FOO", "answer": "yes"},  # Yes / no
        {"name": "BAR", "answer": ["red", "green"]},  # Multi select
        {"name": "BAZ", "answer": "yes"},  # Yes / no
        {"name": "BING", "answer": "yes"},  # Yes / no
        {
            "name": "FILES",
            "answer": [
                {"id": image_upload_1.id, "image": image_upload_1.image.name},
                {"id": image_upload_2.id, "image": image_upload_2.image.name},
            ],
        },
    ]
    sub = SubmissionFactory(complete=False, questions=QUESTIONS, answers=answers)
    mock_email = mock.MagicMock()
    mock_email_cls.return_value = mock_email

    send_submission_email(sub.pk)
    mock_email.send.assert_called_once_with(fail_silently=False)


QUESTIONS = [
    # Section with multiple forms
    {
        "name": "section 1",
        "forms": [
            # Form with multiple fields.
            {
                "name": "form 1",
                "prompt": "Form 1",
                "fields": [
                    # Typical field
                    {"name": "FOO", "type": "TEXT", "prompt": "What is foo?"},
                    # List field
                    {"name": "BAR", "type": "MULTI_SELECT", "prompt": "What is bar?"},
                    # Field of fields
                    {
                        "name": "GROUP",
                        "type": "FIELD_GROUP",
                        "prompt": "What is group?",
                        "fields": [
                            {"name": "BAZ", "type": "TEXT", "prompt": "What is baz?"},
                            {"name": "BING", "type": "TEXT", "prompt": "What is bing?"},
                        ],
                    },
                ],
            }
        ],
    },
    # Section with one form
    {
        "name": "section 2",
        "forms": [
            # Form with one field.
            {
                "name": "form 2",
                "prompt": "Form 1",
                "fields": [
                    # Image upload field
                    {"name": "FILES", "type": "FILE", "prompt": "Show us a picture of your dog?"}
                ],
            }
        ],
    },
]
