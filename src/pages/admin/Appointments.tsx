import { useState, useEffect } from 'react';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { Calendar } from '@/components/Calendar';
import { AppointmentDialog } from '@/components/AppointmentDialog';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle } from '@/components/ui/alert-dialog';
import { Plus, Clock, User, Phone, Mail, Star, Calendar as CalendarIcon, X, Edit, Check } from 'lucide-react';
import { Doctor, Appointment } from '@/lib/mockData';
import { getDoctors, getAppointments, saveAppointment, updateAppointmentStatus, deleteAppointment } from '@/lib/storage';
import { format, isSameDay } from 'date-fns';
import { toast } from 'sonner';
import { cn } from '@/lib/utils';

const Appointments = () => {
  const [doctors, setDoctors] = useState<Doctor[]>([]);
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [selectedDoctor, setSelectedDoctor] = useState<Doctor | null>(null);
  const [selectedDate, setSelectedDate] = useState<Date>(new Date());
  const [dialogOpen, setDialogOpen] = useState(false);
  const [selectedAppointment, setSelectedAppointment] = useState<Appointment | undefined>();
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [appointmentToDelete, setAppointmentToDelete] = useState<string | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = () => {
    const doctorData = getDoctors();
    const appointmentData = getAppointments();
    setDoctors(doctorData);
    setAppointments(appointmentData);
    if (doctorData.length > 0 && !selectedDoctor) {
      setSelectedDoctor(doctorData[0]);
    }
  };

  const getTodayAppointments = () => {
    if (!selectedDoctor) return [];
    return appointments.filter(
      (apt) =>
        apt.doctorId === selectedDoctor.id &&
        isSameDay(new Date(apt.date), selectedDate) &&
        apt.status !== 'cancelled'
    ).sort((a, b) => a.time.localeCompare(b.time));
  };

  const handleSaveAppointment = (appointment: Appointment) => {
    saveAppointment(appointment);
    loadData();
  };

  const handleEditAppointment = (appointment: Appointment) => {
    setSelectedAppointment(appointment);
    setDialogOpen(true);
  };

  const handleNewAppointment = () => {
    setSelectedAppointment(undefined);
    setDialogOpen(true);
  };

  const handleCancelAppointment = (id: string) => {
    setAppointmentToDelete(id);
    setDeleteDialogOpen(true);
  };

  const confirmCancelAppointment = () => {
    if (appointmentToDelete) {
      updateAppointmentStatus(appointmentToDelete, 'cancelled');
      loadData();
      toast.success('Appointment cancelled successfully');
    }
    setDeleteDialogOpen(false);
    setAppointmentToDelete(null);
  };

  const handleCompleteAppointment = (id: string) => {
    updateAppointmentStatus(id, 'completed');
    loadData();
    toast.success('Appointment marked as completed');
  };

  const getStatusColor = (status: Appointment['status']) => {
    switch (status) {
      case 'scheduled':
        return 'bg-blue-500';
      case 'completed':
        return 'bg-green-500';
      case 'cancelled':
        return 'bg-red-500';
      default:
        return 'bg-gray-500';
    }
  };

  const todayAppointments = getTodayAppointments();

  return (
    <DashboardLayout>
      <div className="space-y-6 animate-fade-in">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Appointments</h1>
            <p className="text-muted-foreground mt-2">Manage appointments for all providers</p>
          </div>
          {selectedDoctor && (
            <Button onClick={handleNewAppointment} className="bg-primary hover-lift">
              <Plus className="w-4 h-4 mr-2" />
              New Appointment
            </Button>
          )}
        </div>

        <div className="grid lg:grid-cols-12 gap-6">
          {/* Doctor Sidebar */}
          <div className="lg:col-span-3 space-y-4">
            <Card className="glass-card">
              <CardHeader>
                <CardTitle className="text-lg">Providers</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                {doctors.map((doctor) => (
                  <button
                    key={doctor.id}
                    onClick={() => setSelectedDoctor(doctor)}
                    className={cn(
                      'w-full p-3 rounded-xl transition-all hover-lift text-left',
                      selectedDoctor?.id === doctor.id
                        ? 'bg-primary text-primary-foreground'
                        : 'bg-muted/50 hover:bg-muted'
                    )}
                  >
                    <div className="flex items-center gap-3">
                      <Avatar className="w-12 h-12 ring-2 ring-white/20">
                        <AvatarImage src={doctor.image} alt={doctor.name} />
                        <AvatarFallback>{doctor.name.charAt(0)}</AvatarFallback>
                      </Avatar>
                      <div className="flex-1 min-w-0">
                        <p className="font-medium truncate">{doctor.name}</p>
                        <p className={cn(
                          "text-xs truncate",
                          selectedDoctor?.id === doctor.id ? 'text-primary-foreground/80' : 'text-muted-foreground'
                        )}>
                          {doctor.specialty}
                        </p>
                      </div>
                    </div>
                  </button>
                ))}
              </CardContent>
            </Card>

            {/* Selected Doctor Info */}
            {selectedDoctor && (
              <Card className="glass-card">
                <CardContent className="pt-6 space-y-4">
                  <div className="text-center">
                    <Avatar className="w-24 h-24 mx-auto ring-4 ring-primary/20 mb-3">
                      <AvatarImage src={selectedDoctor.image} alt={selectedDoctor.name} />
                      <AvatarFallback>{selectedDoctor.name.charAt(0)}</AvatarFallback>
                    </Avatar>
                    <h3 className="font-bold text-lg">{selectedDoctor.name}</h3>
                    <p className="text-sm text-muted-foreground">{selectedDoctor.specialty}</p>
                    <div className="flex items-center justify-center gap-1 mt-2">
                      <Star className="w-4 h-4 fill-yellow-400 text-yellow-400" />
                      <span className="font-medium">{selectedDoctor.rating}</span>
                      <span className="text-xs text-muted-foreground">({selectedDoctor.reviews} reviews)</span>
                    </div>
                  </div>

                  <div className="space-y-2 pt-4 border-t">
                    <p className="text-sm text-muted-foreground">{selectedDoctor.bio}</p>
                    <div className="space-y-1 text-sm">
                      <div className="flex items-center gap-2">
                        <Mail className="w-4 h-4 text-primary" />
                        <span className="text-xs">{selectedDoctor.email}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <Phone className="w-4 h-4 text-primary" />
                        <span className="text-xs">{selectedDoctor.phone}</span>
                      </div>
                    </div>
                  </div>

                  <div className="pt-4 border-t">
                    <p className="text-sm font-medium mb-2">Schedule</p>
                    <div className="space-y-1">
                      {selectedDoctor.schedule.map((sched, idx) => (
                        <div key={idx} className="flex justify-between text-xs">
                          <span className="text-muted-foreground">{sched.day}</span>
                          <span className="font-medium">{sched.startTime} - {sched.endTime}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>

          {/* Main Content */}
          <div className="lg:col-span-9 space-y-6">
            {selectedDoctor ? (
              <>
                {/* Calendar */}
                <Calendar
                  appointments={appointments}
                  selectedDate={selectedDate}
                  onDateSelect={setSelectedDate}
                  doctorId={selectedDoctor.id}
                />

                {/* Today's Appointments */}
                <Card className="glass-card">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <CalendarIcon className="w-5 h-5" />
                      Appointments for {format(selectedDate, 'MMMM d, yyyy')}
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    {todayAppointments.length === 0 ? (
                      <div className="text-center py-12">
                        <CalendarIcon className="w-12 h-12 text-muted-foreground mx-auto mb-3 opacity-50" />
                        <p className="text-muted-foreground">No appointments scheduled for this day</p>
                        <Button onClick={handleNewAppointment} variant="outline" className="mt-4 hover-lift">
                          <Plus className="w-4 h-4 mr-2" />
                          Add Appointment
                        </Button>
                      </div>
                    ) : (
                      <div className="space-y-3">
                        {todayAppointments.map((appointment) => (
                          <div
                            key={appointment.id}
                            className="glass p-4 rounded-xl hover-lift transition-all"
                          >
                            <div className="flex items-start justify-between">
                              <div className="flex-1">
                                <div className="flex items-center gap-3 mb-2">
                                  <div className="flex items-center gap-2">
                                    <Clock className="w-4 h-4 text-primary" />
                                    <span className="font-medium">{appointment.time}</span>
                                  </div>
                                  <Badge className={getStatusColor(appointment.status)}>
                                    {appointment.status}
                                  </Badge>
                                </div>
                                <div className="space-y-1">
                                  <div className="flex items-center gap-2">
                                    <User className="w-4 h-4 text-muted-foreground" />
                                    <span className="font-medium">{appointment.patientName}</span>
                                  </div>
                                  <div className="flex items-center gap-2 text-sm text-muted-foreground">
                                    <Mail className="w-3 h-3" />
                                    <span>{appointment.patientEmail}</span>
                                  </div>
                                  <div className="flex items-center gap-2 text-sm text-muted-foreground">
                                    <Phone className="w-3 h-3" />
                                    <span>{appointment.patientPhone}</span>
                                  </div>
                                  <div className="mt-2">
                                    <Badge variant="outline">{appointment.service}</Badge>
                                  </div>
                                  {appointment.notes && (
                                    <p className="text-sm text-muted-foreground mt-2 italic">
                                      Note: {appointment.notes}
                                    </p>
                                  )}
                                </div>
                              </div>
                              {appointment.status === 'scheduled' && (
                                <div className="flex flex-col gap-2">
                                  <Button
                                    size="sm"
                                    variant="outline"
                                    onClick={() => handleEditAppointment(appointment)}
                                    className="hover-lift"
                                  >
                                    <Edit className="w-3 h-3 mr-1" />
                                    Edit
                                  </Button>
                                  <Button
                                    size="sm"
                                    variant="outline"
                                    onClick={() => handleCompleteAppointment(appointment.id)}
                                    className="hover-lift text-green-600 hover:bg-green-50"
                                  >
                                    <Check className="w-3 h-3 mr-1" />
                                    Complete
                                  </Button>
                                  <Button
                                    size="sm"
                                    variant="outline"
                                    onClick={() => handleCancelAppointment(appointment.id)}
                                    className="hover-lift text-red-600 hover:bg-red-50"
                                  >
                                    <X className="w-3 h-3 mr-1" />
                                    Cancel
                                  </Button>
                                </div>
                              )}
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </CardContent>
                </Card>
              </>
            ) : (
              <Card className="glass-card">
                <CardContent className="text-center py-12">
                  <User className="w-12 h-12 text-muted-foreground mx-auto mb-3 opacity-50" />
                  <p className="text-muted-foreground">Please select a provider to view appointments</p>
                </CardContent>
              </Card>
            )}
          </div>
        </div>

        {/* Appointment Dialog */}
        {selectedDoctor && (
          <AppointmentDialog
            open={dialogOpen}
            onOpenChange={setDialogOpen}
            appointment={selectedAppointment}
            doctorId={selectedDoctor.id}
            doctorName={selectedDoctor.name}
            selectedDate={selectedDate}
            onSave={handleSaveAppointment}
          />
        )}

        {/* Delete Confirmation Dialog */}
        <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
          <AlertDialogContent className="glass-card">
            <AlertDialogHeader>
              <AlertDialogTitle>Cancel Appointment?</AlertDialogTitle>
              <AlertDialogDescription>
                This will cancel the appointment. This action can be reversed by editing the appointment status later.
              </AlertDialogDescription>
            </AlertDialogHeader>
            <AlertDialogFooter>
              <AlertDialogCancel>No, keep it</AlertDialogCancel>
              <AlertDialogAction onClick={confirmCancelAppointment} className="bg-destructive">
                Yes, cancel appointment
              </AlertDialogAction>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialog>
      </div>
    </DashboardLayout>
  );
};

export default Appointments;

