import React, { useState, useEffect } from "react";
import {
  Button,
  Container,
  Header,
  Table,
  Input,
  Form,
  Pagination,
  Icon,
  Label,
  Dropdown,
} from "semantic-ui-react";

import { CaseListTable } from "comps/case-table";
import { mount, debounce, useEffectLazy } from "utils";
import { api } from "api";
import { FadeTransition } from "comps/transitions";

const CONTEXT = window.REACT_CONTEXT;
const TABLE_FIELDS = [
  "fileref",
  "topic",
  "client",
  "paralegal",
  "lawyer",
  "created_at",
  "stage",
  "provided_legal_services",
  "outcome",
];
const debouncer = debounce(300);

const App = () => {
  const [showAdvancedSearch, setShowAdvancedSearch] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingSelections, setIsLoadingSelections] = useState(true);
  const [issues, setIssues] = useState(CONTEXT.issues);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalIssues, setTotalIssues] = useState(CONTEXT.total_count);
  const [totalPages, setTotalPages] = useState(CONTEXT.total_pages);
  const [paralegals, setParalegals] = useState([]);
  const [lawyers, setLawyers] = useState([]);
  const [query, setQuery] = useState({
    search: "",
    topic: "",
    stage: "",
    outcome: "",
    is_open: "",
    paralegal: "",
    lawyer: "",
  });
  const onPageChange = (e, { activePage }) => setCurrentPage(activePage);
  const search = debouncer(() => {
    setIsLoading(true);
    api.case
      .search({ ...query, page: currentPage })
      .then(({ data: { issues, total_pages, total_count } }) => {
        setIssues(issues);
        setTotalPages(total_pages);
        setTotalIssues(total_count);
        setIsLoading(false);
      })
      .catch(() => setIsLoading(false));
  });
  useEffectLazy(() => search(), [query, currentPage]);
  useEffect(() => {
    api.accounts
      .search({ group: "Paralegal" })
      .then(({ resp, data }) => setParalegals(data))
      .then(() => api.accounts.search({ group: "Lawyer" }))
      .then(({ resp, data }) => setLawyers(data))
      .then(() => setIsLoadingSelections(false));
  }, []);
  return (
    <Container>
      <Header as="h1">
        Cases
        <Header.Subheader>
          Showing {issues.length} of {totalIssues} cases
        </Header.Subheader>
      </Header>
      <Form>
        <Form.Field>
          <Input
            placeholder="Find cases with the name or email of paralegals and clients, or by using the file ref"
            value={query.search}
            onChange={(e) => setQuery({ ...query, search: e.target.value })}
            loading={isLoading}
          />
        </Form.Field>
        {!showAdvancedSearch && (
          <Label
            style={{ cursor: "pointer" }}
            onClick={(e) => {
              e.preventDefault();
              setShowAdvancedSearch(true);
            }}
          >
            Advanced search
          </Label>
        )}
        {showAdvancedSearch && (
          <>
            <Label
              style={{ cursor: "pointer" }}
              onClick={(e) => {
                e.preventDefault();
                setShowAdvancedSearch(false);
              }}
            >
              Hide advanced search
            </Label>
            <Form.Group style={{ marginTop: "1em" }}>
              <Form.Field width={8}>
                <Dropdown
                  fluid
                  selection
                  clearable
                  value={query.is_open}
                  placeholder="Is case open?"
                  options={choiceToOptions(CONTEXT.choices.is_open)}
                  onChange={(e, { value }) =>
                    setQuery({ ...query, is_open: value })
                  }
                />
              </Form.Field>
              <Form.Field width={8}>
                <Dropdown
                  fluid
                  selection
                  clearable
                  value={query.stage || ""}
                  placeholder="Case stage"
                  options={choiceToOptions(CONTEXT.choices.stage)}
                  onChange={(e, { value }) =>
                    setQuery({ ...query, stage: value })
                  }
                />
              </Form.Field>
            </Form.Group>
            <Form.Group>
              <Form.Field width={8}>
                <Dropdown
                  fluid
                  selection
                  clearable
                  value={query.outcome || ""}
                  placeholder="Case outcome"
                  options={choiceToOptions(CONTEXT.choices.outcome)}
                  onChange={(e, { value }) =>
                    setQuery({ ...query, outcome: value })
                  }
                />
              </Form.Field>
              <Form.Field width={8}>
                <Dropdown
                  fluid
                  selection
                  clearable
                  value={query.topic || ""}
                  placeholder="Case topic"
                  options={choiceToOptions(CONTEXT.choices.topic)}
                  onChange={(e, { value }) =>
                    setQuery({ ...query, topic: value })
                  }
                />
              </Form.Field>
            </Form.Group>
            <Form.Group>
              <Form.Field width={8}>
                <Dropdown
                  fluid
                  selection
                  search
                  clearable
                  value={query.paralegal}
                  loading={isLoadingSelections}
                  placeholder="Select a paralegal"
                  options={paralegals.map((u) => ({
                    key: u.id,
                    value: u.id,
                    text: u.email,
                  }))}
                  onChange={(e, { value }) =>
                    setQuery({ ...query, paralegal: value })
                  }
                />
              </Form.Field>
              <Form.Field width={8}>
                <Dropdown
                  fluid
                  selection
                  search
                  clearable
                  value={query.lawyer}
                  loading={isLoadingSelections}
                  placeholder="Select a lawyer"
                  options={lawyers.map((u) => ({
                    key: u.id,
                    value: u.id,
                    text: u.email,
                  }))}
                  onChange={(e, { value }) =>
                    setQuery({ ...query, lawyer: value })
                  }
                />
              </Form.Field>
            </Form.Group>
          </>
        )}
      </Form>
      <FadeTransition in={!isLoading}>
        <CaseListTable issues={issues} fields={TABLE_FIELDS} />
      </FadeTransition>
      <Pagination
        activePage={currentPage}
        onPageChange={onPageChange}
        totalPages={totalPages}
        style={{ marginTop: "1em" }}
        ellipsisItem={{
          content: <Icon name="ellipsis horizontal" />,
          icon: true,
        }}
        firstItem={{ content: <Icon name="angle double left" />, icon: true }}
        lastItem={{ content: <Icon name="angle double right" />, icon: true }}
        prevItem={{ content: <Icon name="angle left" />, icon: true }}
        nextItem={{ content: <Icon name="angle right" />, icon: true }}
      />
    </Container>
  );
};

const choiceToOptions = (choices) =>
  choices.map(([value, label]) => ({
    key: label,
    text: label,
    value: value,
  }));

mount(App);
