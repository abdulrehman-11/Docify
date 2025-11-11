import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Calendar, Users, Activity, TrendingUp, Clock, CheckCircle, XCircle } from 'lucide-react';
import { mockAppointments, mockDoctors, mockAuditLogs } from '@/lib/mockData';

const AdminDashboard = () => {
  const todayAppointments = mockAppointments.filter(
    (apt) => apt.date === new Date().toISOString().split('T')[0]
  );
  const cancelledToday = mockAppointments.filter(
    (apt) => apt.status === 'cancelled' && apt.date === new Date().toISOString().split('T')[0]
  );

  const stats = [
    {
      title: "Today's Appointments",
      value: todayAppointments.length,
      icon: Calendar,
      gradient: 'from-primary to-secondary',
      change: '+12%',
    },
    {
      title: 'Active Providers',
      value: mockDoctors.length,
      icon: Users,
      gradient: 'from-secondary to-accent',
      change: '+2',
    },
    {
      title: 'Completed Today',
      value: mockAppointments.filter((a) => a.status === 'completed').length,
      icon: CheckCircle,
      gradient: 'from-accent to-primary',
      change: '+8',
    },
    {
      title: 'Cancellations',
      value: cancelledToday.length,
      icon: XCircle,
      gradient: 'from-destructive to-accent',
      change: '-3',
    },
  ];

  return (
    <DashboardLayout>
      <div className="space-y-6 animate-fade-in">
        <div>
          <h1 className="text-3xl font-bold mb-2">Admin Dashboard</h1>
          <p className="text-muted-foreground">Welcome back! Here's your clinic overview.</p>
        </div>

        {/* Stats Grid */}
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
          {stats.map((stat, index) => (
            <Card key={index} className="glass-card hover-lift overflow-hidden">
              <CardContent className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className={`p-3 rounded-xl bg-gradient-to-br ${stat.gradient}`}>
                    <stat.icon className="w-6 h-6 text-white" />
                  </div>
                  <span className="text-sm font-medium text-success">{stat.change}</span>
                </div>
                <div className="text-2xl font-bold mb-1">{stat.value}</div>
                <div className="text-sm text-muted-foreground">{stat.title}</div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Recent Activity */}
        <div className="grid gap-6 lg:grid-cols-2">
          <Card className="glass-card">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Activity className="w-5 h-5" />
                Recent Activity
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {mockAuditLogs.slice(0, 5).map((log) => (
                  <div key={log.id} className="flex items-start gap-3 p-3 glass rounded-xl">
                    <Clock className="w-4 h-4 mt-1 text-primary" />
                    <div className="flex-1">
                      <p className="font-medium text-sm">{log.action}</p>
                      <p className="text-xs text-muted-foreground">{log.details}</p>
                      <p className="text-xs text-muted-foreground mt-1">
                        by {log.user} • {new Date(log.timestamp).toLocaleString()}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          <Card className="glass-card">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="w-5 h-5" />
                Upcoming Appointments
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {mockAppointments.slice(0, 5).map((apt) => {
                  const doctor = mockDoctors.find((d) => d.id === apt.doctorId);
                  return (
                    <div key={apt.id} className="flex items-start gap-3 p-3 glass rounded-xl">
                      <div className="w-10 h-10 rounded-full overflow-hidden">
                        <img src={doctor?.image} alt={doctor?.name} className="w-full h-full object-cover" />
                      </div>
                      <div className="flex-1">
                        <p className="font-medium text-sm">{apt.patientName}</p>
                        <p className="text-xs text-muted-foreground">
                          {doctor?.name} • {apt.service}
                        </p>
                        <p className="text-xs text-primary mt-1">
                          {apt.date} at {apt.time}
                        </p>
                      </div>
                    </div>
                  );
                })}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </DashboardLayout>
  );
};

export default AdminDashboard;
