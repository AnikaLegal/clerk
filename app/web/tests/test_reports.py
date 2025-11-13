import pytest
from django.core.exceptions import ValidationError
from web.factories import BlogPageFactory, DocumentFactory, ReportFactory
from web.models import Report


@pytest.mark.django_db
def test_report_validate_only_one_of_document_or_blog_supplied():
    """
    Validate that a report must have either a document or a blog page, but not
    both or neither.
    """
    with pytest.raises(ValidationError):
        ReportFactory(
            document=DocumentFactory(), blog_page=BlogPageFactory()
        ).full_clean()

    with pytest.raises(ValidationError):
        ReportFactory(document=None, blog_page=None).full_clean()

    ReportFactory(document=DocumentFactory(), blog_page=None).full_clean()
    ReportFactory(document=None, blog_page=BlogPageFactory()).full_clean()


@pytest.mark.django_db
def test_report_is_featured_is_singular():
    """
    Test that only one report is featured at a time.
    """
    ReportFactory(is_featured=True)
    ReportFactory(is_featured=False)
    report = ReportFactory(is_featured=True)

    assert Report.objects.count() == 3
    assert Report.objects.filter(is_featured=True).count() == 1
    assert Report.objects.get(is_featured=True) == report
