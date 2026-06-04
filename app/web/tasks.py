import io
import logging

import pypdfium2 as pdfium
from django.core.files.base import ContentFile
from web.models.impact import Impact, ImpactImage

logger = logging.getLogger(__name__)


def extract_impact_pages(impact_pk: int) -> None:
    """Extract pages from a PDF specified in an Impact instance and save them as
    ImpactImage instances.

    Triggered as a background task after an Impact instance is saved with a
    changed PDF or page range.
    """

    try:
        impact = Impact.objects.get(pk=impact_pk)
    except Impact.DoesNotExist:
        logger.error("Impact with pk=%s does not exist.", impact_pk)
        return

    impact.images.all().delete()
    try:
        with impact.pdf.file.open() as pdf_file:
            pdf_bytes = pdf_file.read()
    except Exception:
        logger.exception("Failed to read PDF file for Impact pk=%s", impact_pk)
        return

    try:
        doc = pdfium.PdfDocument(pdf_bytes)
    except Exception:
        logger.exception("Failed to open PDF for Impact pk=%s", impact_pk)
        return

    start_page = impact.page_range_start or 1
    end_page = impact.page_range_end or len(doc)
    if start_page < 1 or end_page > len(doc) or start_page > end_page:
        logger.error(
            "Invalid page range for Impact pk=%s: start=%s, end=%s, total_pages=%s",
            impact_pk,
            start_page,
            end_page,
            len(doc),
        )
        return

    for page_idx in range(start_page - 1, end_page):
        try:
            page = doc[page_idx]
            bitmap = page.render()
            pil_image = bitmap.to_pil()

            buffer = io.BytesIO()
            pil_image.save(buffer, format="PNG")
            buffer.seek(0)

            img = ImpactImage(impact=impact, page_number=page_idx + 1)
            img.image.save(
                f"impact-{impact.pk}-page-{page_idx + 1}.png",
                ContentFile(buffer.read()),
                save=True,
            )
        except Exception:
            logger.exception(
                "Failed to extract page %s for Impact pk=%s",
                page_idx + 1,
                impact_pk,
            )

    logger.info(
        "Extracted %d pages for Impact pk=%s",
        end_page - start_page + 1,
        impact_pk,
    )
