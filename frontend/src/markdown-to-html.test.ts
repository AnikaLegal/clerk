import { describe, expect, it } from 'vitest'
import { markdownToHtml } from './markdown-to-html'

describe('markdownToHtml', () => {
  it('renders a fenced code block as a paragraph keeping its line breaks', () => {
    const html = markdownToHtml(
      'Before\n\n```js\nfirst line\nsecond line\n```\n\nAfter'
    )
    expect(html).not.toContain('<pre')
    expect(html).not.toContain('<code')
    expect(html).toContain('<p>first line<br />\nsecond line</p>')
  })

  it('renders an indented paragraph as a plain paragraph', () => {
    const html = markdownToHtml('Before\n\n    indented text\n\nAfter')
    expect(html).toBe('<p>Before</p>\n<p>indented text</p>\n<p>After</p>')
  })

  it('keeps code block text escaped and sanitised', () => {
    const html = markdownToHtml('```\n<script>alert(1)</script>\n```')
    expect(html).not.toContain('<script>')
    expect(html).toContain('&lt;script&gt;')
  })

  it('leaves inline code alone', () => {
    expect(markdownToHtml('Use `this`')).toBe('<p>Use <code>this</code></p>')
  })
})
