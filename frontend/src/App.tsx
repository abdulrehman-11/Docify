import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { ProtectedRoute } from "./components/ProtectedRoute";
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

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
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
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
