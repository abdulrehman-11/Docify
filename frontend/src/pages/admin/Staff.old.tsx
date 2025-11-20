import { useState, useEffect } from 'react';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Checkbox } from '@/components/ui/checkbox';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle } from '@/components/ui/alert-dialog';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { UserPlus, Edit, Trash2, Mail, Key, Users as UsersIcon, CheckCircle2 } from 'lucide-react';
import { User } from '@/lib/auth';
import { getAllStaffAccounts, createStaffAccount, updateStaffAccount, deleteStaffAccount } from '@/lib/auth';
import { getDoctors } from '@/lib/storage';
import { Doctor } from '@/lib/mockData';
import { toast } from 'sonner';
import { cn } from '@/lib/utils';

const AVAILABLE_PERMISSIONS = [
  { id: 'view_appointments', label: 'View Appointments', description: 'Can view appointment schedules' },
  { id: 'add_appointments', label: 'Add Appointments', description: 'Can create new appointments' },
  { id: 'edit_appointments', label: 'Edit Appointments', description: 'Can modify existing appointments' },
  { id: 'cancel_appointments', label: 'Cancel Appointments', description: 'Can cancel appointments' },
  { id: 'complete_appointments', label: 'Complete Appointments', description: 'Can mark appointments as completed' },
];

