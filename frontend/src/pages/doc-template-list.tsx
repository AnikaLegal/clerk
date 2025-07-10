import {
  ActionIcon,
  Badge,
  Button,
  Center,
  Container,
  Grid,
  Group,
  Loader,
  Modal,
  ModalProps,
  Select,
  Table,
  Text,
  TextInput,
  Title,
} from '@mantine/core'
import { isNotEmpty, useForm } from '@mantine/form'
import {
  useClickOutside,
  useDebouncedCallback,
  useDisclosure,
} from '@mantine/hooks'
import {
  IconExclamationCircle,
  IconPencil,
  IconSearch,
  IconTrash,
} from '@tabler/icons-react'
import {
  DocumentTemplate,
  GetDocumentTemplatesApiArg,
  useDeleteDocumentTemplateMutation,
  useGetDocumentTemplatesQuery,
  useRenameDocumentTemplateMutation,
} from 'api'
import { enqueueSnackbar } from 'notistack'
import React, { useEffect, useState } from 'react'
import { choiceToMap, getAPIErrorMessage, mount } from 'utils'

import '@mantine/core/styles.css'

interface DjangoContext {
  choices: {
    topic: [string, string][]
  }
  create_url: string
}

const CONTEXT = (window as any).REACT_CONTEXT as DjangoContext
const TopicLabels = choiceToMap(CONTEXT.choices.topic)
const CreateUrl = CONTEXT.create_url

const App = () => {
  const [args, setArgs] = useState<GetDocumentTemplatesApiArg>({})

  const result = useGetDocumentTemplatesQuery(args)

  const setArgByName = (
    name: keyof GetDocumentTemplatesApiArg,
    value: string
  ) => {
    setArgs((prev) => {
      return { ...prev, [name]: value }
    })
  }

  const onChange = useDebouncedCallback(
    (event: React.ChangeEvent<HTMLInputElement>) => {
      setArgByName('name', event.target.value.trim())
    },
    300
  )

  return (
    <Container size="xl">
      <Title order={1}>Document Templates</Title>
      <Button component="a" href={CreateUrl} size="md" mt="sm">
        Upload document template
      </Button>
      <Grid mt="md">
        <Grid.Col span={6}>
          <TextInput
            placeholder="Search by template name..."
            rightSection={<IconSearch size={16} stroke={4} />}
            size="md"
            onChange={onChange}
          />
        </Grid.Col>
        <Grid.Col span={6}>
          <Select
            clearable
            searchable
            size="md"
            placeholder="Select a case topic"
            data={Array.from(TopicLabels, ([key, value]) => ({
              value: key,
              label: value,
            }))}
            onChange={(value) => setArgByName('topic', (value as string) || '')}
            withCheckIcon={false}
          />
        </Grid.Col>
      </Grid>
      <Table
        withColumnBorders
        withTableBorder
        verticalSpacing="md"
        fz="md"
        mt="md"
      >
        <Table.Thead>
          <Table.Tr>
            <Table.Th>Name</Table.Th>
            <Table.Th>Topic</Table.Th>
            <Table.Th>Created</Table.Th>
            <Table.Th>Modified</Table.Th>
            <Table.Th></Table.Th>
          </Table.Tr>
        </Table.Thead>
        <Table.Tbody>
          <DocumentTemplateTableBody result={result} />
        </Table.Tbody>
      </Table>
    </Container>
  )
}

const ErrorState = ({ error }: { error: any }) => {
  useEffect(() => {
    const message = getAPIErrorMessage(
      error,
      'Could not load document templates'
    )
    enqueueSnackbar(message, { variant: 'error' })
  }, [error])

  return (
    <Table.Tr>
      <td colSpan={5}>
        <Group justify="center" gap="xs" m="sm" c="red">
          <IconExclamationCircle />
          <Text>Could not load document templates</Text>
        </Group>
      </td>
    </Table.Tr>
  )
}

const LoadingState = () => (
  <Table.Tr>
    <td colSpan={5}>
      <Center m="sm">
        <Loader />
      </Center>
    </td>
  </Table.Tr>
)

const EmptyState = () => (
  <Table.Tr>
    <td colSpan={5}>
      <Center m="sm">No templates found</Center>
    </td>
  </Table.Tr>
)

interface DocumentTemplateTableBodyProps {
  result: ReturnType<typeof useGetDocumentTemplatesQuery>
}

const DocumentTemplateTableBody = ({
  result,
}: DocumentTemplateTableBodyProps) => {
  if (result.isError) {
    return <ErrorState error={result.error} />
  }
  if (result.isLoading) {
    return <LoadingState />
  }

  const data: DocumentTemplate[] = result.data || []
  if (data.length < 1) {
    return <EmptyState />
  }
  return (
    <>
      {data.map((template) => (
        <DocumentTemplateTableRow
          key={template.url || template.name}
          template={template}
        />
      ))}
    </>
  )
}

interface DocumentTemplateTableRowProps {
  template: DocumentTemplate
}

