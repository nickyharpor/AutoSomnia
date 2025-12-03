import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import Card from '../components/common/Card'
import Table from '../components/common/Table'
import Button from '../components/common/Button'
import './Users.css'

const Users = () => {
  const { t } = useTranslation('pages')
  const [users] = useState([])

  const columns = [
    { key: 'user_id', label: t('users.columns.userId') },
    { key: 'auto_exchange', label: t('users.columns.autoExchange'), render: (value) => value ? t('users.status.enabled') : t('users.status.disabled') },
    { key: 'created_at', label: t('users.columns.createdAt') },
    { key: 'actions', label: t('users.columns.actions'), render: () => <Button size="small">{t('users.manage')}</Button> }
  ]

  return (
    <div className="users-page">
      <div className="page-header">
        <h1>{t('users.title')}</h1>
        <Button>{t('users.addUser')}</Button>
      </div>
      
      <Card>
        {users.length > 0 ? (
          <Table columns={columns} data={users} />
        ) : (
          <p className="empty-state">{t('users.noUsers')}</p>
        )}
      </Card>
    </div>
  )
}

export default Users
