import { Navigate } from 'react-router-dom';
import { getCurrentUser, UserRole } from '@/lib/auth';
import { ReactNode } from 'react';

interface ProtectedRouteProps {
  children: ReactNode;
  allowedRoles?: UserRole[];
}

export const ProtectedRoute = ({ children, allowedRoles }: ProtectedRouteProps) => {
  const user = getCurrentUser();

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  if (allowedRoles && !allowedRoles.includes(user.role)) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="glass-card p-8 rounded-2xl text-center max-w-md">
          <h1 className="text-3xl font-bold text-destructive mb-4">Access Denied</h1>
          <p className="text-muted-foreground mb-6">
            You don't have permission to access this page.
          </p>
          <a href={user.role === 'admin' ? '/admin/dashboard' : '/staff/dashboard'}>
            <button className="px-6 py-2 rounded-xl bg-primary text-white hover:opacity-90">
              Go to Dashboard
            </button>
          </a>
        </div>
      </div>
    );
  }

  return <>{children}</>;
};
