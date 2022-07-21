import React from 'react'
import { Icon, Table } from 'semantic-ui-react'

export const CaseListTable = ({ issues, fields }) => {
  const selectedFields = FIELDS.filter((f) => fields.includes(f.name))
  return (
    <Table celled={true}>
      <Table.Header>
        <Table.Row>
          {selectedFields.map((f) => (
            <Table.HeaderCell key={f.name}>{f.label}</Table.HeaderCell>
          ))}
        </Table.Row>
      </Table.Header>
      <Table.Body>
        {issues.length > 0 &&
          issues.map((issue) => (
            <Table.Row key={issue.id}>
              {selectedFields.map((f) => (
                <Table.Cell key={`${issue.id}-${f.name}`}>
                  {f.getValue(issue)}
                </Table.Cell>
              ))}
            </Table.Row>
          ))}
        {issues.length == 0 && (
          <Table.Row>
            <Table.Cell>No cases found</Table.Cell>
          </Table.Row>
        )}
      </Table.Body>
    </Table>
  )
}
const FIELDS = [
  {
    name: 'fileref',
    label: 'File Ref',
    getValue: (issue) => <a href={issue.url}>{issue.fileref}</a>,
  },
  { name: 'topic', label: 'Topic', getValue: (issue) => issue.topic_display },
  {
    name: 'client',
    label: 'Client',
    getValue: (issue) => (
      <a href={issue.client.url}>{issue.client.full_name}</a>
    ),
  },

  {
    name: 'paralegal',
    label: 'Paralegal',
    getValue: (issue) =>
      issue.paralegal ? (
        <a href={issue.paralegal.url}>{issue.paralegal.full_name}</a>
      ) : (
        '-'
      ),
  },
  {
    name: 'lawyer',
    label: 'Lawyer',
    getValue: (issue) =>
      issue.lawyer ? (
        <a href={issue.lawyer.url}>{issue.lawyer.full_name}</a>
      ) : (
        '-'
      ),
  },
  {
    name: 'created_at',
    label: 'Created',
    getValue: (issue) => issue.created_at,
  },
  {
    name: 'stage',
    label: 'Stage',
    getValue: (issue) => issue.stage_display || '-',
  },
  {
    name: 'provided_legal_services',
    label: 'Advice',
    getValue: (issue) =>
      issue.provided_legal_services ? (
        <Icon name="check" color="green" />
      ) : (
        <Icon name="close" color="yellow" />
      ),
  },
  {
    name: 'outcome',
    label: 'Outcome',
    getValue: (issue) => issue.outcome_display || '-',
  },
]
