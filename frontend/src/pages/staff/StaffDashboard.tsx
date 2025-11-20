import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Calendar, Clock, CheckCircle, Users } from 'lucide-react';
import { CalendarView } from '@/components/CalendarView';
import { dashboardApi } from '@/lib/api';
import type { DashboardStats, TodayAppointment, Appointment } from '@/lib/api/types';
import { toast } from 'sonner';
import { format, parseISO } from 'date-fns';
import { parseUTCDate } from '@/lib/dateUtils';

const StaffDashboard = () => {
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
      const data = await dashboardApi.getStats();
      setStats(data);
      
      // Get today's appointments from the dashboard API
      const today = await dashboardApi.getTodayAppointments();
      setTodayAppointments(today);
    } catch (error: any) {
      toast.error('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const handleDateClick = (date: Date) => {
    // Navigate to appointments page with date filter
    const dateParam = date.toISOString().split('T')[0];
    navigate(`/staff/appointments?date=${dateParam}`);
  };

  const handleAppointmentClick = (appointment: Appointment) => {
    // Navigate to appointments page
    navigate('/staff/appointments');
  };

  const getStatusBadge = (status: string) => {
    const statusStyles = {
      CONFIRMED: 'bg-blue-500/10 text-blue-500',
      COMPLETED: 'bg-green-500/10 text-green-500',
      CANCELLED: 'bg-red-500/10 text-red-500',
      RESCHEDULED: 'bg-yellow-500/10 text-yellow-500',
    };
    return statusStyles[status as keyof typeof statusStyles] || 'bg-gray-500/10 text-gray-500';
  };

  if (loading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-64">
          <p className="text-muted-foreground">Loading...</p>
        </div>
      </DashboardLayout>
    );
  }

  const statsCards = [
    {
      title: "Today's Appointments",
      value: stats?.total_appointments_today || 0,
      icon: Calendar,
      gradient: 'from-primary to-secondary',
    },
    {
      title: 'Upcoming',
      value: stats?.total_appointments_upcoming || 0,
      icon: Clock,
      gradient: 'from-secondary to-accent',
    },
    {
      title: 'Completed',
      value: stats?.completed_appointments || 0,
      icon: CheckCircle,
      gradient: 'from-accent to-primary',
    },
    {
      title: 'Total Patients',
      value: stats?.total_patients || 0,
      icon: Users,
      gradient: 'from-primary to-accent',
    },
  ];

  return (
    <DashboardLayout>
      <div className="space-y-6 animate-fade-in">
        <div>
          <h1 className="text-3xl font-bold mb-2">Staff Dashboard</h1>
          <p className="text-muted-foreground">Manage appointments and patient schedules.</p>
        </div>

        {/* Stats Grid */}
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
          {statsCards.map((stat, index) => (
            <Card key={index} className="glass-card hover-lift">
              <CardContent className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className={`p-3 rounded-xl bg-gradient-to-br ${stat.gradient}`}>
                    <stat.icon className="w-6 h-6 text-white" />
                  </div>
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

        {/* Today's Schedule */}
        <Card className="glass-card">
          <CardHeader>
            <CardTitle>Today's Schedule</CardTitle>
          </CardHeader>
          <CardContent>
            {todayAppointments.length === 0 ? (
              <p className="text-center text-muted-foreground py-8">
                No appointments scheduled for today
              </p>
            ) : (
              <div className="space-y-4">
                {todayAppointments.map((apt) => (
                  <div key={apt.id} className="flex items-center gap-4 p-4 glass rounded-xl">
                    <div className="flex-1">
                      <p className="font-medium">{apt.patient_name}</p>
                      <p className="text-sm text-muted-foreground">{apt.reason}</p>
                    </div>
                    <div className="text-right">
                      <p className="font-medium text-primary">
                        {format(parseUTCDate(apt.start_time), 'h:mm a')} - {format(parseUTCDate(apt.end_time), 'h:mm a')}
                      </p>
                      <span className={`text-xs px-2 py-1 rounded-full ${getStatusBadge(apt.status)}`}>
                        {apt.status}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
};

export default StaffDashboard;
