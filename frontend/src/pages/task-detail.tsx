import React, { useState, useEffect } from "react"
import { Container, Header } from "semantic-ui-react"
import * as Yup from "yup"

import { TableForm } from "comps/table-form"
import { getFormSchema, FormField, Model, Choices } from 'comps/auto-form'
import { FIELD_TYPES } from "comps/field-component"
import { mount } from "utils"
import api, { Task, TaskCreate } from "api"

interface DjangoContext {
  choices: {
    status: string[][]
    type: string[][]
  }
  task_pk: string
  list_url: string
}
const CONTEXT = (window as any).REACT_CONTEXT as DjangoContext

const App = () => {
  const [isLoading, setIsLoading] = useState(true)
  const [task, setTask] = useState<Task>()
  const [getTask] = api.useLazyGetTaskQuery()
  const [updateTask] = api.useUpdateTaskMutation()

  useEffect(() => {
    setIsLoading(true)
    getTask({ id: CONTEXT.task_pk })
      .unwrap()
      .then((task) => {
        setTask(task)
        setIsLoading(false)
      })
      .catch(() => setIsLoading(false))
  }, [])
  if (isLoading) return null

  const update = (id: string, values: { [fieldName: string]: unknown }) =>
    updateTask({
      id: task.id,
      taskCreate: values as TaskCreate,
    }).unwrap()

  const choices = (formFields: FormField[], model: Model) =>
    formFields.reduce<Choices>((accumulator, field) => {
      const choices = CONTEXT.choices?.[field.name]
      if (choices) {
        return { ...accumulator, [field.name]: choices }
      } else {
        return accumulator
      }
    }, {})

  return (
    <Container>
      <Header as="h1">{task.name}</Header>
      <Header as="h3">Task details</Header>
      <TableForm
        fields={FIELDS}
        schema={SCHEMA}
        model={task}
        setModel={setTask}
        modelName="task"
        onUpdate={update}
        choices={choices}
      />
    </Container>
  )
}

const FIELDS = [
  {
    label: "Name",
    schema: Yup.string().required("Required"),
    type: FIELD_TYPES.TEXT,
    name: "name",
  },
  {
    label: "Type",
    schema: Yup.string().required("Required"),
    type: FIELD_TYPES.SINGLE_CHOICE,
    name: "type",
  },
  {
    label: "Description",
    type: FIELD_TYPES.TEXTAREA,
    name: "description",
  },
]
const SCHEMA = getFormSchema(FIELDS)

mount(App)
