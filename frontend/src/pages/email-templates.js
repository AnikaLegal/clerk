import React, { useState, useEffect, useRef } from "react";
import { mount, debounce } from "utils";
import {
  Button,
  Container,
  Header,
  Table,
  Input,
  Dropdown,
} from "semantic-ui-react";

const CONTEXT = window.reactContext;
const TOPIC_OPTIONS = [
  { key: "REPAIRS", value: "REPAIRS", text: "Repairs" },
  { key: "BONDS", value: "BONDS", text: "Bonds" },
  { key: "EVICTION", value: "EVICTION", text: "Eviction" },
];

const debouncer = debounce(300);

const httpGet = (query, url) => {
  const qs = new URLSearchParams(query).toString();
  const queryUrl = `${url}?${qs}`;
  const config = {
    method: "GET",
    headers: { "Content-Type": "application/json" },
  };
  return fetch(queryUrl, config)
    .then((response) => response.json())
    .catch((err) => {
      console.error("Error when fetching search results:", err.message);
    });
};

const App = () => {
  const [templates, setTemplates] = useState(CONTEXT.templates);
  const [name, setName] = useState("");
  const [topic, setTopic] = useState("");
  const search = debouncer(() =>
    httpGet({ name, topic }, CONTEXT.search_url).then((data) => {
      setTemplates(data);
    })
  );
  const isFirstUpdate = useRef(true);
  useEffect(() => {
    if (isFirstUpdate.current) {
      isFirstUpdate.current = false;
    } else {
      search();
    }
  }, [name, topic]);

  return (
    <Container>
      <Header as="h1">Email Templates</Header>
      <a href={CONTEXT.create_url}>
        <Button primary>Create a new email template</Button>
      </a>
      <div
        style={{
          marginTop: "1rem",
          display: "grid",
          gap: "1rem",
          gridTemplateColumns: "1fr 1fr",
        }}
      >
        <Input
          icon="search"
          placeholder="Search by template name or subject..."
          value={name}
          onChange={(e) => setName(e.target.value)}
        />
        <Dropdown
          fluid
          selection
          placeholder="Select a case type"
          options={TOPIC_OPTIONS}
          onChange={(e, { value }) => setTopic(value)}
          value={topic}
        />
      </div>
      <Table celled>
        <Table.Header>
          <Table.Row>
            <Table.HeaderCell>Name</Table.HeaderCell>
            <Table.HeaderCell>Topic</Table.HeaderCell>
            <Table.HeaderCell>Subject</Table.HeaderCell>
            <Table.HeaderCell>Created At</Table.HeaderCell>
          </Table.Row>
        </Table.Header>
        <Table.Body>
          {templates.length < 1 && (
            <Table.Row>
              <td>No templates found</td>
            </Table.Row>
          )}
          {templates.map((t) => (
            <Table.Row key={t.url}>
              <Table.Cell>
                <a href={t.url}>{t.name}</a>
              </Table.Cell>
              <Table.Cell>{t.topic}</Table.Cell>
              <Table.Cell>{t.subject}</Table.Cell>
              <Table.Cell>{t.created_at}</Table.Cell>
            </Table.Row>
          ))}
        </Table.Body>
      </Table>
    </Container>
  );
};

mount(App);