const Staff = () => {
  const [staffMembers, setStaffMembers] = useState<User[]>([]);
  const [doctors, setDoctors] = useState<Doctor[]>([]);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [selectedStaff, setSelectedStaff] = useState<User | null>(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [staffToDelete, setStaffToDelete] = useState<string | null>(null);
  
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
    permissions: [] as string[],
    assignedDoctors: [] as string[],
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = () => {
    setStaffMembers(getAllStaffAccounts());
    setDoctors(getDoctors());
  };

  const resetForm = () => {
    setFormData({
      name: '',
      email: '',
      password: '',
      confirmPassword: '',
      permissions: [],
      assignedDoctors: [],
    });
  };

  const handleAddStaff = () => {
    setSelectedStaff(null);
    resetForm();
    setDialogOpen(true);
  };

  const handleEditStaff = (staff: User) => {
    setSelectedStaff(staff);
    setFormData({
      name: staff.name,
      email: staff.email,
      password: '',
      confirmPassword: '',
      permissions: staff.permissions || [],
      assignedDoctors: staff.assignedDoctors || [],
    });
    setDialogOpen(true);
  };

  const handleDeleteStaff = (email: string) => {
    setStaffToDelete(email);
    setDeleteDialogOpen(true);
  };

  const confirmDelete = () => {
    if (staffToDelete) {
      const success = deleteStaffAccount(staffToDelete);
      if (success) {
        loadData();
        toast.success('Staff account deleted successfully');
      } else {
        toast.error('Failed to delete staff account');
      }
    }
    setDeleteDialogOpen(false);
    setStaffToDelete(null);
  };

  const handleSave = () => {
    // Validation
    if (!formData.name || !formData.email) {
      toast.error('Please fill in all required fields');
      return;
    }

    if (!selectedStaff) {
      // Creating new staff - password is required
      if (!formData.password || !formData.confirmPassword) {
        toast.error('Password is required for new staff accounts');
        return;
      }
      if (formData.password !== formData.confirmPassword) {
        toast.error('Passwords do not match');
        return;
      }
      if (formData.password.length < 6) {
        toast.error('Password must be at least 6 characters');
        return;
      }
    } else {
      // Editing existing staff - password is optional
      if (formData.password || formData.confirmPassword) {
        if (formData.password !== formData.confirmPassword) {
          toast.error('Passwords do not match');
          return;
        }
        if (formData.password.length < 6) {
          toast.error('Password must be at least 6 characters');
          return;
        }
      }
    }

    if (formData.permissions.length === 0) {
      toast.error('Please select at least one permission');
      return;
    }

    if (formData.assignedDoctors.length === 0) {
      toast.error('Please assign at least one doctor');
      return;
    }

    let success = false;

    if (selectedStaff) {
      // Update existing staff
      success = updateStaffAccount(
        formData.email,
        formData.name,
        formData.permissions,
        formData.assignedDoctors,
        formData.password || undefined
      );
    } else {
      // Create new staff
      success = createStaffAccount(
        formData.email,
        formData.password,
        formData.name,
        formData.permissions,
        formData.assignedDoctors
      );
    }

    if (success) {
      loadData();
      toast.success(selectedStaff ? 'Staff account updated successfully' : 'Staff account created successfully');
      setDialogOpen(false);
    } else {
      toast.error(selectedStaff ? 'Failed to update staff account' : 'Email already exists');
    }
  };

  const togglePermission = (permissionId: string) => {
    setFormData(prev => ({
      ...prev,
      permissions: prev.permissions.includes(permissionId)
        ? prev.permissions.filter(p => p !== permissionId)
        : [...prev.permissions, permissionId],
    }));
  };

  const toggleDoctor = (doctorId: string) => {
    setFormData(prev => ({
      ...prev,
      assignedDoctors: prev.assignedDoctors.includes(doctorId)
        ? prev.assignedDoctors.filter(d => d !== doctorId)
        : [...prev.assignedDoctors, doctorId],
    }));
  };

  const selectAllDoctors = () => {
    setFormData(prev => ({
      ...prev,
      assignedDoctors: doctors.map(d => d.id),
    }));
  };

  const selectAllPermissions = () => {
    setFormData(prev => ({
      ...prev,
      permissions: AVAILABLE_PERMISSIONS.map(p => p.id),
    }));
  };

  return (
    <DashboardLayout>
      <div className="space-y-6 animate-fade-in">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Staff Management</h1>
            <p className="text-muted-foreground mt-2">Create and manage staff accounts with custom permissions</p>
          </div>
          <Button onClick={handleAddStaff} className="bg-primary hover-lift">
            <UserPlus className="w-4 h-4 mr-2" />
            Add Staff Member
          </Button>
        </div>

        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {staffMembers.map((staff) => (
            <Card key={staff.email} className="glass-card hover-lift">
              <CardContent className="p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <Avatar className="w-12 h-12 ring-2 ring-primary/20">
                      <AvatarFallback className="bg-primary text-primary-foreground">
                        {staff.name.charAt(0).toUpperCase()}
                      </AvatarFallback>
                    </Avatar>
                    <div>
                      <h3 className="font-bold">{staff.name}</h3>
                      <p className="text-xs text-muted-foreground">{staff.email}</p>
                    </div>
                  </div>
                  <Badge variant="outline" className="bg-primary/10">Staff</Badge>
                </div>

                <div className="space-y-3 mb-4">
                  <div>
                    <p className="text-xs font-medium text-muted-foreground mb-1">Permissions</p>
                    <div className="flex flex-wrap gap-1">
                      {staff.permissions?.map((perm) => (
                        <Badge key={perm} variant="outline" className="text-xs">
                          {AVAILABLE_PERMISSIONS.find(p => p.id === perm)?.label.replace(' Appointments', '')}
                        </Badge>
                      ))}
                    </div>
                  </div>

                  <div>
                    <p className="text-xs font-medium text-muted-foreground mb-1">Assigned Doctors ({staff.assignedDoctors?.length || 0})</p>
                    <div className="flex flex-wrap gap-1">
                      {staff.assignedDoctors?.slice(0, 3).map((doctorId) => {
                        const doctor = doctors.find(d => d.id === doctorId);
                        return doctor ? (
                          <Badge key={doctorId} variant="outline" className="text-xs">
                            {doctor.name.split(' ')[1] || doctor.name}
                          </Badge>
                        ) : null;
                      })}
                      {(staff.assignedDoctors?.length || 0) > 3 && (
                        <Badge variant="outline" className="text-xs">
                          +{(staff.assignedDoctors?.length || 0) - 3} more
                        </Badge>
                      )}
                    </div>
                  </div>
                </div>

                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    className="flex-1 hover-lift"
                    onClick={() => handleEditStaff(staff)}
                  >
                    <Edit className="w-3 h-3 mr-1" />
                    Edit
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    className="hover-lift text-red-600 hover:bg-red-50"
                    onClick={() => handleDeleteStaff(staff.email)}
                  >
                    <Trash2 className="w-3 h-3 mr-1" />
                    Delete
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}

          {staffMembers.length === 0 && (
            <Card className="glass-card col-span-full">
              <CardContent className="text-center py-12">
                <UsersIcon className="w-12 h-12 text-muted-foreground mx-auto mb-3 opacity-50" />
                <p className="text-muted-foreground mb-4">No staff members added yet</p>
                <Button onClick={handleAddStaff} variant="outline" className="hover-lift">
                  <UserPlus className="w-4 h-4 mr-2" />
                  Add Your First Staff Member
                </Button>
              </CardContent>
            </Card>
          )}
        </div>

        {/* Add/Edit Dialog */}
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogContent className="glass-card max-w-3xl max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>
                {selectedStaff ? 'Edit Staff Account' : 'Create New Staff Account'}
              </DialogTitle>
            </DialogHeader>

            <div className="space-y-6">
              {/* Basic Information */}
              <div className="space-y-4">
                <h3 className="font-semibold flex items-center gap-2">
                  <Mail className="w-4 h-4" />
                  Basic Information
                </h3>
                
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="name">Full Name *</Label>
                    <Input
                      id="name"
                      value={formData.name}
                      onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                      placeholder="John Smith"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="email">Email *</Label>
                    <Input
                      id="email"
                      type="email"
                      value={formData.email}
                      onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                      placeholder="staff@clinic.com"
                      disabled={!!selectedStaff}
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="password">
                      Password {!selectedStaff && '*'} {selectedStaff && '(leave blank to keep current)'}
                    </Label>
                    <Input
                      id="password"
                      type="password"
                      value={formData.password}
                      onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                      placeholder="••••••••"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="confirmPassword">
                      Confirm Password {!selectedStaff && '*'}
                    </Label>
                    <Input
                      id="confirmPassword"
                      type="password"
                      value={formData.confirmPassword}
                      onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
                      placeholder="••••••••"
                    />
                  </div>
                </div>
              </div>

              {/* Permissions */}
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="font-semibold flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4" />
                    Permissions *
                  </h3>
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={selectAllPermissions}
                  >
                    Select All
                  </Button>
                </div>

                <div className="grid gap-3">
                  {AVAILABLE_PERMISSIONS.map((permission) => (
                    <div
                      key={permission.id}
                      className={cn(
                        "flex items-start gap-3 p-3 rounded-lg border-2 transition-all cursor-pointer hover:bg-muted/50",
                        formData.permissions.includes(permission.id)
                          ? "border-primary bg-primary/5"
                          : "border-border"
                      )}
                      onClick={() => togglePermission(permission.id)}
                    >
                      <Checkbox
                        checked={formData.permissions.includes(permission.id)}
                        onCheckedChange={() => togglePermission(permission.id)}
                      />
                      <div className="flex-1">
                        <p className="font-medium text-sm">{permission.label}</p>
                        <p className="text-xs text-muted-foreground">{permission.description}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Assigned Doctors */}
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="font-semibold flex items-center gap-2">
                    <UsersIcon className="w-4 h-4" />
                    Assign Doctors * ({formData.assignedDoctors.length} selected)
                  </h3>
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={selectAllDoctors}
                  >
                    Select All
                  </Button>
                </div>

                <div className="grid gap-3 max-h-64 overflow-y-auto">
                  {doctors.map((doctor) => (
                    <div
                      key={doctor.id}
                      className={cn(
                        "flex items-center gap-3 p-3 rounded-lg border-2 transition-all cursor-pointer hover:bg-muted/50",
                        formData.assignedDoctors.includes(doctor.id)
                          ? "border-primary bg-primary/5"
                          : "border-border"
                      )}
                      onClick={() => toggleDoctor(doctor.id)}
                    >
                      <Checkbox
                        checked={formData.assignedDoctors.includes(doctor.id)}
                        onCheckedChange={() => toggleDoctor(doctor.id)}
                      />
                      <Avatar className="w-10 h-10">
                        <AvatarImage src={doctor.image} alt={doctor.name} />
                        <AvatarFallback>{doctor.name.charAt(0)}</AvatarFallback>
                      </Avatar>
                      <div className="flex-1">
                        <p className="font-medium text-sm">{doctor.name}</p>
                        <p className="text-xs text-muted-foreground">{doctor.specialty}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <DialogFooter>
              <Button variant="outline" onClick={() => setDialogOpen(false)}>
                Cancel
              </Button>
              <Button onClick={handleSave} className="bg-primary">
                {selectedStaff ? 'Update Account' : 'Create Account'}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>

        {/* Delete Confirmation Dialog */}
        <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
          <AlertDialogContent className="glass-card">
            <AlertDialogHeader>
              <AlertDialogTitle>Delete Staff Account?</AlertDialogTitle>
              <AlertDialogDescription>
                This will permanently delete this staff account. The staff member will no longer be able to log in. This action cannot be undone.
              </AlertDialogDescription>
            </AlertDialogHeader>
            <AlertDialogFooter>
              <AlertDialogCancel>Cancel</AlertDialogCancel>
              <AlertDialogAction onClick={confirmDelete} className="bg-destructive">
                Delete Account
              </AlertDialogAction>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialog>
      </div>
    </DashboardLayout>
  );
};

export default Staff;
