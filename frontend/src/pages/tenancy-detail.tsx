import React, { useState } from 'react'
import { Container, Header, Table } from 'semantic-ui-react'

import { mount } from 'utils'
import { CaseListTable } from 'comps/case-table'
import { Tenancy, TenancyCreate, useUpdateTenancyMutation } from 'api'
import { TableForm } from 'comps/table-form'
import { FIELD_TYPES } from 'comps/field-component'
import { getFormSchema } from 'comps/auto-form'
import * as Yup from 'yup'

interface DjangoContext {
  tenancy: Tenancy
  issues: any[]
}

const { tenancy: initialTenancy, issues } = (window as any)
  .REACT_CONTEXT as DjangoContext

const App = () => {
  const [tenancy, setTenancy] = useState<Tenancy>(initialTenancy)
  const [updateTenancy] = useUpdateTenancyMutation()
  const update = (id: string, values: { [fieldName: string]: unknown }) =>
    updateTenancy({
      id: tenancy.id,
      tenancyCreate: values as TenancyCreate,
    }).unwrap()

  return (
    <Container>
      <Header as="h1">Tenancy</Header>
      <Header as="h3">Property details</Header>
      <TableForm
        fields={PROPERTY_FIELDS}
        schema={PROPERTY_SCHEMA}
        model={tenancy}
        setModel={setTenancy}
        modelName="tenancy"
        onUpdate={update}
      />
      <Header as="h3">Property people</Header>
      <Table className="definition small">
        <Table.Body>
          <Table.Row>
            <Table.Cell className="four wide">Agent</Table.Cell>
            <Table.Cell>
              {tenancy.agent ? (
                <a href={tenancy.agent.url}>{tenancy.agent.full_name}</a>
              ) : (
                'No agent'
              )}
            </Table.Cell>
          </Table.Row>
          <Table.Row>
            <Table.Cell className="four wide">Landlord</Table.Cell>
            <Table.Cell>
              {tenancy.landlord ? (
                <a href={tenancy.landlord.url}>{tenancy.landlord.full_name}</a>
              ) : (
                'No landlord'
              )}
            </Table.Cell>
          </Table.Row>
        </Table.Body>
      </Table>
      <Header as="h3">Cases</Header>
      <CaseListTable issues={issues} fields={TABLE_FIELDS} />
    </Container>
  )
}


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

const PROPERTY_FIELDS = [
  {
    label: 'Address',
    schema: Yup.string().required('Required'),
    type: FIELD_TYPES.TEXT,
    name: 'address',
  },
  {
    label: 'Suburb',
    schema: Yup.string().required('Required'),
    type: FIELD_TYPES.TEXT,
    name: 'suburb',
  },
  {
    label: 'Postcode',
    schema: Yup.string().required('Required'),
    type: FIELD_TYPES.TEXT,
    name: 'postcode',
  },
  {
    label: 'Tenancy start date',
    type: FIELD_TYPES.DATE,
    name: 'started',
  },
  {
    label: 'Is client on lease?',
    type: FIELD_TYPES.SINGLE_CHOICE,
    name: 'is_on_lease',
  },
  {
    label: 'Rental circumstances',
    type: FIELD_TYPES.SINGLE_CHOICE,
    name: 'rental_circumstances',
  },
]

const PROPERTY_SCHEMA = getFormSchema(PROPERTY_FIELDS)

mount(App)
