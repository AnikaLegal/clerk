import React from "react";
import { Container, Header, Card } from "semantic-ui-react";
import xss from "xss";

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
    <div className="email-list">
      {emails.map((email) => (
        <Card fluid key={email.id}>
          {email.state == "DRAFT" && (
            <div className="ui top attached primary label">Draft</div>
          )}
          {email.state == "SENT" && (
            <div className="ui top attached teal label">
              Sent on {email.created_at} by by {email.sender.full_name}
            </div>
          )}
          {email.state == "INGESTED" && (
            <div className="ui top attached orange label">
              Received on {email.created_at}
            </div>
          )}
          {email.state == "READY_TO_SEND" && (
            <div className="ui top attached primary label">Sending...</div>
          )}
          <Card.Content>
            <Card.Header>{email.subject || "(no subject)"}</Card.Header>
            <Card.Meta>
              From {email.from_address} to {email.to_address}
            </Card.Meta>
            {email.cc_addresses.length > 0 && (
              <Card.Meta>
                Also sent to {email.cc_addresses.join(", ")}
              </Card.Meta>
            )}
            <Card.Description
              dangerouslySetInnerHTML={{ __html: xss(email.html) }}
            />
          </Card.Content>
          {email.attachments.length > 0 && (
            <Card.Content extra>
              <h5>Attached files</h5>
              <div
                style={{
                  display: "flex",
                  flexDirection: "column",
                  gap: "1em",
                }}
              >
                {email.attachments.map((a) => (
                  <Attachment {...a} key={a.id} />
                ))}
              </div>
            </Card.Content>
          )}
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
        </Card>
      ))}
    </div>
  </Container>
);

const Attachment = ({ url, is_image, name }) => (
  <a href={url}>
    {is_image ? (
      <img
        src={url}
        style={{
          maxHeight: "200px",
          maxWidth: "200px",
          objectFit: "contain",
        }}
      />
    ) : (
      name
    )}
  </a>
);

mount(App);
