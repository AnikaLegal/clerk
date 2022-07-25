import React, { useState, useEffect } from "react";
import { Formik } from "formik";
import { Header, Segment, Tab } from "semantic-ui-react";

import { MarkdownAsHtmlDisplay } from "utils";

export const CASE_TABS = {
  DETAIL: "DETAIL",
  EMAIL: "EMAIL",
  DOCUMENTS: "DOCUMENTS",
};

export const CaseHeader = ({ issue, actionstepUrl, activeTab, urls }) => (
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
        {actionstepUrl && <a href={actionstepUrl}>view in Actionstep</a>}
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
      {issue.client.notes && (
        <div className="ui segment padded">
          <div className="ui top attached label">Client notes</div>
          <MarkdownAsHtmlDisplay markdown={issue.client.notes} />
        </div>
      )}
    </span>
    <div className="ui top attached tabular menu">
      <a
        href={urls.detail}
        className={`item ${activeTab === CASE_TABS.DETAIL ? "active" : ""}`}
      >
        <i className="clipboard outline icon"></i>
        Details
      </a>
      <a
        href={urls.email}
        className={`item ${activeTab === CASE_TABS.EMAIL ? "active" : ""}`}
      >
        <i className="envelope outline icon"></i>
        Email
      </a>
      <a
        href={urls.docs}
        className={`item ${activeTab === CASE_TABS.DOCUMENTS ? "active" : ""}`}
      >
        <i className="folder open outline icon"></i>
        Documents
      </a>
    </div>
  </>
);
