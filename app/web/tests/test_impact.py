from unittest.mock import MagicMock, patch

import pytest
from auditlog.models import LogEntry
from django.core.exceptions import ValidationError
from django.db.models.fields.files import FieldFile
from django.urls import reverse
from web.factories import ImpactFactory, ImpactImageFactory
from web.models import Impact
from web.signals import post_log_impact
from web.tasks import extract_impact_pages


@pytest.mark.django_db
def test_impact_only_one_live():
    """
    Saving a new live Impact demotes any previously live Impact.
    """
    first = ImpactFactory(live=True)
    second = ImpactFactory(live=True)

    first.refresh_from_db()
    second.refresh_from_db()

    assert not first.live
    assert second.live
    assert Impact.objects.filter(live=True).count() == 1


@pytest.mark.django_db
def test_impact_draft_does_not_demote_live():
    """
    Saving a draft (live=False) Impact does not affect the current live Impact.
    """
    live = ImpactFactory(live=True)
    ImpactFactory(live=False)

    live.refresh_from_db()
    assert live.live
    assert Impact.objects.filter(live=True).count() == 1


@pytest.mark.django_db
def test_impact_view_with_live_impact(client):
    """
    The impact view passes the live Impact to the template context.
    """
    impact = ImpactFactory(live=True)
    ImpactImageFactory(impact=impact, page_number=1)
    ImpactImageFactory(impact=impact, page_number=2)

    response = client.get(reverse("impact"))

    assert response.status_code == 200
    assert response.context["impact"] == impact
    assert list(response.context["impact"].images.all()) == list(impact.images.all())


@pytest.mark.django_db
def test_impact_view_with_no_live_impact(client):
    """
    The impact view passes None to the template context when no live Impact exists.
    """
    ImpactFactory(live=False)

    response = client.get(reverse("impact"))

    assert response.status_code == 200
    assert response.context["impact"] is None


@pytest.mark.django_db
def test_impact_view_returns_most_recent_live(client):
    """
    When multiple Impacts exist, only the most-recent live one is returned.
    """
    ImpactFactory(live=True)
    latest = ImpactFactory(live=True)

    response = client.get(reverse("impact"))

    assert response.status_code == 200
    assert response.context["impact"] == latest


# ---------------------------------------------------------------------------
# Impact.clean() validation
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_impact_clean_no_range_passes():
    """
    clean() does not raise when page_range_start and page_range_end are both None.
    """
    impact = ImpactFactory.build(page_range_start=None, page_range_end=None)
    impact.clean()  # should not raise


@pytest.mark.django_db
def test_impact_clean_valid_range_passes():
    """
    clean() does not raise for a valid start/end range.
    """
    impact = ImpactFactory.build(page_range_start=2, page_range_end=5)
    impact.clean()  # should not raise


@pytest.mark.django_db
def test_impact_clean_start_page_below_one():
    """
    clean() raises ValidationError when page_range_start is 0.
    """
    impact = ImpactFactory.build(page_range_start=0)
    with pytest.raises(ValidationError) as exc_info:
        impact.clean()
    assert "page_range_start" in exc_info.value.message_dict


@pytest.mark.django_db
def test_impact_clean_end_before_start():
    """
    clean() raises ValidationError when page_range_end < page_range_start.
    """
    impact = ImpactFactory.build(page_range_start=5, page_range_end=3)
    with pytest.raises(ValidationError) as exc_info:
        impact.clean()
    assert "page_range_end" in exc_info.value.message_dict


@pytest.mark.django_db
def test_impact_clean_end_equals_start_passes():
    """
    clean() does not raise when page_range_end == page_range_start.
    """
    impact = ImpactFactory.build(page_range_start=3, page_range_end=3)
    impact.clean()  # should not raise


# ---------------------------------------------------------------------------
# post_log_impact signal
# ---------------------------------------------------------------------------


def _make_mock_impact():
    mock_impact = MagicMock(spec=Impact)
    mock_impact.pk = 99
    return mock_impact


@pytest.mark.django_db
def test_signal_create_schedules_task(django_capture_on_commit_callbacks):
    """
    A CREATE audit log entry triggers async_task via transaction.on_commit.
    """
    mock_impact = _make_mock_impact()
    with patch("web.signals.async_task") as mock_async:
        with django_capture_on_commit_callbacks(execute=True):
            post_log_impact(
                sender=Impact,
                instance=mock_impact,
                action=LogEntry.Action.CREATE,
                changes={},
            )
    mock_async.assert_called_once_with(extract_impact_pages, mock_impact.pk)


@pytest.mark.django_db
@pytest.mark.parametrize("changed_field", ["pdf", "page_range_start", "page_range_end"])
def test_signal_update_trigger_field_schedules_task(
    changed_field, django_capture_on_commit_callbacks
):
    """
    An UPDATE entry touching any of the trigger fields schedules the task.
    """
    mock_impact = _make_mock_impact()
    with patch("web.signals.async_task") as mock_async:
        with django_capture_on_commit_callbacks(execute=True):
            post_log_impact(
                sender=Impact,
                instance=mock_impact,
                action=LogEntry.Action.UPDATE,
                changes={changed_field: [None, 1]},
            )
    mock_async.assert_called_once_with(extract_impact_pages, mock_impact.pk)


@pytest.mark.django_db
def test_signal_update_non_trigger_field_does_not_schedule(
    django_capture_on_commit_callbacks,
):
    """
    An UPDATE entry that only touches 'title' does not schedule the task.
    """
    mock_impact = _make_mock_impact()
    with django_capture_on_commit_callbacks(execute=False) as callbacks:
        post_log_impact(
            sender=Impact,
            instance=mock_impact,
            action=LogEntry.Action.UPDATE,
            changes={"title": ["old", "new"]},
        )
    assert len(callbacks) == 0


