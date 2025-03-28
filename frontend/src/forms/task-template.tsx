import { useClickOutside, useDebouncedCallback } from '@mantine/hooks'
import {
  IssueEventType,
  IssueStage,
  IssueTopic,
  TaskTemplate,
  TaskTriggerCreate,
  TaskTriggerRole,
  TaskType,
} from 'api'
import { DiscardChangesConfirmationModal } from 'comps/modal'
import {
  CASE_EVENT_TYPES,
  CASE_STAGES,
  TASK_TRIGGER_ROLES,
  TASK_TRIGGER_TOPICS,
  TASK_TYPES,
  TASK_TYPES_WITHOUT_REQUEST_TYPES,
} from 'consts'
import {
  FieldArray,
  FieldArrayRenderProps,
  Formik,
  FormikHelpers,
} from 'formik'
import {
  BooleanField,
  DropdownField,
  InputField,
  RichTextEditorField,
} from 'forms/formik'
import React, { useEffect, useState } from 'react'
import {
  Button,
  ButtonProps,
  Form,
  Grid,
  Header,
  Icon,
  IconProps,
  Modal,
  Segment,
  Table,
} from 'semantic-ui-react'
import * as Yup from 'yup'

Yup.setLocale({ mixed: { required: 'This field is required.' } })

const TaskTemplateSchema: Yup.ObjectSchema<TaskTemplate> = Yup.object({
  id: Yup.number().optional(),
  name: Yup.string().required(),
  type: Yup.string<TaskType>().required(),
  due_in: Yup.number().required().nullable().default(null),
  is_urgent: Yup.boolean().required(),
  is_approval_required: Yup.boolean().required(),
  description: Yup.string().optional(),
})

const TaskTriggerSchema: Yup.ObjectSchema<TaskTriggerCreate> = Yup.object({
  name: Yup.string().required(),
  topic: Yup.string<IssueTopic>().required(),
  event: Yup.string<IssueEventType>().required(),
  tasks_assignment_role: Yup.string<TaskTriggerRole>().required(),
  templates: Yup.array().of(TaskTemplateSchema).required(),
  event_stage: Yup.string<IssueStage>().when('event', {
    is: 'STAGE',
    then: (schema) => schema.required(),
    otherwise: (schema) => schema.notRequired(),
  }),
})

interface TaskTemplateFormProps {
  create?: boolean
  onDelete?: (e: any) => void
  initialValues: TaskTriggerCreate
  onSubmit: (
    values: TaskTriggerCreate,
    formikHelpers: FormikHelpers<TaskTriggerCreate>
  ) => void | Promise<any>
}

const beforeUnloadHandler = (event) => {
  event.preventDefault()
  event.returnValue = true
}

const HandleUnload = ({ dirty }: { dirty: boolean }) => {
  useEffect(() => {
    if (dirty) {
      window.addEventListener('beforeunload', beforeUnloadHandler)
    } else {
      window.removeEventListener('beforeunload', beforeUnloadHandler)
    }
  }, [dirty])

  return null
}

export const TaskTemplateForm: React.FC<TaskTemplateFormProps> = ({
  create,
  onDelete,
  initialValues,
  onSubmit,
}) => {
  const [showEventStage, setShowEventStage] = useState<boolean>(
    initialValues.event === 'STAGE'
  )

  const handleSubmit = (
    values: TaskTriggerCreate,
    helpers: FormikHelpers<TaskTriggerCreate>
  ) => {
    onSubmit(values, helpers)
    helpers.resetForm({ values: values })
  }

  return (
    <Formik
      initialValues={initialValues}
      onSubmit={handleSubmit}
      validationSchema={TaskTriggerSchema}
    >
      {(formik) => (
        <>
          <HandleUnload dirty={formik.dirty} />
          <Form
            onSubmit={formik.handleSubmit}
            error={Object.keys(formik.errors).length > 0}
          >
            <InputField
              required
              name="name"
              label="Name"
              placeholder="Describe the task template"
              disabled={formik.isSubmitting}
            />
            <DropdownField
              required
              name="topic"
              label="Case type"
              placeholder="Select a case type"
              options={Object.entries(TASK_TRIGGER_TOPICS).map(
                ([key, value]) => ({
                  key: key,
                  value: key,
                  text: value,
                })
              )}
              disabled={formik.isSubmitting}
            />
            <DropdownField
              required
              name="event"
              label="Trigger event"
              placeholder="Select which event will trigger task creation"
              options={Object.entries(CASE_EVENT_TYPES).map(([key, value]) => ({
                key: key,
                value: key,
                text: value,
              }))}
              onChange={(e, { value }) => {
                const isStage = value === 'STAGE'
                setShowEventStage(isStage)
                if (!isStage) {
                  formik.setFieldValue('event_stage', null)
                }
                formik.setFieldTouched('event_stage', false)
              }}
              disabled={formik.isSubmitting}
            />
            {showEventStage && (
              <DropdownField
                required
                name="event_stage"
                label="Trigger stage"
                placeholder="Select which event stage will trigger task creation"
                options={Object.entries(CASE_STAGES).map(([key, value]) => ({
                  key: key,
                  value: key,
                  text: value,
                }))}
                disabled={formik.isSubmitting}
              />
            )}
            <DropdownField
              required
              name="tasks_assignment_role"
              label="Assignment role"
              placeholder="Select the role of the user to which the task(s) should be assigned"
              options={Object.entries(TASK_TRIGGER_ROLES).map(
                ([key, value]) => ({
                  key: key,
                  value: key,
                  text: value,
                })
              )}
              disabled={formik.isSubmitting}
            />

            <FieldArray name="templates">
              {(arrayHelpers) => {
                return (
                  <>
                    <Grid>
                      <Grid.Row columns={2} style={{ alignItems: 'center' }}>
                        <Grid.Column>
                          <Header as="h3">Tasks</Header>
                        </Grid.Column>
                        <Grid.Column>
                          <AddTaskTemplateButton
                            floated="right"
                            size="mini"
                            type="button"
                            arrayHelpers={arrayHelpers}
                          >
                            Add task
                          </AddTaskTemplateButton>
                        </Grid.Column>
                      </Grid.Row>
                    </Grid>
                    <TaskTemplateTable
                      arrayHelpers={arrayHelpers}
                      templates={formik.values.templates}
                    />
                  </>
                )
              }}
            </FieldArray>

            <Button
              primary
              type="submit"
              disabled={formik.isSubmitting}
              loading={formik.isSubmitting}
              style={{ marginTop: '1rem' }}
            >
              {create ? 'Create task template' : 'Update task template'}
            </Button>
            {!create && onDelete && (
              <Button
                color="red"
                disabled={formik.isSubmitting}
                onClick={onDelete}
              >
                Delete
              </Button>
            )}
          </Form>
        </>
      )}
    </Formik>
  )
}

