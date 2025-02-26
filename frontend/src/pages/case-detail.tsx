import React, { useState } from 'react'
import {
  Checkbox,
  Container,
  Dropdown,
  Feed,
  Header,
  List,
  Segment,
} from 'semantic-ui-react'

import { getFormSchema } from 'comps/auto-form'
import { FIELD_TYPES } from 'comps/field-component'
import { TableForm } from 'comps/table-form'
import { useSnackbar } from 'notistack'
import * as Yup from 'yup'

import {
  Issue,
  IssueUpdate,
  TenancyCreate,
  useGetCaseQuery,
  useGetPeopleQuery,
  useUpdateCaseMutation,
  useUpdateTenancyMutation,
} from 'api'
import { CASE_TABS, CaseHeader, CaseTabUrls } from 'comps/case-header'
import { TimelineNote } from 'comps/timeline-item'
import { URLS } from 'consts'
import {
  AssignForm,
  CloseForm,
  ConflictForm,
  EligibilityForm,
  FilenoteForm,
  OutcomeForm,
  PerformanceForm,
  ProgressForm,
  ReopenForm,
  ReviewForm,
  ServiceForm,
} from 'forms'
import { CaseDetailFormProps, CaseFormChoices } from 'types/case'
import { UserInfo } from 'types/global'
import { getAPIErrorMessage, mount } from 'utils'

interface DjangoContext {
  case_pk: string
  choices: CaseFormChoices
  urls: CaseTabUrls
  user: UserInfo
}

const {
  case_pk,
  choices,
  urls,
  user: permissions,
} = (window as any).REACT_CONTEXT as DjangoContext

const App = () => {
  const { enqueueSnackbar } = useSnackbar()
  const [activeFormId, setActiveFormId] = useState(null)
  const [showSystemNotes, setShowSystemNotes] = useState(true)
  const [_updateTenancy, updateTenancyResult] = useUpdateTenancyMutation()
  const [_updateCase, updateCaseResult] = useUpdateCaseMutation()

  const caseResult = useGetCaseQuery({ id: case_pk })

  const ActiveForm = activeFormId ? CASE_FORMS[activeFormId] : null
  const isInitialLoad = caseResult.isLoading
  const isIssueLoading = caseResult.isFetching || updateCaseResult.isLoading
  const isTenancyLoading = updateTenancyResult.isLoading

  if (isInitialLoad) return null

  const issue = caseResult.data!.issue
  const tenancy = caseResult.data!.tenancy
  const notes = caseResult.data?.notes ?? []
  const details = getSubmittedDetails(issue)

  const filteredNotes = notes
    .filter((note) => note.note_type !== 'EMAIL')
    .filter((note) => showSystemNotes || note.note_type !== 'EVENT')

  const updateTenancy = (tenancyCreate: TenancyCreate) => {
    _updateTenancy({ id: tenancy.id, tenancyCreate })
      .unwrap()
      .then(() => {
        enqueueSnackbar('Updated tenancy', { variant: 'success' })
      })
      .catch((err) => {
        enqueueSnackbar(getAPIErrorMessage(err, 'Failed to update tenancy'), {
          variant: 'error',
        })
      })
  }

  const updateCase = (issueUpdate: IssueUpdate) => {
    _updateCase({ id: issue.id, issueUpdate })
      .unwrap()
      .then(() => {
        enqueueSnackbar('Updated case', { variant: 'success' })
      })
      .catch((err) => {
        enqueueSnackbar(getAPIErrorMessage(err, 'Failed to update case'), {
          variant: 'error',
        })
      })
  }

  const onRemoveLandlord = () => {
    if (confirm('Remove the landlord for this case?')) {
      updateTenancy({ landlord_id: null } as any)
    }
  }
  const onRemoveAgent = () => {
    if (confirm('Remove the agent for this case?')) {
      updateTenancy({ agent_id: null } as any)
    }
  }
  const onRemoveSupportWorker = () => {
    if (confirm('Remove the support worker for this case?')) {
      updateCase({ support_worker_id: null } as any)
    }
  }

  const onAddAgent = (agentId) => {
    updateTenancy({ agent_id: agentId } as any)
  }
  const onAddLandlord = (landlordId) => {
    updateTenancy({ landlord_id: landlordId } as any)
  }
  const onAddSupportWorker = (supportWorkerId) => {
    updateCase({ support_worker_id: supportWorkerId } as any)
  }

  return (
    <Container>
      <CaseHeader issue={issue} activeTab={CASE_TABS.DETAIL} urls={urls} />
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
              choices={choices}
              issue={issue}
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
                  ['Preferred name']: issue.client.preferred_name ?? '',
                  Email: issue.client.email,
                  Phone: issue.client.phone_number,
                  Age: issue.client.age,
                  Gender: issue.client.gender ?? '',
                  Pronouns: issue.client.pronouns ?? '',
                }}
              />
              <EntityCard
                title="Tenancy"
                url={tenancy.url}
                tableData={{
                  ['Street address']: tenancy.address,
                  Suburb: `${tenancy.suburb} ${tenancy.postcode}`,
                  Started: tenancy.started ?? '',
                  ['Client on lease?']: tenancy.is_on_lease
                    ? tenancy.is_on_lease.display
                    : '',
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
                  isLoading={isTenancyLoading}
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
                  isLoading={isTenancyLoading}
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
                  isLoading={isIssueLoading}
                />
              )}
              <CurrentCircumstancesCard
                initialIssue={issue}
                updateCase={_updateCase}
              />
              <OtherInformationCard
                initialIssue={issue}
                updateCase={_updateCase}
              />
              <EntityCard title="Other submitted data" tableData={details} />
            </React.Fragment>
          )}
        </div>
      </div>
    </Container>
  )
}

