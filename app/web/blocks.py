from wagtail.core.blocks import StructBlock, CharBlock


class AttributedQuoteBlock(StructBlock):
    quote = CharBlock()
    source = CharBlock()

    class Meta:
        icon = "openquote"
        template = "web/blocks/attributed-quote.html"
        label = "Attributed Quote"
