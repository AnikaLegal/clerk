import os
from typing import NotRequired, TypedDict

from django.contrib.staticfiles import finders
from django.core import management
from django.core.files.base import File
from django.db import migrations
from django.utils import timezone
from wagtail.utils.file import hash_filelike


class BaseDocument(TypedDict):
    title: str
    description: str
    is_featured: NotRequired[bool]


class BlogPageDocument(BaseDocument):
    blog_slug: str


class FileDocument(BaseDocument):
    file_name: str
    accessible_file_name: NotRequired[str]


Document = BlogPageDocument | FileDocument


documents: list[Document] = [
    {
        "title": "Financial Report 2018-2019",
        "description": "See an overview of our finances.",
        "file_name": "financial-report-2018-2019.pdf",
    },
    {
        "title": "Annual Report 2019-2020",
        "description": "Read about the work we did in our first year of operation.",
        "file_name": "Anika-Legal-Annual-Report-2019-2020.pdf",
    },
    {
        "title": "Financial Report 2020-2021",
        "description": "See an overview of our finances.",
        "file_name": "Anika-Legal-Financial-Report-2021.pdf",
    },
    {
        "title": "Annual Report 2020-2021",
        "description": "Read about the work we've done over 2020-2021.",
        "file_name": "Anika-Legal-Annual-Report-2020-2021.pdf",
    },
    {
        "title": "Financial Report 2021-2022",
        "description": "See an overview of our finances.",
        "file_name": "Anika-Legal-Financial-Report-2022.pdf",
    },
    {
        "title": "Annual Report 2021-2022",
        "description": "Read about the work we've done over the 2021-2022.",
        "file_name": "Anika-Legal-Annual-Report-2021-2022.pdf",
    },
    {
        "title": "Repairing rental homes (2022)",
        "description": "Why self-enforcement fails tenants.",
        "file_name": "Anika-Legal-Repairs-Report.pdf",
    },
    {
        "title": "Strategic Plan 2023-2025",
        "description": "Read about our plans for the future.",
        "file_name": "Anika-Legal-3Y-Strategic-Plan-FY23-25.pdf",
    },
    {
        "title": "Annual Report 2022-2023",
        "description": "Read about the work we've done over the last year.",
        "file_name": "Anika-Legal-Annual-Report-2022-2023.pdf",
        "accessible_file_name": "Anika-Legal-Annual-Report-2022-2023.docx",
    },
    {
        "title": "Anika Legal submission to the Victorian Rental Inquiry (July 2023)",
        "description": "Anika Legal submission to the Inquiry into the Rental and Affordability Crisis in Victoria.",
        "file_name": "Anika-Legal-Submission-to-the-Victorian-Rental-Inquiry.pdf",
    },
    {
        "title": "Anika Legal submission to the Federal Rental Inquiry (August 2023)",
        "description": "Anika Legal submission to the Inquiry into the Worsening Rental Crisis in Australia.",
        "file_name": "Anika-Legal-Submission-to-the-Federal-Rental-Inquiry.pdf",
    },
    {
        "title": "Access to Justice & Technology Network submission to the NLAP Review (October 2023)",
        "description": "Access to Justice & Technology Network submission to the Independent Review of the National Legal Assistance Partnership (2020-2025) regarding the role of technology in addressing unmet legal need.",
        "file_name": "Access-to-Justice-and-Technology-Network-NLAP-Review-Submission.pdf",
    },
    {
        "title": "FY23 Special Purpose Financial Report",
        "description": "See an overview of our finances.",
        "file_name": "Anika-Legal-FY23-Special-Purpose-Financial-Report.pdf",
    },
    {
        "title": "Impact Report",
        "description": "Read about the problems we solve and how we solve them, the people we help and our impact to date.",
        "file_name": "Anika-Legal-Impact-Report.pdf",
    },
    {
        "title": "Broken Bonds",
        "description": "Our Broken Bonds report explores the experiences of renters facing unfair bond claims.",
        "blog_slug": "broken-bonds",
    },
    {
        "title": "FY24 Special Purpose Financial Report",
        "description": "See an overview of our finances.",
        "file_name": "Anika-Legal-FY24-Special-Purpose-Financial-Report.pdf",
    },
    {
        "title": "Too Hot, Too Cold, Too Costly",
        "description": "We've delved deep into the data surrounding energy inefficiency and its impact on Victorian renters.",
        "blog_slug": "report-too-hot-too-cold-too-costly",
        "is_featured": True,
    },
    {
        "title": "Annual Report 2023-2024",
        "description": "Read about the work we've done over the last year.",
        "file_name": "Anika-Legal-Annual-Report-2023-2024.pdf",
    },
]


def _get_static_file(file_name: str) -> File:
    file_path = os.path.join("web", "docs", file_name)
    path = finders.find(file_path)
    if not isinstance(path, str):
        raise FileNotFoundError(f"Could not find static file: {file_path}")
    return File(open(path, "rb"), name=os.path.basename(path))


def _populate_report_db(apps, schema_editor):
    if os.environ.get("PYTEST_CURRENT_TEST"):
        return

    BlogPage = apps.get_model("web", "BlogPage")
    if BlogPage.objects.count() == 0:
        # A heuristic to avoid running this migration in situations where it
        # would fail e.g. if we are resetting the database and running all
        # migrations from scratch.
        return

    Report = apps.get_model("web", "Report")
    Document = apps.get_model("web", "CustomDocument")

    for document in documents:
        if "blog_slug" in document:
            blog_page = BlogPage.objects.get(slug=document["blog_slug"])
            report = Report(blog_page=blog_page)
        else:
            file = _get_static_file(document["file_name"])
            if "accessible_file_name" in document:
                accessible_file = _get_static_file(document["accessible_file_name"])
            else:
                accessible_file = None

            report = Report(
                document=Document.objects.create(
                    title=document["title"],
                    file=file,
                    file_size=file.size,
                    file_hash=hash_filelike(file),
                ),
            )
            if accessible_file:
                report.accessible_document = Document.objects.create(
                    title=f"Accessible version of {document['title']}",
                    file=accessible_file,
                    file_size=accessible_file.size,
                    file_hash=hash_filelike(accessible_file),
                )

        report.title = document["title"]
        report.description = document["description"]
        report.is_featured = document.get("is_featured", False)
        report.first_published_at = timezone.now()
        report.save()

    # Rebuild the references index so documents reference the newly created
    # reports.
    management.call_command("rebuild_references_index")


class Migration(migrations.Migration):
    dependencies = [
        ("web", "0031_migrate_documents"),
    ]

    operations = [
        migrations.RunPython(
            _populate_report_db, reverse_code=migrations.RunPython.noop
        ),
    ]
