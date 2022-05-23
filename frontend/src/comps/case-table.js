import React from "react";
import { Icon, Table } from "semantic-ui-react";

// TODO: Make more generic - whitelist of fields to be rendered passed in a props?
export const CaseListTable = ({ issues }) => (
  <Table celled={true}>
    <Table.Header>
      <Table.Row>
        <Table.HeaderCell>File Ref</Table.HeaderCell>
        <Table.HeaderCell>Topic</Table.HeaderCell>
        <Table.HeaderCell>Paralegal</Table.HeaderCell>
        <Table.HeaderCell>Lawyer</Table.HeaderCell>
        <Table.HeaderCell>Created</Table.HeaderCell>
        <Table.HeaderCell>Stage</Table.HeaderCell>
        <Table.HeaderCell>Advice</Table.HeaderCell>
        <Table.HeaderCell>Outcome</Table.HeaderCell>
      </Table.Row>
    </Table.Header>
    <Table.Body>
      {issues.map((issue) => (
        <Table.Row key={issue.id}>
          <Table.Cell>
            <a href={issue.url}>{issue.fileref}</a>
          </Table.Cell>
          <Table.Cell>{issue.topic_display}</Table.Cell>
          <Table.Cell>
            <a href={issue.paralegal.url}>{issue.paralegal.full_name}</a>
          </Table.Cell>
          <Table.Cell>
            <a href={issue.lawyer.url}>{issue.lawyer.full_name}</a>
          </Table.Cell>
          <Table.Cell>{issue.created_at}</Table.Cell>
          <Table.Cell>{issue.stage_display || "-"}</Table.Cell>
          <Table.Cell>
            {issue.provided_legal_services ? (
              <Icon name="check" color="green" />
            ) : (
              <Icon name="close" color="yellow" />
            )}
          </Table.Cell>
          <Table.Cell>{issue.outcome_display || "-"}</Table.Cell>
        </Table.Row>
      ))}
    </Table.Body>
  </Table>
);