const DocumentTemplateTableRow = ({
  template,
}: DocumentTemplateTableRowProps) => {
  const found: boolean = !!template.url
  return (
    <Table.Tr>
      <Table.Td>
        {found ? (
          <a href={template.url}>{template.name}</a>
        ) : (
          <Group>
            <span>{template.name}</span>
            <Badge radius="xs" color="red">
              File Not Found
            </Badge>
          </Group>
        )}
      </Table.Td>
      <Table.Td>{TopicLabels.get(template.topic)}</Table.Td>
      <Table.Td>{template.created_at || '-'}</Table.Td>
      <Table.Td>{template.modified_at || '-'}</Table.Td>
      <Table.Td>
        <DocumentTemplateActionIcons template={template} isFileFound={found} />
      </Table.Td>
    </Table.Tr>
  )
}

interface DocumentTemplateActionIconsProps {
  template: DocumentTemplate
  isFileFound: boolean
}

const DocumentTemplateActionIcons = ({
  template,
  isFileFound,
}: DocumentTemplateActionIconsProps) => {
  const [displayConfirmDelete, confirmDeleteHandlers] = useDisclosure(false)
  const [displayRenameModal, renameModalHandlers] = useDisclosure(false)
  const [deleteDocumentTemplate] = useDeleteDocumentTemplateMutation()

  const delayedHideConfirmDelete = useDebouncedCallback(() => {
    confirmDeleteHandlers.close()
  }, 100)
  const ref = useClickOutside(() => delayedHideConfirmDelete())

  const handleDelete = () => {
    deleteDocumentTemplate({ id: template.id })
      .unwrap()
      .then(() => {
        enqueueSnackbar('Document template deleted', { variant: 'success' })
      })
      .catch((e) => {
        enqueueSnackbar(
          getAPIErrorMessage(e, 'Failed to delete document template'),
          {
            variant: 'error',
          }
        )
      })
  }

  if (displayConfirmDelete) {
    return (
      <div ref={ref}>
        <Center>
          <Button
            variant="filled"
            color="red"
            size="compact-sm"
            onClick={handleDelete}
          >
            Confirm delete
          </Button>
        </Center>
      </div>
    )
  }

  return (
    <>
      <DocumentTemplateRenameModal
        opened={displayRenameModal}
        onClose={() => renameModalHandlers.close()}
        template={template}
      />
      <Center>
        <ActionIcon variant="transparent" color="gray" disabled={!isFileFound}>
          <IconPencil stroke={1.5} onClick={() => renameModalHandlers.open()} />
        </ActionIcon>
        <ActionIcon variant="transparent" color="gray">
          <IconTrash
            stroke={1.5}
            onClick={() => confirmDeleteHandlers.open()}
          />
        </ActionIcon>
      </Center>
    </>
  )
}

interface DocumentTemplateRenameModalProps extends ModalProps {
  template: DocumentTemplate
}

const DocumentTemplateRenameModal = (
  props: DocumentTemplateRenameModalProps
) => {
  const [renameDocumentTemplate] = useRenameDocumentTemplateMutation()

  const parts = props.template.name.split('.')
  const ext = parts.length > 1 ? '.' + parts.pop() : ''
  const name = parts.join('.')

  type formValues = { name: string }
  const form = useForm<formValues>({
    mode: 'uncontrolled',
    initialValues: {
      name: name,
    },
    validate: {
      name: isNotEmpty('This field is required.'),
    },
  })

  const handleSubmit = (
    values: formValues,
    event: React.FormEvent<HTMLFormElement> | undefined
  ) => {
    event?.preventDefault()

    form.setSubmitting(true)
    renameDocumentTemplate({
      id: props.template.id,
      documentTemplateRename: { name: values.name + ext },
    })
      .unwrap()
      .then(() => {
        enqueueSnackbar('Document template renamed', { variant: 'success' })
        props.onClose()
      })
      .catch((e) => {
        enqueueSnackbar(
          getAPIErrorMessage(e, 'Failed to rename document template'),
          {
            variant: 'error',
          }
        )
      })
      .finally(() => form.setSubmitting(false))
  }

  const handleClose = () => {
    props.onClose()
    form.reset()
  }

  return (
    <Modal
      opened={props.opened}
      onClose={handleClose}
      title={<Text fw={700}>Rename Document Template</Text>}
      size="lg"
    >
      <form onSubmit={form.onSubmit(handleSubmit)}>
        <TextInput
          {...form.getInputProps('name')}
          key={form.key('name')}
          data-autofocus
          rightSection={<Text>{ext}</Text>}
          rightSectionWidth="3rem"
          size="md"
        />
        <Group justify="right" mt="lg">
          <Button
            variant="default"
            onClick={handleClose}
            disabled={form.submitting}
          >
            Close
          </Button>
          <Button
            type="submit"
            disabled={form.submitting}
            loading={form.submitting}
          >
            Rename
          </Button>
        </Group>
      </form>
    </Modal>
  )
}

mount(App)
