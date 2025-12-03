import { useState, useRef, useEffect } from 'react'
import { Bell, User, LogOut, Check, X } from 'lucide-react'
import { useAuth } from '../../contexts/AuthContext'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import ThemeToggle from '../common/ThemeToggle'
import './Header.css'

const Header = () => {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const { t } = useTranslation('common')
  const [showNotifications, setShowNotifications] = useState(false)
  const notificationRef = useRef(null)

  // Sample notifications data
  // TODO: Replace with WebSocket connection in the future
  const [notifications, setNotifications] = useState([
    {
      id: 1,
      type: 'trade',
      title: 'Trade Executed',
      message: 'Your trade of 100 USDT to SOMI was successful',
      timestamp: new Date(Date.now() - 5 * 60000).toISOString(),
      read: false
    },
    {
      id: 2,
      type: 'account',
      title: 'New Account Created',
      message: 'Account 0x1234...5678 has been created successfully',
      timestamp: new Date(Date.now() - 30 * 60000).toISOString(),
      read: false
    },
    {
      id: 3,
      type: 'alert',
      title: 'Price Alert',
      message: 'SOMI has reached your target price of $2.50',
      timestamp: new Date(Date.now() - 2 * 60 * 60000).toISOString(),
      read: false
    },
    {
      id: 4,
      type: 'system',
      title: 'System Update',
      message: 'New features have been added to the dashboard',
      timestamp: new Date(Date.now() - 24 * 60 * 60000).toISOString(),
      read: true
    },
    {
      id: 5,
      type: 'trade',
      title: 'Trade Failed',
      message: 'Your trade of 50 ETH to USDT failed due to insufficient gas',
      timestamp: new Date(Date.now() - 48 * 60 * 60000).toISOString(),
      read: true
    }
  ])

  const unreadCount = notifications.filter(n => !n.read).length

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const toggleNotifications = () => {
    setShowNotifications(!showNotifications)
  }

  const markAsRead = (id) => {
    setNotifications(prev =>
      prev.map(notif =>
        notif.id === id ? { ...notif, read: true } : notif
      )
    )
  }

  const markAllAsRead = () => {
    setNotifications(prev =>
      prev.map(notif => ({ ...notif, read: true }))
    )
  }

  const deleteNotification = (id) => {
    setNotifications(prev => prev.filter(notif => notif.id !== id))
  }

  const getNotificationIcon = (type) => {
    switch (type) {
      case 'trade':
        return '💱'
      case 'account':
        return '👤'
      case 'alert':
        return '⚠️'
      case 'system':
        return '🔔'
      default:
        return '📢'
    }
  }

  const formatTimestamp = (timestamp) => {
    const now = new Date()
    const time = new Date(timestamp)
    const diff = now - time
    const minutes = Math.floor(diff / 60000)
    const hours = Math.floor(diff / 3600000)
    const days = Math.floor(diff / 86400000)

    if (minutes < 1) return t('time.justNow')
    if (minutes < 60) return `${minutes}m ago`
    if (hours < 24) return `${hours}h ago`
    if (days < 7) return `${days}d ago`
    return time.toLocaleDateString()
  }

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (notificationRef.current && !notificationRef.current.contains(event.target)) {
        setShowNotifications(false)
      }
    }

    if (showNotifications) {
      document.addEventListener('mousedown', handleClickOutside)
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [showNotifications])

  return (
    <header className="header">
      <div className="header-content">
        <div className="header-left">
          <h2 className="page-title">{t('navigation.dashboard')}</h2>
        </div>
        
        <div className="header-right">
          {user && (
            <div className="user-info">
              <span className="user-name">
                {user.first_name} {user.last_name}
              </span>
              {user.username && (
                <span className="user-username">@{user.username}</span>
              )}
            </div>
          )}
          <ThemeToggle />
          
          {/* Notifications */}
          <div className="notification-container" ref={notificationRef}>
            <button 
              className="icon-button notification-button" 
              onClick={toggleNotifications}
              title={t('components:header.notifications')}
            >
              <Bell size={20} />
              {unreadCount > 0 && (
                <span className="notification-badge">{unreadCount}</span>
              )}
            </button>

            {showNotifications && (
              <div className="notification-dropdown">
                <div className="notification-header">
                  <h3>{t('components:header.notifications')}</h3>
                  {unreadCount > 0 && (
                    <button onClick={markAllAsRead} className="mark-all-read">
                      <Check size={16} />
                      {t('components:header.markAllAsRead')}
                    </button>
                  )}
                </div>

                <div className="notification-list">
                  {notifications.length > 0 ? (
                    notifications.map((notif) => (
                      <div
                        key={notif.id}
                        className={`notification-item ${notif.read ? 'read' : 'unread'}`}
                        onClick={() => !notif.read && markAsRead(notif.id)}
                      >
                        <div className="notification-icon">
                          {getNotificationIcon(notif.type)}
                        </div>
                        <div className="notification-content">
                          <div className="notification-title">{notif.title}</div>
                          <div className="notification-message">{notif.message}</div>
                          <div className="notification-time">
                            {formatTimestamp(notif.timestamp)}
                          </div>
                        </div>
                        <button
                          className="notification-delete"
                          onClick={(e) => {
                            e.stopPropagation()
                            deleteNotification(notif.id)
                          }}
                          title={t('components:header.delete')}
                        >
                          <X size={16} />
                        </button>
                      </div>
                    ))
                  ) : (
                    <div className="notification-empty">
                      <p>{t('components:header.noNotifications')}</p>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>

          <button className="icon-button" title={t('components:header.profile')}>
            <User size={20} />
          </button>
          <button className="icon-button logout-button" onClick={handleLogout} title={t('components:header.logout')}>
            <LogOut size={20} />
          </button>
        </div>
      </div>
    </header>
  )
}

export default Header
