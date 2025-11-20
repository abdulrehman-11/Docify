import { useState, useEffect } from 'react';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle } from '@/components/ui/alert-dialog';
import { Briefcase, Plus, Edit, Trash2, Clock } from 'lucide-react';
import { Service } from '@/lib/mockData';
import { getServices, saveService, deleteService } from '@/lib/storage';
import { toast } from 'sonner';

const Services = () => {
  const [services, setServices] = useState<Service[]>([]);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [selectedService, setSelectedService] = useState<Service | null>(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [serviceToDelete, setServiceToDelete] = useState<string | null>(null);
  const [formData, setFormData] = useState<Partial<Service>>({});

  useEffect(() => {
    loadServices();
  }, []);

  const loadServices = () => {
    setServices(getServices());
  };

  const handleAddService = () => {
    setSelectedService(null);
    setFormData({ name: '', duration: 30, description: '' });
    setDialogOpen(true);
  };

  const handleEditService = (service: Service) => {
    setSelectedService(service);
    setFormData(service);
    setDialogOpen(true);
  };

  const handleDeleteService = (id: string) => {
    setServiceToDelete(id);
    setDeleteDialogOpen(true);
  };

  const confirmDelete = () => {
    if (serviceToDelete) {
      deleteService(serviceToDelete);
      loadServices();
      toast.success('Service deleted successfully');
    }
    setDeleteDialogOpen(false);
    setServiceToDelete(null);
  };

  const handleSave = () => {
    if (!formData.name || !formData.duration) {
      toast.error('Please fill in all required fields');
      return;
    }

    const serviceData: Service = {
      id: selectedService?.id || Date.now().toString(),
      name: formData.name!,
      duration: formData.duration!,
      description: formData.description || '',
    };

    saveService(serviceData);
    loadServices();
    toast.success(selectedService ? 'Service updated successfully' : 'Service added successfully');
    setDialogOpen(false);
  };

  return (
    <DashboardLayout>
      <div className="space-y-6 animate-fade-in">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Services</h1>
            <p className="text-muted-foreground mt-2">Manage clinic services and their durations</p>
          </div>
          <Button onClick={handleAddService} className="bg-primary hover-lift">
            <Plus className="w-4 h-4 mr-2" />
            Add Service
          </Button>
        </div>

        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {services.map((service) => (
            <Card key={service.id} className="glass-card hover-lift">
              <CardContent className="p-6">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <h3 className="font-bold text-lg mb-1">{service.name}</h3>
                    <div className="flex items-center gap-2 text-sm text-muted-foreground">
                      <Clock className="w-4 h-4" />
                      <span>{service.duration} minutes</span>
                    </div>
                  </div>
                  <div className="p-2 rounded-xl bg-primary/10">
                    <Briefcase className="w-5 h-5 text-primary" />
                  </div>
                </div>

                {service.description && (
                  <p className="text-sm text-muted-foreground mb-4 line-clamp-2">
                    {service.description}
                  </p>
                )}

                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    className="flex-1 hover-lift"
                    onClick={() => handleEditService(service)}
                  >
                    <Edit className="w-3 h-3 mr-1" />
                    Edit
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    className="hover-lift text-red-600 hover:bg-red-50"
                    onClick={() => handleDeleteService(service.id)}
                  >
                    <Trash2 className="w-3 h-3 mr-1" />
                    Delete
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}

          {services.length === 0 && (
            <Card className="glass-card col-span-full">
              <CardContent className="text-center py-12">
                <Briefcase className="w-12 h-12 text-muted-foreground mx-auto mb-3 opacity-50" />
                <p className="text-muted-foreground mb-4">No services added yet</p>
                <Button onClick={handleAddService} variant="outline" className="hover-lift">
                  <Plus className="w-4 h-4 mr-2" />
                  Add Your First Service
                </Button>
              </CardContent>
            </Card>
          )}
        </div>

        {/* Add/Edit Dialog */}
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogContent className="glass-card sm:max-w-[500px]">
            <DialogHeader>
              <DialogTitle>
                {selectedService ? 'Edit Service' : 'Add New Service'}
              </DialogTitle>
            </DialogHeader>

            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="name">Service Name *</Label>
                <Input
                  id="name"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  placeholder="General Consultation"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="duration">Duration (minutes) *</Label>
                <Input
                  id="duration"
                  type="number"
                  value={formData.duration}
                  onChange={(e) => setFormData({ ...formData, duration: parseInt(e.target.value) || 0 })}
                  placeholder="30"
                  min="1"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="description">Description</Label>
                <Textarea
                  id="description"
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  placeholder="Brief description of the service..."
                  rows={3}
                />
              </div>
            </div>

            <DialogFooter>
              <Button variant="outline" onClick={() => setDialogOpen(false)}>
                Cancel
              </Button>
              <Button onClick={handleSave} className="bg-primary">
                {selectedService ? 'Update' : 'Add'} Service
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>

        {/* Delete Confirmation Dialog */}
        <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
          <AlertDialogContent className="glass-card">
            <AlertDialogHeader>
              <AlertDialogTitle>Delete Service?</AlertDialogTitle>
              <AlertDialogDescription>
                This will permanently delete this service. This action cannot be undone.
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

export default Services;

