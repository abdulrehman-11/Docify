import { Button } from '@/components/ui/button';
import { LogOut } from 'lucide-react';
import { logout } from '@/lib/auth';
import { useNavigate } from 'react-router-dom';
import { toast } from 'sonner';

export const DashboardHeader = () => {
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    toast.success('Logged out successfully');
    navigate('/login');
  };

  return (
    <header className="glass-card border-b border-white/20 px-6 py-4">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-foreground">Control Panel</h2>
        <Button
          variant="outline"
          onClick={handleLogout}
          className="glass hover:bg-destructive/10 hover:text-destructive"
        >
          <LogOut className="w-4 h-4 mr-2" />
          Logout
        </Button>
      </div>
    </header>
  );
};
