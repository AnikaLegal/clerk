import React, { useState } from 'react'
import { Container, Header } from 'semantic-ui-react'
import * as Yup from 'yup'

import { TableForm } from 'comps/table-form'
import { getFormSchema } from 'comps/auto-form'
import { FIELD_TYPES } from 'comps/field-component'
import { CaseListTable } from 'comps/case-table'
import { mount } from 'utils'
import { Client, ClientCreate, useUpdateClientMutation } from 'api'

interface DjangoContext {
  client: Client
  issues: any[]
}

const { client: initialClient, issues } = (window as any)
  .REACT_CONTEXT as DjangoContext

const App = () => {
  const [client, setClient] = useState<Client>(initialClient)
  const [updateClient] = useUpdateClientMutation()
  const update = (id: string, values: { [fieldName: string]: unknown }) =>
    updateClient({
      id: client.id,
      clientCreate: values as ClientCreate,
    }).unwrap()

  return (
    <Container>
      <Header as="h1">{client.full_name} (Client)</Header>
      <Header as="h3">Personal details</Header>
      <TableForm
        fields={PERSONAL_FIELDS}
        schema={PERSONAL_SCHEMA}
        model={client}
        setModel={setClient}
        modelName="client"
        onUpdate={update}
      />
      <Header as="h3">Contact details</Header>
      <TableForm
        fields={CONTACT_FIELDS}
        schema={CONTACT_SCHEMA}
        model={client}
        setModel={setClient}
        modelName="client"
        onUpdate={update}
      />
      <Header as="h3">Other Information</Header>
      <TableForm
        fields={OTHER_FIELDS}
        schema={OTHER_SCHEMA}
        model={client}
        setModel={setClient}
        modelName="client"
        onUpdate={update}
      />
      <Header as="h3">Cases</Header>
      <CaseListTable issues={issues} fields={TABLE_FIELDS} />
    </Container>
  )
}

const TABLE_FIELDS = [
  'fileref',
  'topic',
  'paralegal',
  'lawyer',
  'created_at',
  'stage',
  'provided_legal_services',
  'outcome',
]

const PERSONAL_FIELDS = [
  {
    label: 'First name',
    schema: Yup.string().required('Required'),
    type: FIELD_TYPES.TEXT,
    name: 'first_name',
  },
  {
    label: 'Last name',
    schema: Yup.string().required('Required'),
    type: FIELD_TYPES.TEXT,
    name: 'last_name',
  },
  {
    label: 'Preferred name',
    type: FIELD_TYPES.TEXT,
    name: 'preferred_name',
  },
  {
    label: 'Gender',
    name: 'gender',
    type: FIELD_TYPES.TEXT,
    schema: Yup.string().required('Required'),
  },
  {
    label: 'Pronouns',
    type: FIELD_TYPES.TEXT,
    name: 'pronouns',
  },
  {
    label: 'Date of birth',
    type: FIELD_TYPES.DATE,
    name: 'date_of_birth',
  },
  {
    label: 'Notes',
    type: FIELD_TYPES.TEXTAREA,
    name: 'notes',
  },
]
const CONTACT_FIELDS = [
  {
    label: 'Email',
    type: FIELD_TYPES.TEXT,
    name: 'email',
    schema: Yup.string().email().required('Required'),
  },
  {
    label: 'Phone number',
    name: 'phone_number',
    type: FIELD_TYPES.TEXT,
    schema: Yup.string().required('Required'),
  },
  {
    label: 'Call times',
    type: FIELD_TYPES.MULTI_CHOICE,
    name: 'call_times',
  },
]
const OTHER_FIELDS = [
  {
    label: 'Eligibility notes',
    name: 'eligibility_notes',
    schema: Yup.string(),
    type: FIELD_TYPES.TEXT,
  },
  {
    label: 'Eligibility circumstances',
    type: FIELD_TYPES.MULTI_CHOICE,
    name: 'eligibility_circumstances',
  },
  {
    label: 'Is on Centrelink?',
    name: 'centrelink_support',
    schema: Yup.bool(),
    type: FIELD_TYPES.BOOL,
  },
  {
    label: 'Number of dependents',
    name: 'number_of_dependents',
    schema: Yup.number().integer().min(0).nullable(true),
    type: FIELD_TYPES.NUMBER,
  },
  {
    label: 'Primary language',
    name: 'primary_language',
    schema: Yup.string(),
    type: FIELD_TYPES.TEXT,
  },
  {
    label: 'Requires an interpreter?',
    name: 'requires_interpreter',
    type: FIELD_TYPES.SINGLE_CHOICE,
  },
  {
    label: 'Is Aboriginal or Torres Strait Islander?',
    name: 'is_aboriginal_or_torres_strait_islander',
    type: FIELD_TYPES.SINGLE_CHOICE,
  },
]
const PERSONAL_SCHEMA = getFormSchema(PERSONAL_FIELDS)
const CONTACT_SCHEMA = getFormSchema(CONTACT_FIELDS)
const OTHER_SCHEMA = getFormSchema(OTHER_FIELDS)

mount(App)
