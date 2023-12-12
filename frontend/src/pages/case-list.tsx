import React, { useState } from 'react'
import {
  Container,
  Header,
  Input,
  Form,
  Pagination,
  Icon,
  Label,
  Dropdown,
} from 'semantic-ui-react'

import { api } from 'api'
import { CaseListTable } from 'comps/case-table'
import { mount, debounce, useEffectLazy } from 'utils'
import { FadeTransition } from 'comps/transitions'
import { Issue, useGetUsersQuery } from 'apiNew'

interface DjangoContext {
  issues: Issue[]
  next_page: number
  total_pages: number
  total_count: number
  prev_page: number
  choices: {
    stage: string[][]
    topic: string[][]
    outcome: string[][]
    is_open: string[][]
  }
}

const CONTEXT = (window as any).REACT_CONTEXT as DjangoContext

const TABLE_FIELDS = [
  'fileref',
  'topic',
  'client',
  'paralegal',
  'lawyer',
  'created_at',
  'stage',
  'provided_legal_services',
  'outcome',
]
const debouncer = debounce(300)

const App = () => {
  const [showAdvancedSearch, setShowAdvancedSearch] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [issues, setIssues] = useState(CONTEXT.issues)
  const [currentPage, setCurrentPage] = useState(1)
  const [totalIssues, setTotalIssues] = useState(CONTEXT.total_count)
  const [totalPages, setTotalPages] = useState(CONTEXT.total_pages)
  const [query, setQuery] = useState({
    search: '',
    topic: '',
    stage: '',
    outcome: '',
    is_open: '',
    paralegal: '',
    lawyer: '',
  })
  const onPageChange = (e, { activePage }) => setCurrentPage(activePage)
  const search = debouncer(() => {
    setIsLoading(true)
    api.case
      .search({ ...query, page: currentPage })
      .then(({ data: { issues, total_pages, total_count } }) => {
        setIssues(issues)
        setTotalPages(total_pages)
        setTotalIssues(total_count)
        setIsLoading(false)
      })
      .catch(() => setIsLoading(false))
  })
  useEffectLazy(() => search(), [query, currentPage])

  const paralegalResults = useGetUsersQuery({ group: 'Paralegal' })
  const lawyerResults = useGetUsersQuery({ group: 'Lawyer' })
  const isLoadingSelections =
    paralegalResults.isFetching || lawyerResults.isFetching
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
            style={{ cursor: 'pointer' }}
            onClick={(e) => {
              e.preventDefault()
              setShowAdvancedSearch(true)
            }}
          >
            Advanced search
          </Label>
        )}
        {showAdvancedSearch && (
          <>
            <Label
              style={{ cursor: 'pointer' }}
              onClick={(e) => {
                e.preventDefault()
                setShowAdvancedSearch(false)
              }}
            >
              Hide advanced search
            </Label>
            <Form.Group style={{ marginTop: '1em' }}>
              <Form.Field width={8}>
                <Dropdown
                  fluid
                  selection
                  clearable
                  value={query.is_open}
                  placeholder="Is case open?"
                  options={choiceToOptions(CONTEXT.choices.is_open)}
                  onChange={(e, { value }) =>
                    setQuery({ ...query, is_open: value as string })
                  }
                />
              </Form.Field>
              <Form.Field width={8}>
                <Dropdown
                  fluid
                  selection
                  clearable
                  value={query.stage || ''}
                  placeholder="Case stage"
                  options={choiceToOptions(CONTEXT.choices.stage)}
                  onChange={(e, { value }) =>
                    setQuery({ ...query, stage: value as string })
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
                  value={query.outcome || ''}
                  placeholder="Case outcome"
                  options={choiceToOptions(CONTEXT.choices.outcome)}
                  onChange={(e, { value }) =>
                    setQuery({ ...query, outcome: value as string })
                  }
                />
              </Form.Field>
              <Form.Field width={8}>
                <Dropdown
                  fluid
                  selection
                  clearable
                  value={query.topic || ''}
                  placeholder="Case topic"
                  options={choiceToOptions(CONTEXT.choices.topic)}
                  onChange={(e, { value }) =>
                    setQuery({ ...query, topic: value as string })
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
                  options={paralegalResults.data?.map((u) => ({
                    key: u.id,
                    value: u.id,
                    text: u.email,
                  }))}
                  onChange={(e, { value }) =>
                    setQuery({ ...query, paralegal: value as string })
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
                  options={lawyerResults.data?.map((u) => ({
                    key: u.id,
                    value: u.id,
                    text: u.email,
                  }))}
                  onChange={(e, { value }) =>
                    setQuery({ ...query, lawyer: value as string })
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
        onPageChange={onPageChange as any}
        totalPages={totalPages}
        style={{ marginTop: '1em' }}
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
  )
}

const choiceToOptions = (choices) =>
  choices.map(([value, label]) => ({
    key: label,
    text: label,
    value: value,
  }))

mount(App)
