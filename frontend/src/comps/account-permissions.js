import React, { useState, useEffect } from 'react'
import { Table, Label, Button } from 'semantic-ui-react'
import styled from 'styled-components'

import { api } from 'api'
import { GROUPS } from 'consts'
import { GroupLabels } from 'comps/group-label'

const { user } = window.REACT_CONTEXT

export const AccountPermissions = ({ account, setAccount }) => {
  const [isLoading, setIsLoading] = useState(true)
  const [isButtonLoading, setIsButtonLoading] = useState(false)

  const [perms, setPerms] = useState(null)
  useEffect(() => {
    api.accounts.getPermissions(account.id).then(({ resp, data }) => {
      setPerms(data)
      setIsLoading(false)
    })
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
              {isLoading ? (
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
      {user.is_admin_or_better && (
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
  const onClick = () => {
    setIsLoading(true)
    api.accounts.promote(account.id).then(({ resp, data }) => {
      if (resp.ok) {
        setAccount(data.account)
        setPerms(data.perms)
      }
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
  const onClick = () => {
    setIsLoading(true)
    api.accounts.demote(account.id).then(({ resp, data }) => {
      if (resp.ok) {
        setAccount(data.account)
        setPerms(data.perms)
      }
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
  const onClick = () => {
    setIsLoading(true)
    api.accounts.resync(account.id).then(({ resp, data }) => {
      if (resp.ok) {
        setAccount(data.account)
        setPerms(data.perms)
      }
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
