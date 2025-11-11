import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Calendar, Clock, CheckCircle } from 'lucide-react';
import { mockAppointments, mockDoctors } from '@/lib/mockData';

const StaffDashboard = () => {
  const todayAppointments = mockAppointments.filter(
    (apt) => apt.date === new Date().toISOString().split('T')[0]
  );

  const stats = [
    {
      title: "Today's Appointments",
      value: todayAppointments.length,
      icon: Calendar,
      gradient: 'from-primary to-secondary',
    },
    {
      title: 'Scheduled',
      value: mockAppointments.filter((a) => a.status === 'scheduled').length,
      icon: Clock,
      gradient: 'from-secondary to-accent',
    },
    {
      title: 'Completed',
      value: mockAppointments.filter((a) => a.status === 'completed').length,
      icon: CheckCircle,
      gradient: 'from-accent to-primary',
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
        <div className="grid gap-6 md:grid-cols-3">
          {stats.map((stat, index) => (
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

        {/* Today's Schedule */}
        <Card className="glass-card">
          <CardHeader>
            <CardTitle>Today's Schedule</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {todayAppointments.map((apt) => {
                const doctor = mockDoctors.find((d) => d.id === apt.doctorId);
                return (
                  <div key={apt.id} className="flex items-center gap-4 p-4 glass rounded-xl">
                    <div className="w-12 h-12 rounded-full overflow-hidden">
                      <img src={doctor?.image} alt={doctor?.name} className="w-full h-full object-cover" />
                    </div>
                    <div className="flex-1">
                      <p className="font-medium">{apt.patientName}</p>
                      <p className="text-sm text-muted-foreground">
                        {doctor?.name} • {apt.service}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="font-medium text-primary">{apt.time}</p>
                      <span className={`text-xs px-2 py-1 rounded-full ${
                        apt.status === 'scheduled' ? 'bg-primary/10 text-primary' :
                        apt.status === 'completed' ? 'bg-success/10 text-success' :
                        'bg-destructive/10 text-destructive'
                      }`}>
                        {apt.status}
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
};

export default StaffDashboard;
