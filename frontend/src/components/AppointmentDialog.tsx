import { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Appointment, Service } from '@/lib/mockData';
import { getServices } from '@/lib/storage';
import { format } from 'date-fns';
import { toast } from 'sonner';

interface AppointmentDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  appointment?: Appointment;
  doctorId: string;
  doctorName: string;
  selectedDate: Date;
  onSave: (appointment: Appointment) => void;
}

export const AppointmentDialog = ({
  open,
  onOpenChange,
  appointment,
  doctorId,
  doctorName,
  selectedDate,
  onSave,
}: AppointmentDialogProps) => {
  const [services, setServices] = useState<Service[]>([]);
  const [formData, setFormData] = useState<Partial<Appointment>>({
    patientName: '',
    patientEmail: '',
    patientPhone: '',
    service: '',
    date: format(selectedDate, 'yyyy-MM-dd'),
    time: '',
    notes: '',
  });

  useEffect(() => {
    setServices(getServices());
  }, []);

  useEffect(() => {
    if (appointment) {
      setFormData(appointment);
    } else {
      setFormData({
        patientName: '',
        patientEmail: '',
        patientPhone: '',
        service: '',
        date: format(selectedDate, 'yyyy-MM-dd'),
        time: '',
        notes: '',
      });
    }
  }, [appointment, selectedDate]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.patientName || !formData.patientEmail || !formData.patientPhone || !formData.service || !formData.time) {
      toast.error('Please fill in all required fields');
      return;
    }

    const user = JSON.parse(sessionStorage.getItem('user') || '{}');
    
    const newAppointment: Appointment = {
      id: appointment?.id || Date.now().toString(),
      doctorId,
      patientName: formData.patientName!,
      patientEmail: formData.patientEmail!,
      patientPhone: formData.patientPhone!,
      service: formData.service!,
      date: formData.date!,
      time: formData.time!,
      status: appointment?.status || 'scheduled',
      notes: formData.notes,
      createdBy: user.email || 'unknown',
      createdAt: appointment?.createdAt || new Date().toISOString(),
    };

    onSave(newAppointment);
    toast.success(appointment ? 'Appointment updated successfully' : 'Appointment created successfully');
    onOpenChange(false);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[500px] glass-card">
        <DialogHeader>
          <DialogTitle>
            {appointment ? 'Edit Appointment' : 'New Appointment'}
          </DialogTitle>
          <p className="text-sm text-muted-foreground">
            Doctor: {doctorName}
          </p>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="patientName">Patient Name *</Label>
            <Input
              id="patientName"
              value={formData.patientName}
              onChange={(e) => setFormData({ ...formData, patientName: e.target.value })}
              placeholder="Enter patient name"
              required
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="patientEmail">Email *</Label>
              <Input
                id="patientEmail"
                type="email"
                value={formData.patientEmail}
                onChange={(e) => setFormData({ ...formData, patientEmail: e.target.value })}
                placeholder="patient@email.com"
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="patientPhone">Phone *</Label>
              <Input
                id="patientPhone"
                type="tel"
                value={formData.patientPhone}
                onChange={(e) => setFormData({ ...formData, patientPhone: e.target.value })}
                placeholder="+92-300-0000000"
                required
              />
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="service">Service *</Label>
            <Select
              value={formData.service}
              onValueChange={(value) => setFormData({ ...formData, service: value })}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select a service" />
              </SelectTrigger>
              <SelectContent>
                {services.map((service) => (
                  <SelectItem key={service.id} value={service.name}>
                    {service.name} ({service.duration} min)
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="date">Date *</Label>
              <Input
                id="date"
                type="date"
                value={formData.date}
                onChange={(e) => setFormData({ ...formData, date: e.target.value })}
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="time">Time *</Label>
              <Input
                id="time"
                type="time"
                value={formData.time}
                onChange={(e) => setFormData({ ...formData, time: e.target.value })}
                required
              />
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="notes">Notes</Label>
            <Textarea
              id="notes"
              value={formData.notes}
              onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
              placeholder="Any special notes or requirements"
              rows={3}
            />
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            <Button type="submit" className="bg-primary">
              {appointment ? 'Update' : 'Create'} Appointment
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
};
