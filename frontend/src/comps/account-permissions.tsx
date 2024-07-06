import React, { useState, useEffect } from 'react'
import { Table, Label, Button } from 'semantic-ui-react'
import styled from 'styled-components'
import { useSnackbar } from 'notistack'

import { GroupLabels } from 'comps/group-label'
import api, {
  User,
  MicrosoftUserPermissions,
  useResyncUserAccountPermissionsMutation,
  usePromoteUserAccountPermissionsMutation,
  useDemoteUserAccountPermissionsMutation,
} from 'api'
import { getAPIErrorMessage } from 'utils'

interface DjangoContext {
  user: User
}

const CONTEXT = (window as any).REACT_CONTEXT as DjangoContext

interface AccountPermissionsProps {
  account: User
  setAccount: (account: User) => void
}

export const AccountPermissions: React.FC<AccountPermissionsProps> = ({
  account,
  setAccount,
}) => {
  const [isLoading, setIsLoading] = useState(true)
  const [isButtonLoading, setIsButtonLoading] = useState(false)
  const [getPermissions] = api.useLazyGetUserAccountPermissionsQuery()
  const [perms, setPerms] = useState<MicrosoftUserPermissions | null>(null)
  useEffect(() => {
    getPermissions({ id: account.id })
      .unwrap()
      .then((perms) => {
        setPerms(perms)
        setIsLoading(false)
      })
      .catch(() => setIsLoading(false))
  }, [])
  return (
    <>
      <Table size="small" definition>
        <Table.Body>
          <Table.Row>
            <Table.Cell width={3}>Permission groups</Table.Cell>
            <Table.Cell>
              <GroupLabels
                groups={account.groups}
                isSuperUser={account.is_superuser}
              />
            </Table.Cell>
          </Table.Row>
          <Table.Row>
            <Table.Cell width={3}>Microsoft account</Table.Cell>
            <Table.Cell>
              {account.is_ms_account_set_up
                ? `Created on ${account.ms_account_created_at}`
                : 'No Sharepoint access yet - account setup in progress'}
            </Table.Cell>
          </Table.Row>
          <Table.Row>
            <Table.Cell width={3}>Sharepoint access</Table.Cell>
            <Table.Cell>
              {isLoading || !perms ? (
                'Loading...'
              ) : perms.has_coordinator_perms ? (
                'Full access'
              ) : (
                <>
                  {perms.paralegal_perm_issues.map((i) => (
                    <Label color="green" href={i.url} key={i.id}>
                      {i.fileref}
                      <Label.Detail>Has access</Label.Detail>
                    </Label>
                  ))}
                  {perms.paralegal_perm_missing_issues
                    .filter((i) => i.actionstep_id)
                    .map((i) => (
                      <Label color="olive" href={i.url} key={i.id}>
                        {i.fileref}
                        <Label.Detail>Actionstep</Label.Detail>
                      </Label>
                    ))}
                  {perms.paralegal_perm_missing_issues
                    .filter((i) => !i.actionstep_id)
                    .map((i) => (
                      <Label color="yellow" href={i.url} key={i.id}>
                        {i.fileref}
                        <Label.Detail>No access</Label.Detail>
                      </Label>
                    ))}
                </>
              )}
            </Table.Cell>
          </Table.Row>
        </Table.Body>
      </Table>
      {CONTEXT.user.is_admin_or_better && (
        <ButtonList>
          {isLoading && <Button loading>Loading...</Button>}
          {!isLoading && (
            <>
              <PromoteButton
                account={account}
                setAccount={setAccount}
                setPerms={setPerms}
                isLoading={isButtonLoading}
                setIsLoading={setIsButtonLoading}
              />
              <DemoteButton
                account={account}
                setAccount={setAccount}
                setPerms={setPerms}
                isLoading={isButtonLoading}
                setIsLoading={setIsButtonLoading}
              />
              <ResyncButton
                account={account}
                setAccount={setAccount}
                setPerms={setPerms}
                isLoading={isButtonLoading}
                setIsLoading={setIsButtonLoading}
              />
            </>
          )}
        </ButtonList>
      )}
    </>
  )
}

const PromoteButton = ({
  account,
  setAccount,
  setPerms,
  isLoading,
  setIsLoading,
}) => {
  const [promote] = usePromoteUserAccountPermissionsMutation()
  const { enqueueSnackbar } = useSnackbar()

  const onClick = () => {
    setIsLoading(true)
    promote({ id: account.id })
      .unwrap()
      .then(({ account, permissions }) => {
        setAccount(account)
        setPerms(permissions)
        setIsLoading(false)
        enqueueSnackbar('User promoted', { variant: 'success' })
      })
      .catch((err) => {
        enqueueSnackbar(
          getAPIErrorMessage(err, 'Failed to promote this user'),
          {
            variant: 'error',
          }
        )
        setIsLoading(false)
      })
  }
  if (account.is_paralegal) {
    return (
      <Button
        onClick={onClick}
        loading={isLoading}
        disabled={isLoading}
        color="green"
      >
        Promote to coordinator
      </Button>
    )
  } else if (!account.is_paralegal_or_better) {
    return (
      <Button
        onClick={onClick}
        loading={isLoading}
        disabled={isLoading}
        color="green"
      >
        Promote to paralegal
      </Button>
    )
  } else {
    return null
  }
}

const DemoteButton = ({
  account,
  setAccount,
  setPerms,
  isLoading,
  setIsLoading,
}) => {
  const [demote] = useDemoteUserAccountPermissionsMutation()
  const { enqueueSnackbar } = useSnackbar()

  const onClick = () => {
    setIsLoading(true)
    demote({ id: account.id })
      .unwrap()
      .then(({ account, permissions }) => {
        setAccount(account)
        setPerms(permissions)
        setIsLoading(false)
        enqueueSnackbar('User demoted', { variant: 'success' })
      })
      .catch((err) => {
        enqueueSnackbar(getAPIErrorMessage(err, 'Failed to demote this user'), {
          variant: 'error',
        })
        setIsLoading(false)
      })
  }
  if (account.is_coordinator) {
    return (
      <Button
        onClick={onClick}
        loading={isLoading}
        disabled={isLoading}
        color="red"
      >
        Demote to paralegal
      </Button>
    )
  } else if (account.is_paralegal) {
    return (
      <Button
        onClick={onClick}
        loading={isLoading}
        disabled={isLoading}
        color="red"
      >
        Remove paralegal permissions
      </Button>
    )
  } else {
    return null
  }
}

const ResyncButton = ({
  account,
  setAccount,
  setPerms,
  isLoading,
  setIsLoading,
}) => {
  const [resync] = useResyncUserAccountPermissionsMutation()
  const { enqueueSnackbar } = useSnackbar()

  const onClick = () => {
    setIsLoading(true)
    resync({ id: account.id })
      .unwrap()
      .then(({ account, permissions }) => {
        setAccount(account)
        setPerms(permissions)
        setIsLoading(false)
        enqueueSnackbar('Resync successful', { variant: 'success' })
      })
      .catch((err) => {
        enqueueSnackbar(getAPIErrorMessage(err, 'Failed to resync this user'), {
          variant: 'error',
        })
        setIsLoading(false)
      })
  }
  if (account.is_ms_account_set_up) {
    return (
      <Button loading={isLoading} disabled={isLoading} onClick={onClick}>
        Resync permissions
      </Button>
    )
  } else {
    return null
  }
}

const ButtonList = styled.div`
  display: flex;
  gap: 0.5em;
  flex-wrap: wrap;
  margin-bottom: 0.5em;
`
