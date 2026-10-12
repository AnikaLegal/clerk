import { Converter, ShowdownExtension } from 'showdown'
import xss, { OnTagAttrHandler } from 'xss'

/* Code blocks mean nothing to our users, and markdown also treats any 4-space
 * indented text as one. Rendered as <pre> they keep their whitespace and
 * overflow their container, so show them as plain paragraphs that keep their
 * line breaks instead.
 */
const unwrapCodeBlocks: ShowdownExtension = {
  type: 'output',
  filter: (html) =>
    html.replace(
      /<pre><code[^>]*>([\s\S]*?)<\/code><\/pre>/g,
      (_, text: string) =>
        `<p>${text.replace(/\n+$/, '').replace(/\n/g, '<br />\n')}</p>`
    ),
}

const converter = new Converter({ extensions: [unwrapCodeBlocks] })

/* It is safe to allow the HTML class attribute. See
 * https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html#safe-sinks
 * We allow this for styling.
 */
const ignoreTagAttrHandler: OnTagAttrHandler = (tag, name, value) => {
  if (name == 'class') {
    return `${name}="${value}"`
  }
}

export const markdownToHtml = (markdownText) => {
  const html = converter.makeHtml(markdownText)
  // Sanitise HTML removing <script> tags and the like.
  return xss(html, { onIgnoreTagAttr: ignoreTagAttrHandler })
}
