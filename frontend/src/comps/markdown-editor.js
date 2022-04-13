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

export const MarkdownTextArea = (props) => {
  const [html, setHtml] = useState("");
  useEffect(() => {
    if (props.value) {
      setHtml(markdownToHtml(props.value));
    } else {
      setHtml("");
    }
  }, [props.value]);
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
      <TextArea {...props} />
      <div
        style={{ padding: "0 1em" }}
        dangerouslySetInnerHTML={{ __html: html }}
      />
    </>
  );
};
