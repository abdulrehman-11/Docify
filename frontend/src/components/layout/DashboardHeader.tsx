import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { LogOut, Bell } from 'lucide-react';
import { logout } from '@/lib/auth';
import { useNavigate } from 'react-router-dom';
import { toast } from 'sonner';
import { useNotifications } from '@/contexts/NotificationContext';
import { NotificationPanel } from '@/components/NotificationPanel';

export const DashboardHeader = () => {
  const navigate = useNavigate();
  const { unreadCount } = useNotifications();
  const [showNotifications, setShowNotifications] = useState(false);

  const handleLogout = () => {
    logout();
    toast.success('Logged out successfully');
    navigate('/login');
  };

  return (
    <>
      <header className="glass-card border-b border-white/20 px-6 py-4">
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-bold text-foreground">Control Panel</h2>
          
          <div className="flex items-center gap-3">
            {/* Notification Bell */}
            <Button
              variant="outline"
              size="icon"
              onClick={() => setShowNotifications(true)}
              className="glass hover:bg-primary/10 relative"
            >
              <Bell className="w-5 h-5" />
              {unreadCount > 0 && (
                <Badge
                  variant="destructive"
                  className="absolute -top-1 -right-1 h-5 w-5 p-0 flex items-center justify-center text-xs"
                >
                  {unreadCount > 9 ? '9+' : unreadCount}
                </Badge>
              )}
            </Button>

            {/* Logout Button */}
            <Button
              variant="outline"
              onClick={handleLogout}
              className="glass hover:bg-destructive/10 hover:text-destructive"
            >
              <LogOut className="w-4 h-4 mr-2" />
              Logout
            </Button>
          </div>
        </div>
      </header>

      {/* Notification Panel */}
      <NotificationPanel open={showNotifications} onOpenChange={setShowNotifications} />
    </>
  );
};
