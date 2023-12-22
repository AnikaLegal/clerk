import React, { useState, useEffect } from 'react'
import {
  Container,
  Header,
  Dropdown,
  Segment,
  List,
  Feed,
  Checkbox,
} from 'semantic-ui-react'

import { useGetPeopleQuery, Tenancy } from 'apiNew'
import { TimelineNote } from 'comps/timeline-item'
import { CaseHeader, CASE_TABS } from 'comps/case-header'
import { mount } from 'utils'
import { api } from 'api'
import { URLS } from 'consts'
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
} from 'forms'

import { IssueDetail, IssueNote } from 'types'

interface ReactContext {
  issue: IssueDetail
  notes: IssueNote[]
  tenancy: Tenancy
  details: { [title: string]: string }
  actionstep_url: string
  urls: {
    detail: string
    email: string
    docs: string
  }
  permissions: {
    is_paralegal_or_better: boolean
    is_coordinator_or_better: boolean
  }
}

const REACT_CONTEXT = (window as any).REACT_CONTEXT as ReactContext

const { details, urls, actionstep_url, permissions } = REACT_CONTEXT

const App = () => {
  const [issue, setIssue] = useState(REACT_CONTEXT.issue)
  const [notes, setNotes] = useState(REACT_CONTEXT.notes)
  const [tenancy, setTenancy] = useState(REACT_CONTEXT.tenancy)
  const [activeFormId, setActiveFormId] = useState(null)
  const [showSystemNotes, setShowSystemNotes] = useState(true)

  const filteredNotes = notes
    .filter((note) => note.note_type !== 'EMAIL')
    .filter((note) => showSystemNotes || note.note_type !== 'EVENT')

  const setSupportWorker = (supportWorker) =>
    setIssue({ ...issue, support_worker: supportWorker })

  const onRemoveLandlord = () => {
    if (confirm('Remove the landlord for this case?')) {
      api.case.landlord
        .remove(issue.id)
        .then(({ data }) => setTenancy(data as Tenancy))
    }
  }
  const onRemoveAgent = () => {
    if (confirm('Remove the agent for this case?')) {
      api.case.agent
        .remove(issue.id)
        .then(({ data }) => setTenancy(data as Tenancy))
    }
  }
  const onRemoveSupportWorker = () => {
    if (confirm('Remove the support worker for this case?')) {
      api.case.supportWorker.remove(issue.id).then(() => setSupportWorker(null))
    }
  }

  const onAddAgent = (agentId) => {
    api.case.agent
      .add(issue.id, agentId)
      .then(({ data }) => setTenancy(data as Tenancy))
  }
  const onAddLandlord = (landlordId) => {
    api.case.landlord
      .add(issue.id, landlordId)
      .then(({ data }) => setTenancy(data as Tenancy))
  }
  const onAddSupportWorker = (supportWorkerId) => {
    api.case.supportWorker
      .add(issue.id, supportWorkerId)
      .then(({ data }) => setSupportWorker(data))
  }

  const ActiveForm = activeFormId ? CASE_FORMS[activeFormId] : null
  return (
    <Container>
      <CaseHeader
        issue={issue}
        actionstepUrl={actionstep_url}
        activeTab={CASE_TABS.DETAIL}
        urls={urls}
      />
      <div className="ui two column grid" style={{ marginTop: '1rem' }}>
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

          <div
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              margin: '1.5em 0 1em 0',
            }}
          >
            <Header as="h2" style={{ margin: 0 }}>
              Timeline
            </Header>
            <Checkbox
              label="Show system notes"
              checked={showSystemNotes}
              onChange={(e, { checked }) => setShowSystemNotes(checked)}
            />
          </div>

          {filteredNotes.length < 1 && <Feed>No notes yet</Feed>}
          {filteredNotes.map((note) => (
            <TimelineNote note={note} key={note.id} />
          ))}
        </div>
        <div className="column">
          {activeFormId && (
            <ActiveForm
              issue={issue}
              setIssue={setIssue}
              setNotes={setNotes}
              onCancel={() => setActiveFormId(null)}
            />
          )}
          {!activeFormId && (
            <React.Fragment>
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
                  ['Street Address']: tenancy.address,
                  Suburb: `${tenancy.suburb} ${tenancy.postcode}`,
                  Started: tenancy.started,
                  ['Client on lease']: tenancy.is_on_lease ? tenancy.is_on_lease.display : "",
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
                    Phone: tenancy.landlord.phone_number,
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
                    Phone: tenancy.agent.phone_number,
                  }}
                />
              ) : (
                <PersonSearchCard
                  title="Add an agent"
                  createUrl={URLS.PERSON.CREATE}
                  onSelect={onAddAgent}
                />
              )}
              {issue.support_worker ? (
                <EntityCard
                  title="Support Worker"
                  onRemove={onRemoveSupportWorker}
                  url={issue.support_worker.url}
                  tableData={{
                    Name: issue.support_worker.full_name,
                    Address: issue.support_worker.address,
                    Email: issue.support_worker.email,
                    Phone: issue.support_worker.phone_number,
                  }}
                />
              ) : (
                <PersonSearchCard
                  title="Add a support worker"
                  createUrl={URLS.PERSON.CREATE}
                  onSelect={onAddSupportWorker}
                />
              )}
              <EntityCard title="Other submitted data" tableData={details} />
            </React.Fragment>
          )}
        </div>
      </div>
    </Container>
  )
}

