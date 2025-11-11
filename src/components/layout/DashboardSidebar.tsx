import { NavLink } from 'react-router-dom';
import { getCurrentUser } from '@/lib/auth';
import { 
  LayoutDashboard, 
  Calendar, 
  Building2, 
  Users, 
  Briefcase, 
  BookOpen, 
  Bell, 
  ClipboardList,
  Stethoscope
} from 'lucide-react';
import { cn } from '@/lib/utils';

export const DashboardSidebar = () => {
  const user = getCurrentUser();
  const isAdmin = user?.role === 'admin';
  const baseRoute = isAdmin ? '/admin' : '/staff';

  const navItems = [
    { icon: LayoutDashboard, label: 'Dashboard', path: `${baseRoute}/dashboard` },
    { icon: Calendar, label: 'Appointments', path: `${baseRoute}/appointments` },
    ...(isAdmin ? [
      { icon: Building2, label: 'Clinic Info', path: '/admin/clinic' },
      { icon: Users, label: 'Providers', path: '/admin/providers' },
      { icon: Briefcase, label: 'Services', path: '/admin/services' },
      { icon: BookOpen, label: 'Knowledge Base', path: '/admin/knowledge' },
      { icon: Bell, label: 'Notifications', path: '/admin/notifications' },
      { icon: ClipboardList, label: 'Audit Log', path: '/admin/audit' },
    ] : []),
  ];

  return (
    <>
      {/* Mobile sidebar toggle would go here */}
      <aside className="fixed left-0 top-0 z-40 h-screen w-64 glass-card border-r border-white/20 hidden lg:block">
        <div className="flex h-full flex-col gap-6 p-6">
          <div className="flex items-center gap-2">
            <div className="p-2 rounded-xl bg-gradient-to-br from-primary to-secondary">
              <Stethoscope className="w-6 h-6 text-white" />
            </div>
            <span className="text-lg font-bold bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">
              HealthCare Plus
            </span>
          </div>

          <nav className="flex-1 space-y-2">
            {navItems.map((item) => (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  cn(
                    'flex items-center gap-3 px-4 py-3 rounded-xl transition-all hover-lift',
                    isActive
                      ? 'bg-gradient-to-r from-primary to-secondary text-white shadow-lg'
                      : 'text-foreground hover:bg-white/50'
                  )
                }
              >
                <item.icon className="w-5 h-5" />
                <span className="font-medium">{item.label}</span>
              </NavLink>
            ))}
          </nav>

          <div className="glass-card p-4 rounded-xl">
            <p className="text-sm font-medium">{user?.name}</p>
            <p className="text-xs text-muted-foreground">{user?.role.toUpperCase()}</p>
          </div>
        </div>
      </aside>
    </>
  );
};
