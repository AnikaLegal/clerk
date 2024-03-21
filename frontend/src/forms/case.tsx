import React, { useState } from 'react'
import { FormikProps } from 'formik'
import { Button, Dropdown, Form, Header, Search } from 'semantic-ui-react'
import { debounce, useEffectLazy } from 'utils'
import api from 'api'

const debouncer = debounce(300)

interface CaseFormProps {
  create?: boolean
  editable?: boolean
  handleDelete?: (e: any) => void
  formik: FormikProps<any>
  topicOptions: string[][]
}

// Formik form component
export const CaseForm: React.FC<CaseFormProps> = ({
  create,
  editable,
  handleDelete,
  formik: {
    values,
    errors,
    handleChange,
    handleSubmit,
    isSubmitting,
    setFieldValue,
  },
  topicOptions,
}) => (
  <Form onSubmit={handleSubmit} error={Object.keys(errors).length > 0}>
    <Header as="h3">Case</Header>
    <div className={`field ${errors.topic && 'error'}`}>
      <label>Topic</label>
      <Dropdown
        compact
        selection
        placeholder="Select case topic"
        onChange={(e, { value }) =>
          setFieldValue('topic', value)
        }
        options={topicOptions}
        disabled={!editable}
      />
    </div>
    <div className={`field ${errors.client_id && 'error'}`}>
      <label>Client</label>
      <ClientSearch />
    </div>
    {Object.entries(errors).map(([k, v]) => (
      <div key={k} className="ui error message">
        <div className="header">{k}</div>
        <p>{v}</p>
      </div>
    ))}
    {editable ? (
      <Button
        primary
        type="submit"
        disabled={isSubmitting}
        loading={isSubmitting}
      >
        {create ? 'Create case' : 'Update case'}
      </Button>
    ) : null}
    {!create && editable ? (
      <Button
        primary
        color="red"
        disabled={isSubmitting}
        loading={isSubmitting}
        onClick={handleDelete}
      >
        Delete
      </Button>
    ) : null}
  </Form>
)

export const ClientSearch = () => {
  const [query, setQuery] = useState('')
  const [page, setPage] = useState(1)
  const [isLoading, setIsLoading] = useState(false)
  const [results, setResults] = useState([])
  const [getClients] = api.useLazyGetClientsQuery()

  const search = debouncer(() => {
    if (query.length < 3) {
      setIsLoading(false)
      return
    }
    setIsLoading(true)
    getClients({ search: query, page: page })
      .unwrap()
      .then((response) => {

        const newResults = response.results.map((
          { id, full_name, preferred_name, email }
        ) => ({
          id: id,
          title: full_name + (preferred_name ? ' (' + preferred_name + ')' : ''),
          description: email
        }))
        setResults([...results, ...newResults])

        if (response.next) {
          setPage(response.next)
        }
        else {
          setIsLoading(false)
        }
      })
      .catch(() => {
        setIsLoading(false)
      })
  })
  useEffectLazy(() => search(), [query, page])

  const handleSearchChange = (e, { value }) => {
    setResults([])
    setPage(1)
    setQuery(value)
  }

  return (
    <Form.Field>
      <Search
        loading={isLoading}
        placeholder='Search...'
        onSearchChange={handleSearchChange}
        results={results}
        noResultsDescription={query.length < 3 ? 'Search value too short' : ''}
      />
    </Form.Field>
  )
}