const PersonSearchCard = ({ title, createUrl, onSelect }) => {
  const { data, isFetching } = useGetPeopleQuery()
  const people = data || []
  return (
    <div className="ui card fluid">
      <div className="content">
        <h2 className="header">
          {title}
          <a style={{ fontWeight: 'normal', float: 'right' }} href={createUrl}>
            create
          </a>
        </h2>
        <Dropdown
          fluid
          search
          selection
          loading={isFetching}
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
  )
}

interface EntityCardProps {
  title: string
  tableData: any
  url?: string
  onRemove?: () => void
}

const EntityCard: React.FC<EntityCardProps> = ({
  title,
  url,
  onRemove,
  tableData,
}) => (
  <div className="ui card fluid">
    <div className="content">
      <h2 className="header">
        {url ? <a href={url}>{title}</a> : title}
        {onRemove && (
          <a
            style={{ fontWeight: 'normal', float: 'right' }}
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
)

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
}

const CASE_FORM_OPTIONS = [
  {
    id: 'filenote',
    icon: 'clipboard outline',
    text: 'Add a file note',
    when: (perms, issue) => perms.is_paralegal_or_better,
  },
  {
    id: 'review',
    icon: 'clipboard outline',
    text: 'Add a coordinator case review note',
    when: (perms, issue) => perms.is_coordinator_or_better,
  },
  {
    id: 'performance',
    icon: 'clipboard outline',
    text: 'Add a paralegal performance review note',
    when: (perms, issue) => perms.is_coordinator_or_better && issue.paralegal,
  },
  {
    id: 'conflict',
    icon: 'search',
    text: 'Record a conflict check',
    when: (perms, issue) => perms.is_paralegal_or_better,
  },
  {
    id: 'eligibility',
    icon: 'search',
    text: 'Record an eligibility check',
    when: (perms, issue) => perms.is_paralegal_or_better,
  },
  {
    id: 'assign',
    icon: 'graduation cap',
    text: 'Assign a paralegal to the case',
    when: (perms, issue) => perms.is_coordinator_or_better,
  },
  {
    id: 'progress',
    icon: 'chart line',
    text: 'Progress the case status',
    when: (perms, issue) => perms.is_paralegal_or_better && issue.is_open,
  },
  {
    id: 'close',
    icon: 'times circle outline',
    text: 'Close the case',
    when: (perms, issue) => perms.is_coordinator_or_better && issue.is_open,
  },
  {
    id: 'reopen',
    icon: 'check',
    text: 'Re-open the case',
    when: (perms, issue) => perms.is_coordinator_or_better && !issue.is_open,
  },
  {
    id: 'outcome',
    icon: 'undo',
    text: 'Edit case outcome',
    when: (perms, issue) => perms.is_coordinator_or_better && !issue.is_open,
  },
]

mount(App)
