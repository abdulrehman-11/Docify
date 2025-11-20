import { useState, useEffect } from 'react';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle } from '@/components/ui/alert-dialog';
import { Users, Plus, Edit, Trash2, Star, Mail, Phone, Clock, Calendar } from 'lucide-react';
import { Doctor } from '@/lib/mockData';
import { getDoctors, saveDoctor, deleteDoctor } from '@/lib/storage';
import { toast } from 'sonner';

const Providers = () => {
  const [doctors, setDoctors] = useState<Doctor[]>([]);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [selectedDoctor, setSelectedDoctor] = useState<Doctor | null>(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [doctorToDelete, setDoctorToDelete] = useState<string | null>(null);
  const [formData, setFormData] = useState<Partial<Doctor>>({});

  const daysOfWeek = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];

  useEffect(() => {
    loadDoctors();
  }, []);

  const loadDoctors = () => {
    setDoctors(getDoctors());
  };

  const handleAddDoctor = () => {
    setSelectedDoctor(null);
    setFormData({
      name: '',
      specialty: '',
      email: '',
      phone: '',
      bio: '',
      image: 'https://images.unsplash.com/photo-1612349317150-e413f6a5b16d?w=400&h=400&fit=crop',
      rating: 5.0,
      reviews: 0,
      schedule: daysOfWeek.map(day => ({
        day,
        startTime: '',
        endTime: '',
      })),
    });
    setDialogOpen(true);
  };

  const handleEditDoctor = (doctor: Doctor) => {
    setSelectedDoctor(doctor);
    setFormData(doctor);
    setDialogOpen(true);
  };

  const handleDeleteDoctor = (id: string) => {
    setDoctorToDelete(id);
    setDeleteDialogOpen(true);
  };

  const confirmDelete = () => {
    if (doctorToDelete) {
      deleteDoctor(doctorToDelete);
      loadDoctors();
      toast.success('Provider deleted successfully');
    }
    setDeleteDialogOpen(false);
    setDoctorToDelete(null);
  };

  const handleSave = () => {
    if (!formData.name || !formData.specialty || !formData.email || !formData.phone) {
      toast.error('Please fill in all required fields');
      return;
    }

    const doctorData: Doctor = {
      id: selectedDoctor?.id || Date.now().toString(),
      name: formData.name!,
      specialty: formData.specialty!,
      email: formData.email!,
      phone: formData.phone!,
      bio: formData.bio || '',
      image: formData.image || 'https://images.unsplash.com/photo-1612349317150-e413f6a5b16d?w=400&h=400&fit=crop',
      rating: formData.rating || 5.0,
      reviews: formData.reviews || 0,
      schedule: formData.schedule?.filter(s => s.startTime && s.endTime) || [],
    };

    saveDoctor(doctorData);
    loadDoctors();
    toast.success(selectedDoctor ? 'Provider updated successfully' : 'Provider added successfully');
    setDialogOpen(false);
  };

  const updateSchedule = (day: string, field: 'startTime' | 'endTime', value: string) => {
    const schedule = formData.schedule || [];
    const updatedSchedule = schedule.map(s =>
      s.day === day ? { ...s, [field]: value } : s
    );
    setFormData({ ...formData, schedule: updatedSchedule });
  };

  return (
    <DashboardLayout>
      <div className="space-y-6 animate-fade-in">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Providers</h1>
            <p className="text-muted-foreground mt-2">Manage healthcare providers and their schedules</p>
          </div>
          <Button onClick={handleAddDoctor} className="bg-primary hover-lift">
            <Plus className="w-4 h-4 mr-2" />
            Add Provider
          </Button>
        </div>

        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {doctors.map((doctor) => (
            <Card key={doctor.id} className="glass-card hover-lift overflow-hidden">
              <CardContent className="p-6">
                <div className="flex flex-col items-center text-center mb-4">
                  <Avatar className="w-24 h-24 mb-3 ring-4 ring-primary/20">
                    <AvatarImage src={doctor.image} alt={doctor.name} />
                    <AvatarFallback>{doctor.name.charAt(0)}</AvatarFallback>
                  </Avatar>
                  <h3 className="font-bold text-lg">{doctor.name}</h3>
                  <p className="text-sm text-muted-foreground">{doctor.specialty}</p>
                  <div className="flex items-center gap-1 mt-2">
                    <Star className="w-4 h-4 fill-yellow-400 text-yellow-400" />
                    <span className="font-medium">{doctor.rating}</span>
                    <span className="text-xs text-muted-foreground">({doctor.reviews})</span>
                  </div>
                </div>

                <div className="space-y-2 mb-4">
                  <div className="flex items-center gap-2 text-sm">
                    <Mail className="w-4 h-4 text-primary" />
                    <span className="text-xs truncate">{doctor.email}</span>
                  </div>
                  <div className="flex items-center gap-2 text-sm">
                    <Phone className="w-4 h-4 text-primary" />
                    <span className="text-xs">{doctor.phone}</span>
                  </div>
                  <div className="flex items-start gap-2 text-sm">
                    <Calendar className="w-4 h-4 text-primary mt-0.5" />
                    <span className="text-xs text-muted-foreground">
                      {doctor.schedule.length} days scheduled
                    </span>
                  </div>
                </div>

                {doctor.bio && (
                  <p className="text-xs text-muted-foreground mb-4 line-clamp-2">
                    {doctor.bio}
                  </p>
                )}

                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    className="flex-1 hover-lift"
                    onClick={() => handleEditDoctor(doctor)}
                  >
                    <Edit className="w-3 h-3 mr-1" />
                    Edit
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    className="hover-lift text-red-600 hover:bg-red-50"
                    onClick={() => handleDeleteDoctor(doctor.id)}
                  >
                    <Trash2 className="w-3 h-3 mr-1" />
                    Delete
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}

          {doctors.length === 0 && (
            <Card className="glass-card col-span-full">
              <CardContent className="text-center py-12">
                <Users className="w-12 h-12 text-muted-foreground mx-auto mb-3 opacity-50" />
                <p className="text-muted-foreground mb-4">No providers added yet</p>
                <Button onClick={handleAddDoctor} variant="outline" className="hover-lift">
                  <Plus className="w-4 h-4 mr-2" />
                  Add Your First Provider
                </Button>
              </CardContent>
            </Card>
          )}
        </div>

        {/* Add/Edit Dialog */}
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogContent className="glass-card max-w-2xl max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>
                {selectedDoctor ? 'Edit Provider' : 'Add New Provider'}
              </DialogTitle>
            </DialogHeader>

            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="name">Name *</Label>
                  <Input
                    id="name"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    placeholder="Dr. John Doe"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="specialty">Specialty *</Label>
                  <Input
                    id="specialty"
                    value={formData.specialty}
                    onChange={(e) => setFormData({ ...formData, specialty: e.target.value })}
                    placeholder="General Physician"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="email">Email *</Label>
                  <Input
                    id="email"
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    placeholder="doctor@clinic.com"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="phone">Phone *</Label>
                  <Input
                    id="phone"
                    type="tel"
                    value={formData.phone}
                    onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                    placeholder="+92-300-0000000"
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="image">Profile Image URL</Label>
                <Input
                  id="image"
                  value={formData.image}
                  onChange={(e) => setFormData({ ...formData, image: e.target.value })}
                  placeholder="https://example.com/image.jpg"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="bio">Bio</Label>
                <Textarea
                  id="bio"
                  value={formData.bio}
                  onChange={(e) => setFormData({ ...formData, bio: e.target.value })}
                  placeholder="Brief professional bio..."
                  rows={3}
                />
              </div>

              <div>
                <Label className="mb-3 block">Schedule</Label>
                <div className="space-y-2 max-h-60 overflow-y-auto">
                  {daysOfWeek.map((day) => {
                    const daySchedule = formData.schedule?.find(s => s.day === day);
                    return (
                      <div key={day} className="grid grid-cols-7 gap-2 items-center glass p-2 rounded-lg">
                        <span className="col-span-3 text-sm font-medium">{day}</span>
                        <Input
                          type="time"
                          value={daySchedule?.startTime || ''}
                          onChange={(e) => updateSchedule(day, 'startTime', e.target.value)}
                          className="col-span-2 h-8 text-xs"
                        />
                        <Input
                          type="time"
                          value={daySchedule?.endTime || ''}
                          onChange={(e) => updateSchedule(day, 'endTime', e.target.value)}
                          className="col-span-2 h-8 text-xs"
                        />
                      </div>
                    );
                  })}
                </div>
                <p className="text-xs text-muted-foreground mt-2">
                  Leave empty for days the provider is not available
                </p>
              </div>
            </div>

            <DialogFooter>
              <Button variant="outline" onClick={() => setDialogOpen(false)}>
                Cancel
              </Button>
              <Button onClick={handleSave} className="bg-primary">
                {selectedDoctor ? 'Update' : 'Add'} Provider
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>

        {/* Delete Confirmation Dialog */}
        <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
          <AlertDialogContent className="glass-card">
            <AlertDialogHeader>
              <AlertDialogTitle>Delete Provider?</AlertDialogTitle>
              <AlertDialogDescription>
                This will permanently delete this provider. This action cannot be undone.
              </AlertDialogDescription>
            </AlertDialogHeader>
            <AlertDialogFooter>
              <AlertDialogCancel>Cancel</AlertDialogCancel>
              <AlertDialogAction onClick={confirmDelete} className="bg-destructive">
                Delete
              </AlertDialogAction>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialog>
      </div>
    </DashboardLayout>
  );
};

export default Providers;

