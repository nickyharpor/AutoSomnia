import { NavLink } from 'react-router-dom'
import { 
  LayoutDashboard, 
  Wallet, 
  TrendingUp, 
  BarChart3, 
  Settings 
} from 'lucide-react'
import { useTranslation } from 'react-i18next'
import './Sidebar.css'

const Sidebar = () => {
  const { t } = useTranslation('common')
  
  const navItems = [
    { path: '/', icon: LayoutDashboard, label: t('navigation.dashboard') },
    { path: '/portfolio', icon: Wallet, label: t('navigation.portfolio') },
    { path: '/trades', icon: TrendingUp, label: t('navigation.trades') },
    { path: '/analytics', icon: BarChart3, label: t('navigation.analytics') },
    { path: '/settings', icon: Settings, label: t('navigation.settings') },
  ]

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <h1 className="sidebar-title">{t('app.name')}</h1>
        <p className="sidebar-subtitle">{t('app.tagline')}</p>
      </div>
      
      <nav className="sidebar-nav">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) => 
              `nav-item ${isActive ? 'active' : ''}`
            }
          >
            <item.icon size={20} />
            <span>{item.label}</span>
          </NavLink>
        ))}
      </nav>
    </aside>
  )
}

export default Sidebar
