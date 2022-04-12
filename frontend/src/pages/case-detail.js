import React, { useState, useEffect } from "react";
import { Formik } from "formik";
import {
  Container,
  Header,
  Divider,
  Form,
  Button,
  Dropdown,
  Message,
  Segment,
  List,
  Feed,
} from "semantic-ui-react";
import { mount } from "utils";
import { api } from "api";
import { URLS } from "consts";
import {
  FilenoteForm,
  ReviewForm,
  ReopenForm,
  PerformanceForm,
  CloseForm,
  EligibilityForm,
  AssignForm,
  OutcomeForm,
  ProgressForm,
  ConflictForm,
} from "forms";

const { details, urls, file_urls, image_urls, actionstep_url, permissions } =
  window.REACT_CONTEXT;

const App = () => {
  const [issue, setIssue] = useState(window.REACT_CONTEXT.issue);
  const [notes, setNotes] = useState(window.REACT_CONTEXT.notes);
  const [tenancy, setTenancy] = useState(window.REACT_CONTEXT.tenancy);
  const [activeFormId, setActiveFormId] = useState(null);
  const onRemoveLandlord = () => {
    if (confirm("Remove the landlord for this case?")) {
      api.case.landlord.remove(issue.id).then(({ data }) => setTenancy(data));
    }
  };
  const onRemoveAgent = () => {
    if (confirm("Remove the agent for this case?")) {
      api.case.agent.remove(issue.id).then(({ data }) => setTenancy(data));
    }
  };
  const onAddAgent = (agentId) => {
    api.case.agent.add(issue.id, agentId).then(({ data }) => setTenancy(data));
  };
  const onAddLandlord = (landlordId) => {
    api.case.landlord
      .add(issue.id, landlordId)
      .then(({ data }) => setTenancy(data));
  };
  const ActiveForm = activeFormId ? CASE_FORMS[activeFormId] : null;
  return (
    <Container>
      <CaseHeader issue={issue} actionstep_url={actionstep_url} />
      <CaseTabMenu />
      <div className="ui two column grid" style={{ marginTop: "1rem" }}>
        <div className="column">
          <Segment>
            <List divided verticalAlign="middle" selection>
              {CASE_FORM_OPTIONS.filter((o) => o.when(permissions, issue)).map(
                ({ id, icon, text }) => (
                  <List.Item
                    active={id === activeFormId}
                    key={text}
                    onClick={() =>
                      id === activeFormId
                        ? setActiveFormId(null)
                        : setActiveFormId(id)
                    }
                  >
                    <List.Content>
                      <div className="header">
                        <i className={`${icon} icon`}></i>
                        {text}
                      </div>
                    </List.Content>
                  </List.Item>
                )
              )}
            </List>
          </Segment>
          {activeFormId && (
            <ActiveForm
              issue={issue}
              setIssue={setIssue}
              setNotes={setNotes}
              onCancel={() => setActiveFormId(null)}
            />
          )}

          <Header as="h2">Timeline</Header>
          {notes.length < 1 && <Feed>No notes yet</Feed>}
          {notes.map((note) => {
            const NoteElement = NOTE_TYPES[note.note_type];
            return <NoteElement key={note.id} {...note} />;
          })}
        </div>
        <div className="column">
          <EntityCard
            title="Client"
            url={issue.client.url}
            tableData={{
              Name: issue.client.full_name,
              Email: issue.client.email,
              Phone: issue.client.phone_number,
              Age: issue.client.age,
              Gender: issue.client.gender,
            }}
          />
          <EntityCard
            title="Tenancy"
            url={tenancy.url}
            tableData={{
              ["Street Address"]: tenancy.address,
              Suburb: `${tenancy.suburb} ${tenancy.postcode}`,
              Started: tenancy.started,
              ["Client on lease"]: tenancy.is_on_lease,
            }}
          />
          {tenancy.landlord ? (
            <EntityCard
              title="Landlord"
              url={tenancy.landlord.url}
              onRemove={onRemoveLandlord}
              tableData={{
                Name: tenancy.landlord.full_name,
                Address: tenancy.landlord.address,
                Email: tenancy.landlord.email,
                Phone: tenancy.landlord.phone,
              }}
            />
          ) : (
            <PersonSearchCard
              title="Add a landlord"
              createUrl={URLS.PERSON.CREATE}
              onSelect={onAddLandlord}
            />
          )}
          {tenancy.agent ? (
            <EntityCard
              title="Real estate agent"
              onRemove={onRemoveAgent}
              url={tenancy.agent.url}
              tableData={{
                Name: tenancy.agent.full_name,
                Address: tenancy.agent.address,
                Email: tenancy.agent.email,
                Phone: tenancy.agent.phone,
              }}
            />
          ) : (
            <PersonSearchCard
              title="Add an agent"
              createUrl={URLS.PERSON.CREATE}
              onSelect={onAddAgent}
            />
          )}
          <EntityCard title="Other submitted data" tableData={details} />
          {file_urls && (
            <>
              <h2 className="header">Submitted documents</h2>
              <table
                className="ui definition table small"
                style={{ marginBottom: "2rem" }}
              >
                <tbody>
                  {file_urls.map((url, idx) => (
                    <tr key={url}>
                      <td className="four wide">Document #{idx}</td>
                      <td>
                        <a href={url}>Open document</a>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </>
          )}
          {image_urls && (
            <>
              <h2 className="header">Submitted images</h2>
              {image_urls.map((url) => (
                <a href={url} key={url}>
                  <img
                    className="ui small rounded image"
                    src={url}
                    style={{ marginBottom: "1rem" }}
                  />
                </a>
              ))}
            </>
          )}
        </div>
      </div>
    </Container>
  );
};

const PersonSearchCard = ({ title, createUrl, onSelect }) => {
  const [isLoading, setIsLoading] = useState(true);
  const [people, setPeople] = useState([]);
  useEffect(() => {
    api.person.list().then(({ data }) => {
      setPeople(data);
      setIsLoading(false);
    });
  }, []);
  return (
    <div className="ui card fluid">
      <div className="content">
        <h2 className="header">
          {title}
          <a style={{ fontWeight: "normal", float: "right" }} href={createUrl}>
            create
          </a>
        </h2>
        <Dropdown
          fluid
          search
          selection
          loading={isLoading}
          placeholder="Select a person"
          options={people.map((p) => ({
            key: p.id,
            text: p.email ? `${p.full_name} (${p.email})` : p.full_name,
            value: p.id,
          }))}
          onChange={(e, { value }) => onSelect(value)}
        />
      </div>
    </div>
  );
};

const EntityCard = ({ title, url, onRemove, tableData }) => (
  <div className="ui card fluid">
    <div className="content">
      <h2 className="header">
        {url ? <a href={url}>{title}</a> : title}
        {onRemove && (
          <a
            style={{ fontWeight: "normal", float: "right" }}
            onClick={onRemove}
          >
            remove
          </a>
        )}
      </h2>
      <table className="ui definition table small">
        <tbody>
          {Object.entries(tableData).map(([title, text]) => (
            <tr key={title}>
              <td className="four wide">{title}</td>
              <td>{text}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  </div>
);

const CaseTabMenu = () => (
  <div className="ui top attached tabular menu">
    <a href={urls.detail} className="item active">
      <i className="clipboard outline icon"></i>
      Details
    </a>
    <a href={urls.email} className="item">
      <i className="envelope outline icon"></i>
      Email
    </a>
    <a href={urls.docs} className="item">
      <i className="folder open outline icon"></i>
      Documents
    </a>
  </div>
);

const CaseHeader = ({ issue, actionstep_url }) => (
  <>
    <Header as="h1">
      {issue.topic_display} case for {issue.client.full_name} ({issue.fileref})
      <div className="sub header">
        Created {issue.created_at}
        <br />
        {issue.paralegal ? (
          <span>
            Assigned to&nbsp;
            <a href={issue.paralegal.url}>{issue.paralegal.full_name},</a>
            &nbsp;
          </span>
        ) : (
          "Not assigned, "
        )}
        {issue.lawyer ? (
          <span>
            supervised by&nbsp;
            <a href={issue.lawyer.url}>{issue.lawyer.full_name}</a>&nbsp;
          </span>
        ) : (
          "not supervised "
        )}
        {actionstep_url && <a href="{actionstep_url}">view in Actionstep</a>}
      </div>
    </Header>
    <span id="case-status" hx-swap-oob="true">
      {issue.is_open ? (
        <div className="ui blue label">Case open</div>
      ) : (
        <div className="ui green label">Case closed</div>
      )}
      {issue.provided_legal_services ? (
        <div className="ui green label">Legal services provided</div>
      ) : (
        <div className="ui blue label">Legal services not provided</div>
      )}

      <div className="ui grey label">
        Stage
        {issue.stage ? (
          <div className="detail">{issue.stage_display}</div>
        ) : (
          <div className="detail">-</div>
        )}
      </div>

      <div className="ui grey label">
        Outcome
        {issue.outcome ? (
          <div className="detail">{issue.outcome_display}</div>
        ) : (
          <div className="detail">-</div>
        )}
      </div>
      {!issue.is_open && issue.outcome_notes && (
        <div className="ui segment padded">
          <div className="ui top attached label green">Outcome notes</div>
          <p style={{ marginBottom: 0 }}>{issue.outcome_notes}</p>
        </div>
      )}
    </span>
  </>
);

const TimelineItem = ({
  title,
  detail,
  content,
  label,
  bottomLabel,
  color,
}) => (
  <div className="ui segment padded">
    <div className={`ui top attached label ${color}`}>
      {title}
      <div className="detail">{detail}</div>
    </div>
    <p style={{ marginBottom: bottomLabel ? "1rem" : 0 }}>{content}</p>
    {label && (
      <div className={`ui top right attached label ${color}`}>{label}</div>
    )}
    {bottomLabel && (
      <div className="ui bottom right attached label">{bottomLabel}</div>
    )}
  </div>
);

const NOTE_TYPES = {
  PARALEGAL: (note) => (
    <TimelineItem
      title={note.creator.full_name}
      detail={note.created_at}
      content={note.text_display}
      label="File note"
      color="primary"
    />
  ),
  EVENT: (note) => (
    <TimelineItem
      title="Case Update"
      detail={note.created_at}
      content={note.text_display}
      color="primary"
    />
  ),
  ELIGIBILITY_CHECK_SUCCESS: (note) => (
    <TimelineItem
      title={
        <span>
          Eligibility check <strong>cleared</strong> by {note.creator.full_name}
        </span>
      }
      detail={note.created_at}
      content={note.text_display}
    />
  ),
  ELIGIBILITY_CHECK_FAILURE: (note) => (
    <TimelineItem
      title={
        <span>
          Eligibility check <strong>not cleared</strong> by{" "}
          {note.creator.full_name}
        </span>
      }
      detail={note.created_at}
      content={note.text_display}
    />
  ),
  CONFLICT_CHECK_SUCCESS: (note) => (
    <TimelineItem
      title={
        <span>
          Conflict check <strong>cleared</strong> by {note.creator.full_name}
        </span>
      }
      detail={note.created_at}
      content={note.text_display}
    />
  ),
  CONFLICT_CHECK_FAILURE: (note) => (
    <TimelineItem
      title={
        <span>
          Conflict check <strong>not cleared</strong> by{" "}
          {note.creator.full_name}
        </span>
      }
      detail={note.created_at}
      content={note.text_display}
    />
  ),
  REVIEW: (note) => (
    <TimelineItem
      title={note.creator.full_name}
      detail={note.created_at}
      content={note.text_display}
      label="Case review"
      color="orange"
      bottomLabel={<span>Next review {note.event}</span>}
    />
  ),
  PERFORMANCE: (note) => (
    <TimelineItem
      title={note.creator.full_name}
      detail={note.created_at}
      content={note.text_display}
      label="Performance review"
      color="teal"
      bottomLabel={
        <span>
          About&nbsp;
          <a href={note.reviewee.url}>{note.reviewee.full_name}</a>
        </span>
      }
    />
  ),
  EMAIL: (note) => null,
};

const CASE_FORMS = {
  filenote: FilenoteForm,
  review: ReviewForm,
  performance: PerformanceForm,
  conflict: ConflictForm,
  eligibility: EligibilityForm,
  assign: AssignForm,
  progress: ProgressForm,
  close: CloseForm,
  reopen: ReopenForm,
  outcome: OutcomeForm,
};

const CASE_FORM_OPTIONS = [
  {
    id: "filenote",
    icon: "clipboard outline",
    text: "Add a file note",
    when: (perms, issue) => perms.is_paralegal_or_better,
  },
  {
    id: "review",
    icon: "clipboard outline",
    text: "Add a coordinator case review note",
    when: (perms, issue) => perms.is_coordinator_or_better,
  },
  {
    id: "performance",
    icon: "clipboard outline",
    text: "Add a paralegal performance review note",
    when: (perms, issue) => perms.is_coordinator_or_better && issue.paralegal,
  },
  {
    id: "conflict",
    icon: "search",
    text: "Record a conflict check",
    when: (perms, issue) => perms.is_paralegal_or_better,
  },
  {
    id: "eligibility",
    icon: "search",
    text: "Record an eligibility check",
    when: (perms, issue) => perms.is_paralegal_or_better,
  },
  {
    id: "assign",
    icon: "graduation cap",
    text: "Assign a paralegal to the case",
    when: (perms, issue) => perms.is_coordinator_or_better,
  },
  {
    id: "progress",
    icon: "chart line",
    text: "Progress the case status",
    when: (perms, issue) => perms.is_paralegal_or_better && issue.is_open,
  },
  {
    id: "close",
    icon: "times circle outline",
    text: "Close the case",
    when: (perms, issue) => perms.is_coordinator_or_better && issue.is_open,
  },
  {
    id: "reopen",
    icon: "check",
    text: "Re-open the case",
    when: (perms, issue) => perms.is_coordinator_or_better && !issue.is_open,
  },
  {
    id: "outcome",
    icon: "undo",
    text: "Edit case outcome",
    when: (perms, issue) => perms.is_coordinator_or_better && !issue.is_open,
  },
];

mount(App);