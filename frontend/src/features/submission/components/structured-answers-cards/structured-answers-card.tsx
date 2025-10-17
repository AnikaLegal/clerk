import { Card, CardProps, Table, Text, Title } from '@mantine/core'
import React from 'react'

export interface StructuredAnswersCardProps {
  title: string
  data: { label: string; value: string | number | null | undefined }[][]
  card?: CardProps
}

export const StructuredAnswersCard = ({
  title,
  data,
  card,
}: StructuredAnswersCardProps) => {
  return (
    <Card {...card}>
      <Card.Section>
        <Title order={3}>{title}</Title>
      </Card.Section>
      <Card.Section>
        {data.map(
          (subSection, index) =>
            subSection.some((v) => v.value) && (
              <Table
                key={index}
                variant="vertical"
                withTableBorder
                withColumnBorders
                mt="sm"
              >
                <Table.Tbody>
                  {subSection.map(
                    (row) =>
                      row.value != null && (
                        <Table.Tr key={row.label}>
                          <Table.Th w="25%">
                            <Text fw={700} inherit>
                              {row.label}
                            </Text>
                          </Table.Th>
                          <Table.Td>{row.value}</Table.Td>
                        </Table.Tr>
                      )
                  )}
                </Table.Tbody>
              </Table>
            )
        )}
      </Card.Section>
    </Card>
  )
}
