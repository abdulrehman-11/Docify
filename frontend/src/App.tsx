import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { ProtectedRoute } from "./components/ProtectedRoute";
import { NotificationProvider } from "./contexts/NotificationContext";
import { FloatingNotificationsContainer } from "./components/FloatingNotification";
import { useNotifications } from "./contexts/NotificationContext";
import { useState, useEffect } from "react";
import Landing from "./pages/Landing";
import Login from "./pages/Login";
import AdminDashboard from "./pages/admin/AdminDashboard";
import StaffDashboard from "./pages/staff/StaffDashboard";
import AdminAppointments from "./pages/admin/Appointments";
import Patients from "./pages/admin/Patients";
import Clinic from "./pages/admin/Clinic";
import Staff from "./pages/admin/Staff";
import StaffAppointments from "./pages/staff/Appointments";
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient();

// Wrapper to access notification context
const AppContent = () => {
  const { floatingNotifications, dismissFloatingNotification } = useNotifications();
  
  return (
    <>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/login" element={<Login />} />
        
        {/* Admin Routes */}
        <Route
          path="/admin/dashboard"
          element={
            <ProtectedRoute allowedRoles={['admin']}>
              <AdminDashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin/appointments"
          element={
            <ProtectedRoute allowedRoles={['admin']}>
              <AdminAppointments />
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin/patients"
          element={
            <ProtectedRoute allowedRoles={['admin']}>
              <Patients />
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin/clinic"
          element={
            <ProtectedRoute allowedRoles={['admin']}>
              <Clinic />
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin/staff"
          element={
            <ProtectedRoute allowedRoles={['admin']}>
              <Staff />
            </ProtectedRoute>
          }
        />
        
        {/* Staff Routes */}
        <Route
          path="/staff/dashboard"
          element={
            <ProtectedRoute allowedRoles={['staff']}>
              <StaffDashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/staff/appointments"
          element={
            <ProtectedRoute allowedRoles={['staff']}>
              <StaffAppointments />
            </ProtectedRoute>
          }
        />
        
        <Route path="*" element={<NotFound />} />
      </Routes>

      {/* Floating Notifications */}
      <FloatingNotificationsContainer
        notifications={floatingNotifications}
        onDismiss={dismissFloatingNotification}
      />
    </>
  );
};

const App = () => {
  // Get user role from sessionStorage and make it reactive
  const [userRole, setUserRole] = useState<'admin' | 'staff' | undefined>(() => {
    const userStr = sessionStorage.getItem('user');
    if (userStr) {
      try {
        const user = JSON.parse(userStr);
        return user.role as 'admin' | 'staff';
      } catch {
        return undefined;
      }
    }
    return undefined;
  });

  // Listen for storage changes (login/logout)
  useEffect(() => {
    const handleStorageChange = () => {
      const userStr = sessionStorage.getItem('user');
      if (userStr) {
        try {
          const user = JSON.parse(userStr);
          setUserRole(user.role as 'admin' | 'staff');
        } catch {
          setUserRole(undefined);
        }
      } else {
        setUserRole(undefined);
      }
    };

    // Listen for custom storage event
    window.addEventListener('storage', handleStorageChange);
    
    // Create a custom event for session storage changes in the same tab
    const originalSetItem = sessionStorage.setItem;
    sessionStorage.setItem = function(key: string, value: string) {
      originalSetItem.apply(this, [key, value]);
      if (key === 'user') {
        handleStorageChange();
      }
    };

    return () => {
      window.removeEventListener('storage', handleStorageChange);
      sessionStorage.setItem = originalSetItem;
    };
  }, []);
  
  return (
    <QueryClientProvider client={queryClient}>
      <TooltipProvider>
        <Toaster />
        <Sonner />
        <BrowserRouter>
          <NotificationProvider userRole={userRole}>
            <AppContent />
          </NotificationProvider>
        </BrowserRouter>
      </TooltipProvider>
    </QueryClientProvider>
  );
};

export default App;