interface TaskTemplateTableProps {
  arrayHelpers: FieldArrayRenderProps
  templates: TaskTemplate[]
}

export const TaskTemplateTable = ({
  arrayHelpers,
  templates,
}: TaskTemplateTableProps) => {
  if (templates.length == 0) {
    return (
      <Segment textAlign="center" secondary>
        <p>No tasks.</p>
      </Segment>
    )
  }
  return (
    <Table celled>
      <Table.Header>
        <Table.Row>
          <Table.HeaderCell>Name</Table.HeaderCell>
          <Table.HeaderCell>Type</Table.HeaderCell>
          <Table.HeaderCell>Due in</Table.HeaderCell>
          <Table.HeaderCell>Urgent?</Table.HeaderCell>
          <Table.HeaderCell>Approval required?</Table.HeaderCell>
          <Table.HeaderCell></Table.HeaderCell>
        </Table.Row>
      </Table.Header>
      <Table.Body>
        {templates.map((template, index) => (
          <Table.Row key={template.id || template.type + '_' + template.name}>
            <Table.Cell>{template.name}</Table.Cell>
            <Table.Cell>{TASK_TYPES[template.type]}</Table.Cell>
            <Table.Cell>{template.due_in || '-'}</Table.Cell>
            <Table.Cell>{template.is_urgent ? 'Yes' : 'No'}</Table.Cell>
            <Table.Cell>
              {template.is_approval_required ? 'Yes' : 'No'}
            </Table.Cell>
            <Table.Cell collapsing textAlign="center">
              <TaskTemplateActionIcons
                templates={templates}
                index={index}
                arrayHelpers={arrayHelpers}
              />
            </Table.Cell>
          </Table.Row>
        ))}
      </Table.Body>
    </Table>
  )
}

export interface TaskTemplateActionIconProps {
  templates: TaskTemplate[]
  index: number
  arrayHelpers: FieldArrayRenderProps
}

export const TaskTemplateActionIcons = ({
  templates,
  index,
  arrayHelpers,
}: TaskTemplateActionIconProps) => {
  const [showConfirmDelete, setShowConfirmDelete] = useState(false)

  /* Handle a situation where a click event does not trigger due to element
   * resizing when attempting to click an action icon on another row of the same
   * table when a confirm delete button is already showing. This delays the
   * element resize which allows the click event to trigger. This feels nasty and
   * probably is and I presume it might not always work but gets the job done
   * most of the time */
  const delayedHideConfirmDelete = useDebouncedCallback(() => {
    setShowConfirmDelete(false)
  }, 100)
  const ref = useClickOutside(() => delayedHideConfirmDelete())

  if (showConfirmDelete) {
    return (
      <div ref={ref}>
        <Button
          negative
          compact
          size="mini"
          onClick={(event) => {
            event.preventDefault()
            arrayHelpers.remove(index)
            setShowConfirmDelete(false)
          }}
        >
          Confirm delete
        </Button>
      </div>
    )
  }
  return (
    <>
      <EditTaskTemplateIcon
        link
        name="pencil"
        templates={templates}
        index={index}
        arrayHelpers={arrayHelpers}
      />
      <Icon
        link
        name="trash alternate outline"
        onClick={() => setShowConfirmDelete(true)}
      />
      {templates.length > 1 && (
        <>
          <Icon
            link
            name="arrow up"
            onClick={() => arrayHelpers.move(index, index - 1)}
            disabled={index == 0}
          />
          <Icon
            link
            name="arrow down"
            onClick={() => arrayHelpers.move(index, index + 1)}
            disabled={index == templates.length - 1}
          />
        </>
      )}
    </>
  )
}

