import {
  Box,
  Button,
  Container,
  Grid,
  Group,
  Pagination,
  Stack,
  Text,
  Title,
  Transition,
} from '@mantine/core'
import { useToggle } from '@mantine/hooks'
import { GetCasesApiArg, useGetCasesQuery } from 'api'
import { CaseListTable } from 'comps/case-table'
import { SelectFilter, TextInputFilter } from 'comps/filter'
import { UserSelect } from 'comps/user-select'
import React, { useState } from 'react'
import { UserPermission } from 'types'
import { mount } from 'utils'

interface DjangoContext {
  user: UserPermission
  choices: {
    stage: string[][]
    topic: string[][]
    outcome: string[][]
    is_open: string[][]
  }
  create_url: string
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

const App = () => {
  const [showAdvancedSearch, toggleAdvancedSearch] = useToggle()
  const [args, setArgs] = useState<GetCasesApiArg>({})

  const handleFilterChange = (key, value) => {
    setArgs((prev) => ({
      ...prev,
      [key]: value !== null ? value : undefined,
      page: 1, // Reset to first page on filter change
    }))
  }

  const result = useGetCasesQuery(args)
  const issues = result.data?.results ?? []
  const currentPage = result.data?.current
  const totalPages = result.data?.page_count

  return (
    <Container size="xl">
      <Title order={1}>
        <Group wrap="nowrap" gap="sm" justify="space-between">
          <span>Cases</span>
          {CONTEXT.user.is_coordinator_or_better && (
            <Button component="a" href={CONTEXT.create_url}>
              Create a new case
            </Button>
          )}
        </Group>
      </Title>
      {!result.isLoading && result.data && (
        <Text c="dimmed">
          Showing {result.data.results.length} of {result.data.item_count} cases
        </Text>
      )}
      <Stack gap="md" mt="md">
        <TextInputFilter
          name="search"
          placeholder="Find cases with the name or email of paralegals and clients, or by using the file ref"
          onFilterChange={handleFilterChange}
        />
        <Group>
          <Button
            variant="filled"
            onClick={() => toggleAdvancedSearch()}
            size="compact-sm"
            color="gray.3"
            fw="normal"
            autoContrast
          >
            {showAdvancedSearch ? 'Hide advanced search' : 'Advanced search'}
          </Button>
        </Group>
        {showAdvancedSearch && (
          <Grid>
            <Grid.Col span={6}>
              <SelectFilter
                name="isOpen"
                placeholder="Is case open?"
                data={choiceToOptions(CONTEXT.choices.is_open)}
                onFilterChange={handleFilterChange}
              />
            </Grid.Col>
            <Grid.Col span={6}>
              <SelectFilter
                name="stage"
                placeholder="Case stage"
                data={choiceToOptions(CONTEXT.choices.stage)}
                onFilterChange={handleFilterChange}
              />
            </Grid.Col>
            <Grid.Col span={6}>
              <SelectFilter
                name="outcome"
                placeholder="Case outcome"
                data={choiceToOptions(CONTEXT.choices.outcome)}
                onFilterChange={handleFilterChange}
              />
            </Grid.Col>
            <Grid.Col span={6}>
              <SelectFilter
                name="topic"
                placeholder="Case topic"
                data={choiceToOptions(CONTEXT.choices.topic)}
                onFilterChange={handleFilterChange}
              />
            </Grid.Col>
            <Grid.Col span={6}>
              <UserSelect
                searchable
                clearable
                placeholder="Select a paralegal"
                onChange={(value) =>
                  setArgs({ ...args, paralegal: value || undefined, page: 1 })
                }
                params={{
                  group: 'Paralegal',
                  sort: 'email',
                }}
                size="md"
              />
            </Grid.Col>
            <Grid.Col span={6}>
              <UserSelect
                searchable
                clearable
                placeholder="Select a lawyer"
                onChange={(value) =>
                  setArgs({ ...args, lawyer: value || undefined, page: 1 })
                }
                filter={{
                  group: 'Lawyer',
                  sort: 'email',
                }}
                size="md"
              />
            </Grid.Col>
          </Grid>
        )}
      </Stack>
      <Box mt="md">
        <Transition
          mounted={!result.isFetching}
          transition="fade"
          duration={300}
          timingFunction="ease"
        >
          {(styles) => (
            <Box style={styles}>
              <CaseListTable issues={issues} fields={TABLE_FIELDS} />
              {!!totalPages && (
                <Pagination
                  total={totalPages}
                  value={currentPage || 1}
                  onChange={(page) => setArgs({ ...args, page })}
                  mt="md"
                  withEdges
                  withControls
                />
              )}
            </Box>
          )}
        </Transition>
      </Box>
    </Container>
  )
}

const choiceToOptions = (choices: string[][]) =>
  choices.map(([value, label]) => ({
    value,
    label,
  }))

mount(App)
