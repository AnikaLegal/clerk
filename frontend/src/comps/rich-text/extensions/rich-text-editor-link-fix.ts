import Link from '@tiptap/extension-link'
import { MultiToken, tokenize } from 'linkifyjs'

export const CustomLink = Link.extend({
    addCommands() {
        return {
            ...this.parent?.(),
            /* The tiptap link extension uses a default protocol if a link is
             * entered without a protocol. This does not happen for links entered
             * via the mantine RichTextEditor.Link component (we use in this in
             * the bubble menu of the rich text area component). This addition to
             * the existing link extension addresses this issue. */
            setLink: attributes => ({ chain }) => {
                const tokens: Array<ReturnType<MultiToken['toObject']>> = tokenize(attributes.href).map(t => t.toObject(this.options.defaultProtocol))
                if (tokens.length == 1 && tokens[0].isLink) {
                    attributes.href = tokens[0].href
                }
                return chain().setMark(this.name, attributes).setMeta('preventAutolink', true).run()
            },
        }
    },
})