export interface EditTaskTemplateIconProps {
  templates: TaskTemplate[]
  index: number
  arrayHelpers: FieldArrayRenderProps
}

export const EditTaskTemplateIcon = ({
  templates,
  index,
  arrayHelpers,
  ...props
}: EditTaskTemplateIconProps & IconProps) => {
  const [open, setOpen] = useState(false)

  const handleSubmit = (
    template: TaskTemplate,
    { resetForm }: FormikHelpers<TaskTemplate>
  ) => {
    arrayHelpers.replace(index, template)
    resetForm()
    setOpen(false)
  }

  return (
    <>
      <TaskTemplateModal
        initialValues={templates[index]}
        open={open}
        setOpen={setOpen}
        handleSubmit={handleSubmit}
        label="Update task"
      />
      <Icon {...props} onClick={() => setOpen(true)} />
    </>
  )
}

export interface AddTaskTemplateButtonProps {
  arrayHelpers: FieldArrayRenderProps
  children: string | number
}

export const AddTaskTemplateButton = ({
  arrayHelpers,
  children,
  ...props
}: AddTaskTemplateButtonProps & ButtonProps) => {
  const [open, setOpen] = useState(false)

  const handleSubmit = (
    template: TaskTemplate,
    { resetForm }: FormikHelpers<TaskTemplate>
  ) => {
    arrayHelpers.push(template)
    resetForm()
    setOpen(false)
  }

  return (
    <>
      <TaskTemplateModal
        initialValues={{
          // @ts-expect-error
          type: '',
          name: '',
          due_in: null,
          is_urgent: false,
          is_approval_required: false,
          description: '',
        }}
        open={open}
        setOpen={setOpen}
        handleSubmit={handleSubmit}
        label={children}
      />
      <Button {...props} onClick={() => setOpen(true)}>
        {children}
      </Button>
    </>
  )
}

export interface TaskTemplateModalProps {
  open: boolean
  setOpen: React.Dispatch<React.SetStateAction<boolean>>
  initialValues: TaskTemplate
  handleSubmit: (
    values: TaskTemplate,
    helpers: FormikHelpers<TaskTemplate>
  ) => void
  label: string | number
}

export const TaskTemplateModal = ({
  open,
  setOpen,
  initialValues,
  handleSubmit,
  label,
}: TaskTemplateModalProps) => {
  const [confirmationOpen, setConfirmationOpen] = useState(false)

  return (
    <Formik
      enableReinitialize
      initialValues={initialValues}
      onSubmit={handleSubmit}
      validationSchema={TaskTemplateSchema}
    >
      {(formik) => {
        const confirmDiscardHandler = () => {
          setConfirmationOpen(false)
          setOpen(false)
          formik.resetForm()
        }
        const cancelDiscardHandler = () => {
          setConfirmationOpen(false)
        }

        const closeHandler = () => {
          if (formik.dirty) {
            setConfirmationOpen(true)
          } else {
            setOpen(false)
            formik.resetForm()
          }
        }
        return (
          <>
            <DiscardChangesConfirmationModal
              open={confirmationOpen}
              onConfirm={confirmDiscardHandler}
              onCancel={cancelDiscardHandler}
            />
            <Modal size="large" open={open} onClose={closeHandler}>
              <Modal.Header>{label}</Modal.Header>
              <Modal.Content>
                <Form
                  onSubmit={formik.handleSubmit}
                  error={Object.keys(formik.errors).length > 0}
                >
                  <InputField
                    name="name"
                    label="Task name"
                    placeholder="Provide more specific task information"
                    required
                  />
                  <DropdownField
                    name="type"
                    label="Task type"
                    placeholder="Select the task type"
                    options={Object.entries(
                      TASK_TYPES_WITHOUT_REQUEST_TYPES
                    ).map(([key, value]) => ({
                      key: key,
                      value: key,
                      text: value,
                    }))}
                    required
                  />
                  <InputField
                    name="due_in"
                    type="number"
                    label="Due in"
                    placeholder="The number of days from when the task is assigned until it is due"
                  />
                  <BooleanField
                    name="is_urgent"
                    label="Urgent?"
                    placeholder="Is the task urgent?"
                  />
                  <BooleanField
                    name="is_approval_required"
                    label="Approval required?"
                    placeholder="Does the task require approval?"
                  />
                  <RichTextEditorField
                    name="description"
                    label="Task description"
                    placeholder="Describe the task in detail"
                  />
                </Form>
              </Modal.Content>
              <Modal.Actions>
                <Button
                  primary
                  type="submit"
                  onClick={() => formik.handleSubmit()}
                >
                  {label}
                </Button>
                <Button onClick={closeHandler}>Close</Button>
              </Modal.Actions>
            </Modal>
          </>
        )
      }}
    </Formik>
  )
}
