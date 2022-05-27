import React, { useEffect, useState } from "react";
import { Form, Segment } from "semantic-ui-react";

import { TextArea } from "comps/textarea";
import { markdownToHtml } from "utils";

export const MarkdownExplainer = () => (
  <Segment secondary>
    Text can be formatted using Markdown. See&nbsp;
    <a
      href="https://www.markdownguide.org/cheat-sheet/#basic-syntax"
      target="_blank"
      rel="noopener noreferrer"
    >
      here
    </a>
    &nbsp;for a basic reference.
  </Segment>
);

export const MarkdownEditor = ({
  text,
  html,
  onChangeText,
  onChangeHtml,
  disabled,
}) => {
  useEffect(() => {
    if (text) {
      onChangeHtml(markdownToHtml(text));
    }
  }, []);

  const onTextAreaChange = (e) => {
    onChangeText(e.target.value);
    onChangeHtml(markdownToHtml(e.target.value));
  };
  return (
    <div style={{ padding: "1em 0" }}>
      <MarkdownExplainer />
      <div
        style={{
          display: "grid",
          gap: "2em",
          paddingTop: "1em",
          gridTemplateColumns: "1fr 1fr",
        }}
      >
        <TextArea
          placeholder="Dear Ms Example..."
          onChange={onTextAreaChange}
          disabled={disabled}
          rows={12}
          value={text}
        />
        <Form.Field>
          <div dangerouslySetInnerHTML={{ __html: html }} />
        </Form.Field>
      </div>
    </div>
  );
};

export const MarkdownTextArea = ({ value, ...props }) => {
  const [html, setHtml] = useState("");
  useEffect(() => {
    if (value) {
      setHtml(markdownToHtml(value));
    } else {
      setHtml("");
    }
  }, [value]);
  return (
    <>
      <Segment secondary>
        This text can be formatted using Markdown. See&nbsp;
        <a
          href="https://www.markdownguide.org/cheat-sheet/#basic-syntax"
          target="_blank"
          rel="noopener noreferrer"
        >
          here
        </a>
        &nbsp;for a basic reference.
      </Segment>
      <TextArea value={value} {...props} />
      <div
        style={{
          margin: "1em 0",
          padding: "1em",
          border: "1px solid rgba(34,36,38,.15)",
          borderRadius: "0.28571429rem",
        }}
        dangerouslySetInnerHTML={{
          __html: html || "<span style='opacity: 0.5'>Start typing...</span>",
        }}
      />
    </>
  );
};
