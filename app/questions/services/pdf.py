import weasyprint
from django.template.loader import render_to_string

from questions.models import FileUpload, ImageUpload


def create_pdf(submission):
    """
    Returns a PDF file string.
    """
    # Get questions from sections
    fields = {}
    for section in submission.questions:
        for form in section["forms"]:
            for field in form["fields"]:
                fs = field.get("fields", [field])
                for f in fs:
                    fields[f["name"]] = f

    # Pull out image and answers
    images = []
    docs = []
    answers = []
    for answer in submission.answers:
        answer, name = answer.get("answer", ""), answer.get("name", "")
        field = fields[name]
        if field["type"] == "FILE":
            image_ids = []
            doc_ids = []
            for file in answer:
                if "image" in file:
                    image_ids.append(file["id"])
                elif "file" in file:
                    doc_ids.append(file["id"])

            if image_ids:
                images += [
                    image_upload.image
                    for image_upload in ImageUpload.objects.filter(
                        pk__in=image_ids
                    ).all()
                ]
            if doc_ids:
                docs += [
                    file_upload.file
                    for file_upload in FileUpload.objects.filter(pk__in=doc_ids).all()
                ]
        else:
            answers.append(
                {
                    "name": name.lower().replace("_", " ").capitalize(),
                    "prompt": field.get("prompt", ""),
                    "answers": answer if type(answer) is list else [answer],
                }
            )

    context = {
        "submission": submission,
        "answers": answers,
        "images": images,
        "docs": docs,
    }
    pdf_html_str = render_to_string("client-intake.html", context=context)
    pdf_bytes = weasyprint.HTML(string=pdf_html_str).write_pdf()
    return pdf_bytes