interface PersonSearchCardProps {
  title: string
  createUrl: string
  onSelect: (val: any) => void
  isLoading: boolean
}

const PersonSearchCard: React.FC<PersonSearchCardProps> = ({
  title,
  createUrl,
  onSelect,
  isLoading,
}) => {
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
          loading={isFetching || isLoading}
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
  tableData: { [key: string]: string | number }
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
              <td className="four wide">
                {title[0].toUpperCase() + title.slice(1).toLowerCase()}
              </td>
              <td>{text}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  </div>
)

const CurrentCircumstancesCard = ({ initialIssue, updateCase }) => {
  const fields = [
    {
      label: 'Weekly rent',
      schema: Yup.number().integer().min(0).nullable(),
      type: FIELD_TYPES.NUMBER,
      name: 'weekly_rent',
    },
    {
      label: 'Employment status',
      schema: Yup.array().of(Yup.string()).required('Required'),
      type: FIELD_TYPES.MULTI_CHOICE,
      name: 'employment_status',
    },
    {
      label: 'Weekly income',
      name: 'weekly_income',
      schema: Yup.number().integer().min(0).nullable(),
      type: FIELD_TYPES.NUMBER,
    },
  ]

  return (
    <TableFormCard
      header="Current circumstances"
      fields={fields}
      initialIssue={initialIssue}
      updateCase={updateCase}
    />
  )
}

const OtherInformationCard = ({ initialIssue, updateCase }) => {
  const fields = [
    {
      label: 'Referrer type',
      type: FIELD_TYPES.SINGLE_CHOICE,
      name: 'referrer_type',
    },
    {
      label: 'Referrer',
      name: 'referrer',
      type: FIELD_TYPES.TEXT,
      schema: Yup.string(),
    },
  ]

  return (
    <TableFormCard
      header="Other information"
      fields={fields}
      initialIssue={initialIssue}
      updateCase={updateCase}
    />
  )
}

const TableFormCard = ({ header, fields, initialIssue, updateCase }) => {
  const [issue, setIssue] = useState<Issue>(initialIssue)
  const update = (id: string, values: { [fieldName: string]: unknown }) =>
    updateCase({
      id: issue.id,
      issueUpdate: values as IssueUpdate,
    }).unwrap()

  const schema = getFormSchema(fields)

  return (
    <div className="ui card fluid">
      <div className="content">
        <Header as="h3">{header}</Header>
        <TableForm
          fields={fields}
          schema={schema}
          model={issue}
          setModel={setIssue}
          modelName="case"
          onUpdate={update}
        />
      </div>
    </div>
  )
}

const CASE_FORMS: { [name: string]: React.FC<CaseDetailFormProps> } = {
  filenote: FilenoteForm,
  review: ReviewForm,
  performance: PerformanceForm,
  conflict: ConflictForm,
  eligibility: EligibilityForm,
  assign: AssignForm,
  progress: ProgressForm,
  service: ServiceForm,
  close: CloseForm,
  reopen: ReopenForm,
  outcome: OutcomeForm,
}

interface CaseFormOption {
  id: string
  icon: string
  text: string
  when: (perms: UserInfo, issue: Issue) => boolean
}

const CASE_FORM_OPTIONS: CaseFormOption[] = [
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
    when: (perms, issue) => perms.is_coordinator_or_better && !!issue.paralegal,
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
    id: 'service',
    icon: 'balance scale',
    text: 'Add a service',
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

const getSubmittedDetails = (issue: Issue): { [key: string]: string } =>
  Object.entries(issue.answers).reduce((obj, [k, v]) => {
    if (!v) return obj
    // Chop off first part of title
    const title = correctCase(k.split('_').slice(1).join('_'))
    // Handle answers that are lists of answers
    const answer = (Array.isArray(v) ? v : [v]).map(correctCase).join(', ')
    return { ...obj, [title]: answer }
  }, {})

const correctCase = (str: any): string =>
  String(str)
    .split('_')
    .map((s) => {
      const lowered = s.toLowerCase()
      return lowered[0].toUpperCase() + lowered.slice(1)
    })
    .join(' ')

mount(App)
