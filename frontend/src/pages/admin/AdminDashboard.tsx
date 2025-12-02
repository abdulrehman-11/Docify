import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Calendar, Users, Activity, TrendingUp, Clock, CheckCircle, XCircle } from 'lucide-react';
import { CalendarView } from '@/components/CalendarView';
import { dashboardApi, DashboardStats, TodayAppointment } from '@/lib/api';
import type { Appointment } from '@/lib/api/types';
import { toast } from 'sonner';
import { format, parseISO } from 'date-fns';
import { parseUTCDate } from '@/lib/dateUtils';

const AdminDashboard = () => {
  const navigate = useNavigate();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [todayAppointments, setTodayAppointments] = useState<TodayAppointment[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      console.log('Loading dashboard data...');
      
      const [statsData, todayData] = await Promise.all([
        dashboardApi.getStats(),
        dashboardApi.getTodayAppointments(),
      ]);
      
      console.log('Stats data:', statsData);
      console.log('Today data:', todayData);
      
      setStats(statsData);
      setTodayAppointments(todayData);
      console.log('Dashboard data loaded successfully');
    } catch (error: any) {
      console.error('Failed to load dashboard data:', error);
      console.error('Error details:', error.response?.data);
      console.error('Error status:', error.response?.status);
      toast.error('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const handleDateClick = (date: Date) => {
    // Navigate to appointments page with date filter
    // Use local date components to avoid timezone conversion issues
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const dateParam = `${year}-${month}-${day}`; // YYYY-MM-DD format in local timezone
    navigate(`/admin/appointments?date=${dateParam}`);
  };

  const handleAppointmentClick = (appointment: Appointment) => {
    // Navigate to appointments page
    navigate('/admin/appointments');
  };

  const statsCards = stats ? [
    {
      title: "Today's Appointments",
      value: stats.total_appointments_today,
      icon: Calendar,
      gradient: 'from-primary to-secondary',
      change: `${stats.total_appointments_today} total`,
    },
    {
      title: 'Total Patients',
      value: stats.total_patients,
      icon: Users,
      gradient: 'from-secondary to-accent',
      change: `${stats.total_patients} registered`,
    },
    {
      title: 'Completed',
      value: stats.completed_appointments,
      icon: CheckCircle,
      gradient: 'from-accent to-primary',
      change: `${stats.completed_appointments} total`,
    },
    {
      title: 'Upcoming',
      value: stats.total_appointments_upcoming,
      icon: TrendingUp,
      gradient: 'from-primary to-accent',
      change: `${stats.total_appointments_upcoming} scheduled`,
    },
  ] : [];

  if (loading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-96">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
            <p className="mt-4 text-muted-foreground">Loading dashboard...</p>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="space-y-6 animate-fade-in">
        <div>
          <h1 className="text-3xl font-bold mb-2">Admin Dashboard</h1>
          <p className="text-muted-foreground">Welcome back! Here's your clinic overview.</p>
        </div>

        {/* Stats Grid */}
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
          {statsCards.map((stat, index) => (
            <Card key={index} className="glass-card hover-lift overflow-hidden">
              <CardContent className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className={`p-3 rounded-xl bg-gradient-to-br ${stat.gradient}`}>
                    <stat.icon className="w-6 h-6 text-white" />
                  </div>
                  <span className="text-sm font-medium text-muted-foreground">{stat.change}</span>
                </div>
                <div className="text-2xl font-bold mb-1">{stat.value}</div>
                <div className="text-sm text-muted-foreground">{stat.title}</div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Calendar View */}
        <CalendarView 
          onDateClick={handleDateClick}
          onAppointmentClick={handleAppointmentClick}
        />

        {/* Today's Appointments */}
        <div className="grid gap-6 lg:grid-cols-2">
          <Card className="glass-card">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Calendar className="w-5 h-5" />
                Today's Appointments
              </CardTitle>
            </CardHeader>
            <CardContent>
              {todayAppointments.length === 0 ? (
                <p className="text-muted-foreground text-center py-4">No appointments today</p>
              ) : (
                <div className="space-y-4">
                  {todayAppointments.slice(0, 5).map((apt) => {
                    // Safely parse the time
                    let timeDisplay = 'Time not available';
                    try {
                      const startTime = parseUTCDate(apt.start_time);
                      const endTime = parseUTCDate(apt.end_time);
                      timeDisplay = `${format(startTime, 'h:mm a')} - ${format(endTime, 'h:mm a')}`;
                    } catch (e) {
                      console.error('Error parsing appointment time:', e);
                    }
                    
                    return (
                      <div key={apt.id} className="flex items-start gap-3 p-3 glass rounded-xl">
                        <Clock className="w-4 h-4 mt-1 text-primary" />
                        <div className="flex-1">
                          <p className="font-medium text-sm">{apt.patient_name}</p>
                          <p className="text-xs text-muted-foreground">{apt.reason}</p>
                          <p className="text-xs text-muted-foreground mt-1 flex items-center gap-1">
                            <Calendar className="w-3 h-3" />
                            {timeDisplay}
                          </p>
                        </div>
                        <span className={`text-xs px-2 py-1 rounded ${
                          apt.status === 'CONFIRMED' ? 'bg-blue-500/20 text-blue-500' :
                          apt.status === 'COMPLETED' ? 'bg-green-500/20 text-green-500' :
                          apt.status === 'CANCELLED' ? 'bg-red-500/20 text-red-500' :
                          'bg-gray-500/20 text-gray-500'
                        }`}>
                          {apt.status}
                        </span>
                      </div>
                    );
                  })}
                  {todayAppointments.length > 5 && (
                    <p className="text-xs text-center text-muted-foreground">
                      +{todayAppointments.length - 5} more appointments
                    </p>
                  )}
                </div>
              )}
            </CardContent>
          </Card>

          <Card className="glass-card">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Activity className="w-5 h-5" />
                Statistics Summary
              </CardTitle>
            </CardHeader>
            <CardContent>
              {stats && (
                <div className="space-y-4">
                  <div className="flex justify-between items-center p-3 glass rounded-xl">
                    <span className="text-sm text-muted-foreground">Confirmed</span>
                    <span className="font-medium">{stats.confirmed_appointments}</span>
                  </div>
                  <div className="flex justify-between items-center p-3 glass rounded-xl">
                    <span className="text-sm text-muted-foreground">Cancelled</span>
                    <span className="font-medium text-red-500">{stats.cancelled_appointments}</span>
                  </div>
                  <div className="flex justify-between items-center p-3 glass rounded-xl">
                    <span className="text-sm text-muted-foreground">Completed</span>
                    <span className="font-medium text-green-500">{stats.completed_appointments}</span>
                  </div>
                  <div className="flex justify-between items-center p-3 glass rounded-xl">
                    <span className="text-sm text-muted-foreground">Total Patients</span>
                    <span className="font-medium">{stats.total_patients}</span>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </DashboardLayout>
  );
};

export default AdminDashboard;
