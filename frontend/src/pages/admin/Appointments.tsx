import { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Plus, Calendar as CalendarIcon, Clock, User, X, Search, AlertCircle, Info } from 'lucide-react';
import { appointmentApi, patientApi } from '@/lib/api';
import type { Appointment, Patient, AppointmentCreate, AppointmentUpdate } from '@/lib/api/types';
import { toast } from 'sonner';
import { format, parseISO } from 'date-fns';
import { parseUTCDate, formatBackendDate, utcToLocalDateTime, localDateTimeToUTC } from '@/lib/dateUtils';
import { validateAppointmentTime, getClinicHoursForDate, getClinicSchedule, type ValidationResult } from '@/lib/clinicValidation';

const Appointments = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [patients, setPatients] = useState<Patient[]>([]);
  const [loading, setLoading] = useState(true);
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [selectedDate, setSelectedDate] = useState<string | null>(
    searchParams.get('date')
  );

  // Dialog states
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [isCancelDialogOpen, setIsCancelDialogOpen] = useState(false);

  // Form states
  const [formData, setFormData] = useState<{
    patient_id: number | null;
    start_time: string;
    end_time: string;
    reason: string;
    cancellation_reason?: string;
  }>({
    patient_id: null,
    start_time: '',
    end_time: '',
    reason: '',
    cancellation_reason: '',
  });
  const [selectedAppointment, setSelectedAppointment] = useState<Appointment | null>(null);
  const [cancellationReason, setCancellationReason] = useState('');

  // Clinic validation states
  const [validationError, setValidationError] = useState<string | null>(null);
  const [clinicHoursInfo, setClinicHoursInfo] = useState<string | null>(null);
  const [isValidating, setIsValidating] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [appointmentsData, patientsData] = await Promise.all([
        appointmentApi.getAll(),
        patientApi.getAll(),
      ]);
      
      setAppointments(appointmentsData.appointments);
      setPatients(patientsData.patients);
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setFormData({
      patient_id: null,
      start_time: '',
      end_time: '',
      reason: '',
    });
    setSelectedAppointment(null);
    setValidationError(null);
    setClinicHoursInfo(null);
  };

  // Validate appointment time when start_time changes
  const validateAndUpdateTime = async (startTime: string, endTime: string) => {
    if (!startTime) {
      setValidationError(null);
      setClinicHoursInfo(null);
      return;
    }

    setIsValidating(true);
    try {
      const startDate = new Date(startTime);
      const endDate = endTime ? new Date(endTime) : null;
      
      // Calculate duration in minutes
      const durationMinutes = endDate ? Math.round((endDate.getTime() - startDate.getTime()) / (1000 * 60)) : 30;
      
      // Validate the appointment time
      const validation = await validateAppointmentTime(startDate, durationMinutes > 0 ? durationMinutes : 30);
      
      if (!validation.isValid) {
        setValidationError(validation.error || 'Invalid appointment time');
      } else {
        setValidationError(null);
      }
      
      // Get clinic hours info for this date
      const hoursInfo = await getClinicHoursForDate(startDate);
      if (hoursInfo) {
        if (!hoursInfo.isOpen) {
          setClinicHoursInfo(hoursInfo.holidayName 
            ? `Clinic closed: ${hoursInfo.holidayName}` 
            : 'Clinic is closed on this day');
        } else {
          let info = `Hours: ${hoursInfo.openTime} - ${hoursInfo.closeTime}`;
          if (hoursInfo.breakStart && hoursInfo.breakEnd) {
            info += ` (Break: ${hoursInfo.breakStart} - ${hoursInfo.breakEnd})`;
          }
          if (hoursInfo.holidayName) {
            info += ` - ${hoursInfo.holidayName} (Modified hours)`;
          }
          setClinicHoursInfo(info);
        }
      }
    } catch (error) {
      console.error('Validation error:', error);
    } finally {
      setIsValidating(false);
    }
  };

  // Effect to validate when form times change and auto-set end time
  useEffect(() => {
    if (formData.start_time) {
      const startDate = new Date(formData.start_time);
      
      // Auto-set end time to 30 minutes after start time if end time is not set or needs adjustment
      if (!formData.end_time) {
        const endDate = new Date(startDate.getTime() + 30 * 60000); // Add 30 minutes
        
        // Format to datetime-local format (YYYY-MM-DDTHH:MM)
        const year = endDate.getFullYear();
        const month = String(endDate.getMonth() + 1).padStart(2, '0');
        const day = String(endDate.getDate()).padStart(2, '0');
        const hours = String(endDate.getHours()).padStart(2, '0');
        const minutes = String(endDate.getMinutes()).padStart(2, '0');
        const endTimeString = `${year}-${month}-${day}T${hours}:${minutes}`;
        
        setFormData(prev => ({ ...prev, end_time: endTimeString }));
      } else {
        // If end time is already set, check if it's before start time or more than 3 hours after
        const endDate = new Date(formData.end_time);
        const maxEndDate = new Date(startDate.getTime() + 180 * 60000); // 3 hours max
        
        if (endDate <= startDate) {
          // End time is before or equal to start time, auto-adjust
          const newEndDate = new Date(startDate.getTime() + 30 * 60000);
          const year = newEndDate.getFullYear();
          const month = String(newEndDate.getMonth() + 1).padStart(2, '0');
          const day = String(newEndDate.getDate()).padStart(2, '0');
          const hours = String(newEndDate.getHours()).padStart(2, '0');
          const minutes = String(newEndDate.getMinutes()).padStart(2, '0');
          const endTimeString = `${year}-${month}-${day}T${hours}:${minutes}`;
          setFormData(prev => ({ ...prev, end_time: endTimeString }));
        } else if (endDate > maxEndDate) {
          // End time is more than 3 hours after start, cap it
          const year = maxEndDate.getFullYear();
          const month = String(maxEndDate.getMonth() + 1).padStart(2, '0');
          const day = String(maxEndDate.getDate()).padStart(2, '0');
          const hours = String(maxEndDate.getHours()).padStart(2, '0');
          const minutes = String(maxEndDate.getMinutes()).padStart(2, '0');
          const endTimeString = `${year}-${month}-${day}T${hours}:${minutes}`;
          setFormData(prev => ({ ...prev, end_time: endTimeString }));
        }
      }
      
      // Validate after adjusting times
      validateAndUpdateTime(formData.start_time, formData.end_time);
    }
  }, [formData.start_time]);

  const handleCreateAppointment = async () => {
    if (!formData.patient_id || !formData.start_time || !formData.end_time || !formData.reason) {
      toast.error('❌ Missing Fields: Please fill in all required fields (Patient, Start Time, End Time, and Reason)');
      return;
    }

    // Validate dates
    const startDate = new Date(formData.start_time);
    const endDate = new Date(formData.end_time);
    const now = new Date();

    if (startDate < now) {
      toast.error('❌ Invalid Time: Start time cannot be in the past. Please select a future date and time.');
      return;
    }

    if (endDate <= startDate) {
      toast.error('❌ Invalid Time: End time must be after start time. Please adjust your selection.');
      return;
    }

    // Validate maximum appointment duration (3 hours = 180 minutes)
    const durationMinutes = Math.round((endDate.getTime() - startDate.getTime()) / (1000 * 60));
    if (durationMinutes > 180) {
      const hours = Math.floor(durationMinutes / 60);
      const mins = durationMinutes % 60;
      toast.error(`❌ Duration Too Long: Selected duration is ${hours}h ${mins}m. Maximum allowed is 3 hours.`);
      return;
    }

    // Validate against clinic hours and holidays
    const validation = await validateAppointmentTime(startDate, durationMinutes);
    
    if (!validation.isValid) {
      toast.error(`⚠️ ${validation.error || 'Invalid appointment time'}`);
      return;
    }

    try {
      // datetime-local inputs give us a local time string
      // We need to convert to UTC for storage
      const startISO = localDateTimeToUTC(formData.start_time);
      const endISO = localDateTimeToUTC(formData.end_time);
      
      const createData: AppointmentCreate = {
        patient_id: formData.patient_id,
        start_time: startISO,
        end_time: endISO,
        reason: formData.reason,
      };

      await appointmentApi.create(createData);
      toast.success('✅ Appointment created successfully');
      setIsCreateDialogOpen(false);
      resetForm();
      loadData();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to create appointment');
    }
  };

  const handleUpdateAppointment = async () => {
    if (!selectedAppointment || !formData.start_time || !formData.end_time || !formData.reason) {
      toast.error('❌ Missing Fields: Please fill in all required fields (Start Time, End Time, and Reason)');
      return;
    }

    // Validate dates
    const startDate = new Date(formData.start_time);
    const endDate = new Date(formData.end_time);

    if (endDate <= startDate) {
      toast.error('❌ Invalid Time: End time must be after start time. Please adjust your selection.');
      return;
    }

    // Validate maximum appointment duration (3 hours = 180 minutes)
    const durationMinutes = Math.round((endDate.getTime() - startDate.getTime()) / (1000 * 60));
    if (durationMinutes > 180) {
      const hours = Math.floor(durationMinutes / 60);
      const mins = durationMinutes % 60;
      toast.error(`❌ Duration Too Long: Selected duration is ${hours}h ${mins}m. Maximum allowed is 3 hours.`);
      return;
    }

    // Validate against clinic hours and holidays
    const validation = await validateAppointmentTime(startDate, durationMinutes);
    
    if (!validation.isValid) {
      toast.error(`⚠️ ${validation.error || 'Invalid appointment time'}`);
      return;
    }

    try {
      // datetime-local inputs give us a local time string
      // We need to convert to UTC for storage
      const startISO = localDateTimeToUTC(formData.start_time);
      const endISO = localDateTimeToUTC(formData.end_time);
      
      const updateData: AppointmentUpdate = {
        start_time: startISO,
        end_time: endISO,
        reason: formData.reason,
      };

      await appointmentApi.update(selectedAppointment.id, updateData);
      toast.success('✅ Appointment updated successfully');
      setIsEditDialogOpen(false);
      resetForm();
      loadData();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to update appointment');
    }
  };

  const handleCancelAppointment = async () => {
    if (!selectedAppointment) return;

    try {
      await appointmentApi.cancel(selectedAppointment.id, cancellationReason || 'Cancelled by admin');
      toast.success('Appointment cancelled successfully');
      setIsCancelDialogOpen(false);
      setSelectedAppointment(null);
      setCancellationReason('');
      loadData();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to cancel appointment');
    }
  };

  const handleCompleteAppointment = async (appointment: Appointment) => {
    try {
      await appointmentApi.update(appointment.id, {
        status: 'COMPLETED',
        start_time: appointment.start_time,
        end_time: appointment.end_time,
        reason: appointment.reason,
      });
      toast.success('Appointment marked as completed');
      loadData();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to update appointment');
    }
  };

  const canCompleteAppointment = (appointment: Appointment): boolean => {
    // Check if appointment end time has passed
    const endTime = parseUTCDate(appointment.end_time);
    const now = new Date();
    return now >= endTime;
  };

  const openEditDialog = (appointment: Appointment) => {
    setSelectedAppointment(appointment);
    // Convert UTC datetime from backend to local datetime-local format
    const startLocal = utcToLocalDateTime(appointment.start_time);
    const endLocal = utcToLocalDateTime(appointment.end_time);
    
    setFormData({
      patient_id: appointment.patient_id,
      start_time: startLocal,
      end_time: endLocal,
      reason: appointment.reason,
    });
    setIsEditDialogOpen(true);
  };

  const openCancelDialog = (appointment: Appointment) => {
    setSelectedAppointment(appointment);
    setIsCancelDialogOpen(true);
  };

  const getPatientName = (patientId: number) => {
    const patient = patients.find((p) => p.id === patientId);
    return patient?.name || 'Unknown Patient';
  };

  const formatDateTime = (dateString: string) => {
    // Use utility function to properly handle UTC timestamps from backend
    return formatBackendDate(dateString);
  };

  const getStatusBadge = (status: string) => {
    const statusConfig = {
      CONFIRMED: { variant: 'default' as const, label: 'Confirmed' },
      CANCELLED: { variant: 'destructive' as const, label: 'Cancelled' },
      COMPLETED: { variant: 'secondary' as const, label: 'Completed' },
      PENDING: { variant: 'outline' as const, label: 'Pending' },
    };

    const config = statusConfig[status as keyof typeof statusConfig] || statusConfig.PENDING;
    return <Badge variant={config.variant}>{config.label}</Badge>;
  };

  const filteredAppointments = appointments.filter((apt) => {
    // Filter by status
    if (filterStatus !== 'all' && apt.status !== filterStatus) {
      return false;
    }
    
    // Filter by selected date from calendar
    if (selectedDate) {
      try {
        // Parse appointment time as wall clock time
        const aptDate = parseUTCDate(apt.start_time);
        
        // selectedDate is already in YYYY-MM-DD format (local)
        // Compare using local date components to avoid timezone issues
        const aptYear = aptDate.getFullYear();
        const aptMonth = String(aptDate.getMonth() + 1).padStart(2, '0');
        const aptDay = String(aptDate.getDate()).padStart(2, '0');
        const aptDateStr = `${aptYear}-${aptMonth}-${aptDay}`;
        
        const matches = aptDateStr === selectedDate;
        
        if (!matches) {
          return false;
        }
      } catch (error) {
        console.error('Error parsing date:', error);
        return false;
      }
    }
    
    // Filter by search query
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      const patientName = getPatientName(apt.patient_id).toLowerCase();
      const reason = apt.reason.toLowerCase();
      const status = apt.status.toLowerCase();
      
      return (
        patientName.includes(query) ||
        reason.includes(query) ||
        status.includes(query)
      );
    }
    
    return true;
  });

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold gradient-text">Appointments</h1>
            <p className="text-muted-foreground mt-1">
              Manage patient appointments and schedules
            </p>
          </div>
          <Button
            onClick={() => {
              resetForm();
              setIsCreateDialogOpen(true);
            }}
            className="gradient"
          >
            <Plus className="w-4 h-4 mr-2" />
            New Appointment
          </Button>
        </div>

        <Card className="glass-card">
          <CardHeader>
            <div className="flex items-center justify-between mb-4">
              <CardTitle className="flex items-center gap-2">
                <CalendarIcon className="w-5 h-5" />
                All Appointments
                {selectedDate && (
                  <span className="text-sm font-normal text-muted-foreground">
                    - {format(new Date(selectedDate), 'MMM dd, yyyy')}
                  </span>
                )}
              </CardTitle>
              <div className="flex items-center gap-3">
                {selectedDate && (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => {
                      setSelectedDate(null);
                      setSearchParams({});
                    }}
                  >
                    Clear Date Filter
                  </Button>
                )}
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                  <Input
                    placeholder="Search by patient, reason, or status..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-10 w-[300px]"
                  />
                </div>
                <Select value={filterStatus} onValueChange={setFilterStatus}>
                  <SelectTrigger className="w-[180px]">
                    <SelectValue placeholder="Filter by status" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Status</SelectItem>
                    <SelectItem value="CONFIRMED">Confirmed</SelectItem>
                    <SelectItem value="PENDING">Pending</SelectItem>
                    <SelectItem value="COMPLETED">Completed</SelectItem>
                    <SelectItem value="CANCELLED">Cancelled</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="text-center py-8 text-muted-foreground">
                Loading appointments...
              </div>
            ) : filteredAppointments.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                No appointments found
              </div>
            ) : (
              <div className="rounded-md border">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Patient</TableHead>
                      <TableHead>Start Time</TableHead>
                      <TableHead>End Time</TableHead>
                      <TableHead>Reason</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead className="text-right">Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {filteredAppointments.map((appointment) => (
                      <TableRow key={appointment.id}>
                        <TableCell className="font-medium">
                          <div className="flex items-center gap-2">
                            <User className="w-4 h-4 text-muted-foreground" />
                            {getPatientName(appointment.patient_id)}
                          </div>
                        </TableCell>
                        <TableCell>
                          <div className="flex items-center gap-2 text-sm">
                            <Clock className="w-3 h-3 text-muted-foreground" />
                            {formatDateTime(appointment.start_time)}
                          </div>
                        </TableCell>
                        <TableCell>
                          <div className="text-sm">
                            {formatDateTime(appointment.end_time)}
                          </div>
                        </TableCell>
                        <TableCell className="max-w-xs truncate">
                          {appointment.reason}
                        </TableCell>
                        <TableCell>{getStatusBadge(appointment.status)}</TableCell>
                        <TableCell className="text-right">
                          <div className="flex justify-end gap-2">
                            {appointment.status === 'CONFIRMED' && (
                              <>
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  onClick={() => openEditDialog(appointment)}
                                >
                                  Edit
                                </Button>
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  onClick={() => handleCompleteAppointment(appointment)}
                                  disabled={!canCompleteAppointment(appointment)}
                                  title={!canCompleteAppointment(appointment) ? 'Appointment not yet completed' : 'Mark as completed'}
                                >
                                  Complete
                                </Button>
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  onClick={() => openCancelDialog(appointment)}
                                  className="text-red-500"
                                >
                                  <X className="w-4 h-4" />
                                </Button>
                              </>
                            )}
                            {appointment.status !== 'CONFIRMED' && (
                              <span className="text-xs text-muted-foreground px-3">
                                {appointment.cancellation_reason || 'No actions available'}
                              </span>
                            )}
                          </div>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Create Appointment Dialog */}
      <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
        <DialogContent className="sm:max-w-[500px]">
          <DialogHeader>
            <DialogTitle>Create New Appointment</DialogTitle>
            <DialogDescription>
              Schedule a new appointment for a patient.
            </DialogDescription>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            <div className="grid gap-2">
              <Label htmlFor="patient">Patient</Label>
              <Select
                value={formData.patient_id?.toString()}
                onValueChange={(value) => setFormData({ ...formData, patient_id: parseInt(value) })}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select a patient" />
                </SelectTrigger>
                <SelectContent>
                  {patients.map((patient) => (
                    <SelectItem key={patient.id} value={patient.id.toString()}>
                      {patient.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="grid gap-2">
              <Label htmlFor="start_time">Start Time</Label>
              <Input
                id="start_time"
                type="datetime-local"
                value={formData.start_time}
                min={format(new Date(), "yyyy-MM-dd'T'HH:mm")}
                onChange={(e) => setFormData({ ...formData, start_time: e.target.value })}
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="end_time">End Time (Max 3 hours from start)</Label>
              <Input
                id="end_time"
                type="datetime-local"
                value={formData.end_time}
                min={formData.start_time || format(new Date(), "yyyy-MM-dd'T'HH:mm")}
                max={formData.start_time ? (() => {
                  const maxEnd = new Date(new Date(formData.start_time).getTime() + 180 * 60000);
                  return format(maxEnd, "yyyy-MM-dd'T'HH:mm");
                })() : undefined}
                onChange={(e) => setFormData({ ...formData, end_time: e.target.value })}
              />
            </div>
            
            {/* Clinic Hours Info */}
            {clinicHoursInfo && (
              <Alert className="border-blue-200 bg-blue-50 dark:border-blue-800 dark:bg-blue-950">
                <Info className="h-4 w-4 text-blue-600" />
                <AlertDescription className="text-blue-700 dark:text-blue-300">
                  {clinicHoursInfo}
                </AlertDescription>
              </Alert>
            )}
            
            {/* Validation Error */}
            {validationError && (
              <Alert variant="destructive">
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>
                  {validationError}
                </AlertDescription>
              </Alert>
            )}
            
            <div className="grid gap-2">
              <Label htmlFor="reason">Reason for Visit</Label>
              <Textarea
                id="reason"
                value={formData.reason}
                onChange={(e) => setFormData({ ...formData, reason: e.target.value })}
                placeholder="Enter reason for appointment..."
                rows={3}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsCreateDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleCreateAppointment} disabled={!!validationError || isValidating}>
              {isValidating ? 'Validating...' : 'Create Appointment'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Edit Appointment Dialog */}
      <Dialog open={isEditDialogOpen} onOpenChange={setIsEditDialogOpen}>
        <DialogContent className="sm:max-w-[500px]">
          <DialogHeader>
            <DialogTitle>Edit Appointment</DialogTitle>
            <DialogDescription>
              Update appointment details.
            </DialogDescription>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            <div className="grid gap-2">
              <Label htmlFor="edit-patient">Patient</Label>
              <Select
                value={formData.patient_id?.toString()}
                onValueChange={(value) => setFormData({ ...formData, patient_id: parseInt(value) })}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select a patient" />
                </SelectTrigger>
                <SelectContent>
                  {patients.map((patient) => (
                    <SelectItem key={patient.id} value={patient.id.toString()}>
                      {patient.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="grid gap-2">
              <Label htmlFor="edit-start_time">Start Time</Label>
              <Input
                id="edit-start_time"
                type="datetime-local"
                value={formData.start_time}
                onChange={(e) => setFormData({ ...formData, start_time: e.target.value })}
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="edit-end_time">End Time (Max 3 hours from start)</Label>
              <Input
                id="edit-end_time"
                type="datetime-local"
                value={formData.end_time}
                min={formData.start_time}
                max={formData.start_time ? (() => {
                  const maxEnd = new Date(new Date(formData.start_time).getTime() + 180 * 60000);
                  return format(maxEnd, "yyyy-MM-dd'T'HH:mm");
                })() : undefined}
                onChange={(e) => setFormData({ ...formData, end_time: e.target.value })}
              />
            </div>
            
            {/* Clinic Hours Info */}
            {clinicHoursInfo && (
              <Alert className="border-blue-200 bg-blue-50 dark:border-blue-800 dark:bg-blue-950">
                <Info className="h-4 w-4 text-blue-600" />
                <AlertDescription className="text-blue-700 dark:text-blue-300">
                  {clinicHoursInfo}
                </AlertDescription>
              </Alert>
            )}
            
            {/* Validation Error */}
            {validationError && (
              <Alert variant="destructive">
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>
                  {validationError}
                </AlertDescription>
              </Alert>
            )}
            
            <div className="grid gap-2">
              <Label htmlFor="edit-reason">Reason for Visit</Label>
              <Textarea
                id="edit-reason"
                value={formData.reason}
                onChange={(e) => setFormData({ ...formData, reason: e.target.value })}
                placeholder="Enter reason for appointment..."
                rows={3}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsEditDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleUpdateAppointment} disabled={!!validationError || isValidating}>
              {isValidating ? 'Validating...' : 'Save Changes'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Cancel Appointment Dialog */}
      <AlertDialog open={isCancelDialogOpen} onOpenChange={setIsCancelDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Cancel Appointment</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to cancel this appointment? This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <div className="grid gap-2 py-4">
            <Label htmlFor="cancellation_reason">Cancellation Reason (Optional)</Label>
            <Textarea
              id="cancellation_reason"
              value={formData.cancellation_reason || ''}
              onChange={(e) => setFormData({ ...formData, cancellation_reason: e.target.value })}
              placeholder="Enter reason for cancellation..."
              rows={3}
            />
          </div>
          <AlertDialogFooter>
            <AlertDialogCancel>Keep Appointment</AlertDialogCancel>
            <AlertDialogAction onClick={handleCancelAppointment} className="bg-red-500 hover:bg-red-600">
              Cancel Appointment
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </DashboardLayout>
  );
};

export default Appointments;
