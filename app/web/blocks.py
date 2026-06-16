from wagtail.blocks import (
    CharBlock,
    ListBlock,
    RichTextBlock,
    StructBlock,
)
from wagtail_link_block.blocks import LinkBlock


class AttributedQuoteBlock(StructBlock):
    quote = CharBlock()
    source = CharBlock()

    class Meta:
        icon = "openquote"
        template = "web/blocks/attributed-quote.html"
        label = "Attributed Quote"


class AccordionItemBlock(StructBlock):
    title = CharBlock()
    content = RichTextBlock()

    class Meta:
        icon = "help"
        label = "Accordion Item"


class AccordionBlock(StructBlock):
    items = ListBlock(AccordionItemBlock())

    class Meta:
        icon = "list-ul"
        template = "web/blocks/accordion.html"
        label = "Accordion"


class LinkButtonBlock(StructBlock):
    text = CharBlock()
    link = LinkBlock()

    class Meta:
        icon = "pick"
        template = "web/blocks/link-button.html"
        label = "Link Button"
