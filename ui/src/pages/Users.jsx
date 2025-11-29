import { useState } from 'react'
import Card from '../components/common/Card'
import Table from '../components/common/Table'
import Button from '../components/common/Button'
import './Users.css'

const Users = () => {
  const [users] = useState([])

  const columns = [
    { key: 'user_id', label: 'User ID' },
    { key: 'auto_exchange', label: 'Auto Exchange', render: (value) => value ? 'Enabled' : 'Disabled' },
    { key: 'created_at', label: 'Created At' },
    { key: 'actions', label: 'Actions', render: () => <Button size="small">Manage</Button> }
  ]

  return (
    <div className="users-page">
      <div className="page-header">
        <h1>Users</h1>
        <Button>Add User</Button>
      </div>
      
      <Card>
        {users.length > 0 ? (
          <Table columns={columns} data={users} />
        ) : (
          <p className="empty-state">No users found</p>
        )}
      </Card>
    </div>
  )
}

export default Users