@pytest.mark.django_db
def test_signal_delete_does_not_schedule(django_capture_on_commit_callbacks):
    """
    A DELETE audit log entry does not schedule the task.
    """
    mock_impact = _make_mock_impact()
    with django_capture_on_commit_callbacks(execute=False) as callbacks:
        post_log_impact(
            sender=Impact,
            instance=mock_impact,
            action=LogEntry.Action.DELETE,
            changes={},
        )
    assert len(callbacks) == 0


# ---------------------------------------------------------------------------
# extract_impact_pages task
# ---------------------------------------------------------------------------


def _make_doc_mock(n_pages=3, fail_page_idx=None):
    """Return a pdfium PdfDocument mock with n_pages pages.

    If fail_page_idx is given, accessing that page index raises RuntimeError.
    """
    mock_pil = MagicMock()
    mock_pil.save.side_effect = lambda buf, **kwargs: buf.write(b"\x89PNG\r\n\x1a\n")

    def get_page(idx):
        if fail_page_idx is not None and idx == fail_page_idx:
            raise RuntimeError("simulated page render failure")
        page = MagicMock()
        page.render.return_value.to_pil.return_value = mock_pil
        return page

    mock_doc = MagicMock()
    mock_doc.__len__ = MagicMock(return_value=n_pages)
    mock_doc.__getitem__ = MagicMock(side_effect=get_page)
    return mock_doc


@pytest.mark.django_db
def test_extract_impact_pages_nonexistent_pk(caplog):
    """
    extract_impact_pages logs an error and returns when the pk does not exist.
    """
    extract_impact_pages(99999)
    assert "does not exist" in caplog.text


@pytest.mark.django_db
def test_extract_impact_pages_file_read_failure(caplog):
    """
    extract_impact_pages logs an exception when the PDF file cannot be opened.
    """
    impact = ImpactFactory()
    with patch.object(FieldFile, "open", side_effect=OSError("disk error")):
        extract_impact_pages(impact.pk)
    assert "Failed to read PDF" in caplog.text
    assert impact.images.count() == 0


@pytest.mark.django_db
def test_extract_impact_pages_invalid_pdf(caplog):
    """
    extract_impact_pages logs an exception when pdfium cannot parse the file.
    """
    impact = ImpactFactory()
    with patch("web.tasks.pdfium.PdfDocument", side_effect=Exception("bad pdf")):
        extract_impact_pages(impact.pk)
    assert "Failed to open PDF" in caplog.text
    assert impact.images.count() == 0


@pytest.mark.django_db
def test_extract_impact_pages_invalid_page_range(caplog):
    """
    extract_impact_pages logs an error when the page range exceeds the document.
    """
    impact = ImpactFactory(page_range_start=1, page_range_end=10)
    mock_doc = _make_doc_mock(n_pages=3)
    with patch("web.tasks.pdfium.PdfDocument", return_value=mock_doc):
        extract_impact_pages(impact.pk)
    assert "Invalid page range" in caplog.text
    assert impact.images.count() == 0


@pytest.mark.django_db
def test_extract_impact_pages_creates_images():
    """
    extract_impact_pages creates one ImpactImage per page in the requested range.
    """
    impact = ImpactFactory(page_range_start=2, page_range_end=4)
    mock_doc = _make_doc_mock(n_pages=5)
    with patch("web.tasks.pdfium.PdfDocument", return_value=mock_doc):
        extract_impact_pages(impact.pk)

    images = list(impact.images.order_by("page_number"))
    assert len(images) == 3
    assert [img.page_number for img in images] == [2, 3, 4]


@pytest.mark.django_db
def test_extract_impact_pages_defaults_full_range():
    """
    When page_range_start/end are None, all pages of the document are extracted.
    """
    impact = ImpactFactory(page_range_start=None, page_range_end=None)
    mock_doc = _make_doc_mock(n_pages=4)
    with patch("web.tasks.pdfium.PdfDocument", return_value=mock_doc):
        extract_impact_pages(impact.pk)

    assert impact.images.count() == 4


@pytest.mark.django_db
def test_extract_impact_pages_clears_existing_images():
    """
    Stale ImpactImage records are deleted before re-extraction begins,
    even when the subsequent PDF processing fails.
    """
    impact = ImpactFactory()
    ImpactImageFactory(impact=impact, page_number=1)
    ImpactImageFactory(impact=impact, page_number=2)
    assert impact.images.count() == 2

    # Force a failure after the delete step by providing invalid PDF content.
    with patch("web.tasks.pdfium.PdfDocument", side_effect=Exception("bad pdf")):
        extract_impact_pages(impact.pk)

    assert impact.images.count() == 0


@pytest.mark.django_db
def test_extract_impact_pages_page_failure_skips_page(caplog):
    """
    A failure extracting a single page is logged, but remaining pages are still processed.
    """
    impact = ImpactFactory(page_range_start=1, page_range_end=3)
    # Page index 1 (page number 2) will fail.
    mock_doc = _make_doc_mock(n_pages=3, fail_page_idx=1)
    with patch("web.tasks.pdfium.PdfDocument", return_value=mock_doc):
        extract_impact_pages(impact.pk)

    assert "Failed to extract page" in caplog.text
    # Pages 1 and 3 should still be saved.
    saved_pages = set(impact.images.values_list("page_number", flat=True))
    assert saved_pages == {1, 3}
