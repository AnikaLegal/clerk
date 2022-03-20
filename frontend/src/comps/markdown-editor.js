import React, { useEffect, useState, useRef } from "react";
import { Form, Segment } from "semantic-ui-react";
import { Converter, setFlavor } from "showdown";

const converter = new Converter();
setFlavor("github");

export const MarkdownEditor = ({ text, html, onChangeText, onChangeHtml }) => {
  const textAreaRef = useRef(null);
  const setScrollHeight = () => {
    const el = textAreaRef.current;
    if (el) {
      el.style.height = el.scrollHeight;
    }
  };
  useEffect(() => {
    if (text) {
      setScrollHeight();
      onChangeHtml(converter.makeHtml(text));
    }
  }, []);

  const onTextAreaChange = (e) => {
    onChangeText(e.target.value);
    onChangeHtml(converter.makeHtml(e.target.value));
    setScrollHeight();
  };
  return (
    <div style={{ padding: "1em 0" }}>
      <Segment secondary>
        Emails can be formatted using Markdown. See&nbsp;
        <a
          href="https://www.markdownguide.org/cheat-sheet/#basic-syntax"
          target="_blank"
          rel="noopener noreferrer"
        >
          here
        </a>
        &nbsp;for a basic reference.
      </Segment>
      <div
        style={{
          display: "grid",
          gap: "2em",
          paddingTop: "1em",
          gridTemplateColumns: "1fr 1fr",
        }}
      >
        <textarea
          ref={textAreaRef}
          placeholder="Dear Ms Example..."
          onChange={onTextAreaChange}
          rows={12}
          style={{
            overflow: "hidden",
            resize: "none !important",
            minHeight: "240px",
          }}
          value={text}
        />
        <Form.Field>
          <div dangerouslySetInnerHTML={{ __html: html }} />
        </Form.Field>
      </div>
    </div>
  );
};
