import React from 'react'
import { Icon, Table } from 'semantic-ui-react'
import { Issue } from 'api'
import moment from 'moment'

interface CaseListTableProps {
  issues: Issue[]
  fields: string[]
}

export const CaseListTable: React.FC<CaseListTableProps> = ({
  issues,
  fields,
}) => {
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
                <Table.Cell
                  key={`${issue.id}-${f.name}`}
                  className={f.getColor ? f.getColor(issue) : ''}
                >
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

const getNextReviewColor = (issue: Issue): string => {
  const now = moment()
  if (!issue.next_review) return ''
  const nextReviewMoment = moment(issue.next_review, 'DD/MM/YY')
  const days = nextReviewMoment.diff(now, 'days')
  if (days >= 7) {
    return ''
  } else if (days >= 3) {
    return 'green'
  } else if (days >= 2) {
    return 'yellow'
  } else if (days >= 0) {
    return 'orange'
  } else {
    return 'red'
  }
}

interface TableField {
  name: string
  label: string
  getValue: (issue: Issue) => any
  getColor?: (issue: Issue) => string
}

const FIELDS: TableField[] = [
  {
    name: 'fileref',
    label: 'File ref',
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
    name: 'next_review',
    label: 'Next review due',
    getValue: (issue) => issue.next_review || '-',
    getColor: getNextReviewColor,
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
    label: 'Advice?',
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
  {
    name: 'is_conflict_check',
    label: 'Conflict check performed?',
    getValue: (issue) =>
      issue.is_conflict_check ? (
        <Icon name="check" color="green" />
      ) : (
        <Icon name="close" color="yellow" />
      ),
  },
  {
    name: 'is_eligibility_check',
    label: 'Eligibility check performed?',
    getValue: (issue) =>
      issue.is_eligibility_check ? (
        <Icon name="check" color="green" />
      ) : (
        <Icon name="close" color="yellow" />
      ),
  },
]
