import React from "react";
import { Container, Header, Card } from "semantic-ui-react";
import xss from "xss";
import styled from "styled-components";

import { mount } from "utils";

const { issue, subject, emails, case_email_address, case_email_list_url } =
  window.REACT_CONTEXT;

const App = () => (
  <Container>
    <Header as="h1">
      {subject}
      <Header.Subheader>
        Most recent emails are at the top
        <br />
        <a href={case_email_list_url}>Back to case emails</a>
      </Header.Subheader>
    </Header>
    <EmailList>
      {emails.map((email) => (
        <Email key={email.id}>
          <EmailHeader>
            <p>
              <strong>To:</strong>&nbsp;
              {email.to_address}
            </p>
            <p>
              <strong>From:</strong>&nbsp;
              {email.from_address}
            </p>
            {email.cc_addresses.length > 0 && (
              <p>
                <strong>CC:</strong>&nbsp;
                {email.cc_addresses.join(", ")}
              </p>
            )}
            {email.state == "DRAFT" && <div className="label">Draft</div>}
            {email.state == "SENT" && (
              <div className="label">
                Sent on {email.created_at} by by {email.sender.full_name}
              </div>
            )}
            {email.state == "INGESTED" && (
              <div className="label">Received on {email.created_at}</div>
            )}
            {email.state == "READY_TO_SEND" && (
              <div className="label">Sending...</div>
            )}
          </EmailHeader>
          <EmailBody dangerouslySetInnerHTML={{ __html: xss(email.html) }} />
          <EmailControls>
            {email.state == "DRAFT" ? (
              <Card.Content extra>
                <a href={email.edit_url} className="header" target="_blank">
                  <button className="ui button primary">Edit Draft</button>
                </a>
              </Card.Content>
            ) : (
              <Card.Content extra>
                <a href={email.reply_url} className="header" target="_blank">
                  <button className="ui button">Reply</button>
                </a>
              </Card.Content>
            )}
          </EmailControls>
          {email.attachments.length > 0 && (
            <EmailAttachmentBlock>
              <h5>Attached files</h5>
              <EmailAttachmentList>
                {email.attachments.map((a) => (
                  <Attachment {...a} key={a.id} />
                ))}
              </EmailAttachmentList>
            </EmailAttachmentBlock>
          )}
        </Email>
      ))}
    </EmailList>
  </Container>
);

const Attachment = ({ url, is_image, name }) => {
  const filename = name.split("/").pop();
  return (
    <span>
      <a href={url}>{filename}</a> - <span>save to sharepoint</span>
    </span>
  );
};

const EmailList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  margin-top: 1.5rem;
`;

const Email = styled.div`
  border: 3px solid var(--grey);
`;
const EmailHeader = styled.div`
  background-color: var(--grey);
  padding: 1rem;
  border-bottom: solid 1px var(--grey);
  p {
    margin-bottom: 0;
  }
  position: relative;
  .label {
    position: absolute;
    right: 0;
    bottom: 0;
    padding: 1rem;
  }
`;
const EmailBody = styled.div`
  padding: 1rem;
  h1,
  h2,
  h3,
  h4,
  h5,
  p {
    font-size: 1rem !important;
    margin: 0 0 1em;
  }
`;
const EmailControls = styled.div`
  padding: 0 1rem 1rem 1rem;
`;
const EmailAttachmentBlock = styled.div`
  background-color: var(--grey);
  border-top: solid 1px var(--grey);
  padding: 1rem;
`;
const EmailAttachmentList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 0.5em;
`;

mount(App);
