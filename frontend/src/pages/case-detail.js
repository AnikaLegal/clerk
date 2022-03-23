import React from "react";
import { Formik } from "formik";
import { Container, Header } from "semantic-ui-react";

import { mount } from "utils";
import { api } from "api";

const { issue, tenancy, details, urls, file_urls, image_urls } =
  window.REACT_CONTEXT;

const App = () => (
  <Container>
    <CaseHeader issue={issue} />
    <CaseTabMenu />
    <div className="ui two column grid" style={{ marginTop: "1rem" }}>
      <div className="column"></div>
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

const EntityCard = ({ title, url, onRemove, tableData }) => (
  <div className="ui card fluid">
    <div className="content">
      <h2 className="header">
        {url ? <a href={url}>{title}</a> : title}
        {onRemove && (
          <a style="font-weight: normal;float: right" onClick={onRemove}>
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

const CaseHeader = ({ issue }) => (
  <>
    <Header as="h1">
      {issue.topic} case for {issue.client.full_name} ({issue.fileref})
      <div className="sub header">
        Created {issue.created_at}
        <br />
        {issue.paralegal ? (
          <span>
            Assigned to&nbsp;
            <a href={issue.paralegal.url}>{issue.paralegal.full_name},</a>&nbsp;
          </span>
        ) : (
          "Not assigned,"
        )}
        {issue.lawyer ? (
          <span>
            supervised by&nbsp;
            <a href={issue.lawyer.url}>{issue.lawyer.full_name}</a>&nbsp;
          </span>
        ) : (
          "not supervised"
        )}
        {issue.actionstep_url ? (
          <a href="{issue.actionstep_url}">view in Actionstep</a>
        ) : (
          "(Actionstep link not available)"
        )}
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
          <div className="detail">{issue.stage}</div>
        ) : (
          <div className="detail">-</div>
        )}
      </div>

      <div className="ui grey label">
        Outcome
        {issue.outcome ? (
          <div className="detail">{issue.outcome}</div>
        ) : (
          <div className="detail">-</div>
        )}
      </div>
      {!issue.is_open && issue.outcome_notes && (
        <div className="ui segment padded">
          <div className="ui top attached label green">Outcome notes</div>
          <p style="margin-bottom: 0">{issue.outcome_notes}</p>
        </div>
      )}
    </span>
  </>
);

mount(App);
