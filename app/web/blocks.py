from wagtail.blocks import StructBlock, CharBlock, ChoiceBlock
from django.utils.text import slugify



class AttributedQuoteBlock(StructBlock):
    quote = CharBlock()
    source = CharBlock()

    class Meta:
        icon = "openquote"
        template = "web/blocks/attributed-quote.html"
        label = "Attributed Quote"


class HeadingSizeChoiceBlock(ChoiceBlock):
    choices = [
        ("h2", "H2"),
        ("h3", "H3"),
        ("h4", "H4"),
        ("h5", "H5"),
        ("h6", "H6"),
    ]


class HeadingBlock(StructBlock):
    """
    Custom `StructBlock` that allows the user to select the size for headers
    """

    title = CharBlock(required=True)
    size = HeadingSizeChoiceBlock(required=True, default="h2")
    anchor_target = CharBlock(required=False)

    class Meta:
        icon = "title"
        template = "web/blocks/heading_block.html"

    def clean(self, value):
        value["anchor_target"] = slugify(value.get("title"))
        return super().clean(value)
