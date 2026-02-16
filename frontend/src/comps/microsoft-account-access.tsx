import {
  ActionIcon,
  Badge,
  BadgeProps,
  Group,
  Loader,
  Table,
  Text,
  Tooltip,
} from '@mantine/core'
import { IconRefresh } from '@tabler/icons-react'
import {
  Issue,
  useGetUserAccountPermissionsQuery,
  User,
  useResyncUserAccountPermissionsMutation,
} from 'api'
import React from 'react'
import { getAPIErrorMessage } from 'utils'
import styles from './microsoft-account-access.module.css'
import { showNotification } from './notification'

interface DjangoContext {
  user: User
}

const CONTEXT = (window as any).REACT_CONTEXT as DjangoContext

interface MicrosoftAccountAccessProps {
  account: User
}

export const MicrosoftAccountAccess = ({
  account,
}: MicrosoftAccountAccessProps) => {
  return (
    <>
      <Table
        variant="vertical"
        withTableBorder
        withColumnBorders
        verticalSpacing="xs"
        fz="md"
      >
        <Table.Tbody>
          <Table.Tr key="ms_account">
            <Table.Th w="15%">
              <Text fw={700} inherit>
                Microsoft account
              </Text>
            </Table.Th>
            <Table.Td>
              <MicrosoftAccountCell account={account} />
            </Table.Td>
          </Table.Tr>
          <Table.Tr key="sharepoint_access">
            <Table.Th w="15%">
              <Text fw={700} inherit>
                Sharepoint access
              </Text>
            </Table.Th>
            <Table.Td>
              <SharepointAccessCell account={account} />
            </Table.Td>
          </Table.Tr>
        </Table.Tbody>
      </Table>
    </>
  )
}

interface MicrosoftAccountCellProps {
  account: User
}

const MicrosoftAccountCell = ({ account }: MicrosoftAccountCellProps) => {
  const [resyncUserAccountPermissions, result] =
    useResyncUserAccountPermissionsMutation()

  const handleClick = () => {
    if (result.isLoading) {
      return
    }
    resyncUserAccountPermissions({ id: account.id })
      .unwrap()
      .then(() => {
        showNotification({
          type: 'success',
          message: 'Permission reset successful',
        })
      })
      .catch((e) => {
        showNotification({
          type: 'error',
          title: 'Permission reset failed',
          message: getAPIErrorMessage(e),
        })
      })
  }

  return (
    <Group justify="space-between">
      <Text>
        {account.is_ms_account_set_up
          ? `Created on ${account.ms_account_created_at}`
          : 'No access yet - account setup in progress'}
      </Text>
      {CONTEXT.user.is_admin_or_better && (
        <ActionIcon
          variant="transparent"
          color="gray"
          onClick={handleClick}
          disabled={!account.is_active || !account.is_ms_account_set_up}
        >
          <Tooltip openDelay={750} label="Reset Microsoft access permissions">
            <IconRefresh
              className={result.isLoading ? styles.iconRotate : undefined}
            />
          </Tooltip>
        </ActionIcon>
      )}
    </Group>
  )
}

interface IssuePermissionBadgeProps extends BadgeProps {
  issue: Issue
}

const IssuePermissionBadge = ({
  issue,
  children,
  ...props
}: IssuePermissionBadgeProps) => {
  return (
    <Badge
      radius="sm"
      component="a"
      href={issue.url}
      key={issue.id}
      leftSection={issue.fileref}
      style={{ cursor: 'pointer' }}
      miw="9rem"
      {...props}
    >
      {children}
    </Badge>
  )
}

interface SharepointAccessCellProps {
  account: User
}

const SharepointAccessCell = ({ account }: SharepointAccessCellProps) => {
  const result = useGetUserAccountPermissionsQuery({ id: account.id })

  if (result.isLoading) {
    return <Loader size="sm" />
  }

  const data = result.data

  if (data?.has_coordinator_perms) {
    return <Text>Full access</Text>
  }

  return (
    <Group gap="0.25rem">
      {data?.paralegal_perm_issues.map((i) => (
        <IssuePermissionBadge issue={i} color="green.6">
          Has access
        </IssuePermissionBadge>
      ))}
      {data?.paralegal_perm_missing_issues
        .filter((i) => i.actionstep_id)
        .map((i) => (
          <IssuePermissionBadge issue={i} color="green.9">
            Actionstep
          </IssuePermissionBadge>
        ))}
      {data?.paralegal_perm_missing_issues
        .filter((i) => !i.actionstep_id)
        .map((i) => (
          <IssuePermissionBadge issue={i} color="yellow.6">
            No access
          </IssuePermissionBadge>
        ))}
    </Group>
  )
}
