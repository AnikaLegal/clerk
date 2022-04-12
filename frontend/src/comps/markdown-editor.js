import React, { useEffect, useState } from "react";
import { Form, Segment } from "semantic-ui-react";
import { Converter, setFlavor } from "showdown";
import xss from "xss";

import { TextArea } from "comps/textarea";

const converter = new Converter();
setFlavor("github");

const convert = (text) => {
  const html = converter.makeHtml(text);
  const sanitisedHtml = xss(html);
  return sanitisedHtml;
};

export const MarkdownEditor = ({
  text,
  html,
  onChangeText,
  onChangeHtml,
  disabled,
}) => {
  useEffect(() => {
    if (text) {
      onChangeHtml(convert(text));
    }
  }, []);

  const onTextAreaChange = (e) => {
    onChangeText(e.target.value);
    onChangeHtml(convert(e.target.value));
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
      setHtml(convert(props.value));
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
