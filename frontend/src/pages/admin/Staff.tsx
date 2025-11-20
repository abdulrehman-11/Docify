import { useState, useEffect } from 'react';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Checkbox } from '@/components/ui/checkbox';
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
import { UserPlus, Edit2, Trash2, Users as UsersIcon } from 'lucide-react';
import { staffApi } from '@/lib/api';
import type { Staff, StaffCreate, StaffUpdate } from '@/lib/api/types';
import { toast } from 'sonner';

const AVAILABLE_PERMISSIONS = [
  { id: 'view_appointments', label: 'View Appointments', description: 'Can view appointment schedules' },
  { id: 'manage_appointments', label: 'Manage Appointments', description: 'Can create, edit, and cancel appointments' },
  { id: 'view_patients', label: 'View Patients', description: 'Can view patient information' },
  { id: 'manage_patients', label: 'Manage Patients', description: 'Can create, edit, and delete patients' },
  { id: 'manage_clinic', label: 'Manage Clinic', description: 'Can manage clinic hours and settings' },
];

const StaffManagement = () => {
  const [staffMembers, setStaffMembers] = useState<Staff[]>([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [selectedStaff, setSelectedStaff] = useState<Staff | null>(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [staffToDelete, setStaffToDelete] = useState<Staff | null>(null);
  
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
    permissions: {} as Record<string, boolean>,
  });

  useEffect(() => {
    loadStaff();
  }, []);

  const loadStaff = async () => {
    try {
      setLoading(true);
      const response = await staffApi.list({ page: 1, page_size: 100 });
      setStaffMembers(response.staff);
    } catch (error: any) {
      toast.error('Failed to load staff members');
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setFormData({
      name: '',
      email: '',
      password: '',
      confirmPassword: '',
      permissions: {},
    });
  };

  const handleAddStaff = () => {
    setSelectedStaff(null);
    resetForm();
    setDialogOpen(true);
  };

  const handleEditStaff = (staff: Staff) => {
    setSelectedStaff(staff);
    setFormData({
      name: staff.name,
      email: staff.email,
      password: '',
      confirmPassword: '',
      permissions: staff.permissions || {},
    });
    setDialogOpen(true);
  };

  const handleDeleteStaff = (staff: Staff) => {
    setStaffToDelete(staff);
    setDeleteDialogOpen(true);
  };

  const confirmDelete = async () => {
    if (staffToDelete) {
      try {
        await staffApi.delete(staffToDelete.id);
        await loadStaff();
        toast.success('Staff member deleted successfully');
      } catch (error: any) {
        toast.error(error.response?.data?.detail || 'Failed to delete staff member');
      }
    }
    setDeleteDialogOpen(false);
    setStaffToDelete(null);
  };

  const handleSave = async () => {
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

    // Check at least one permission
    const hasPermissions = Object.values(formData.permissions).some(v => v === true);
    if (!hasPermissions) {
      toast.error('Please select at least one permission');
      return;
    }

    try {
      if (selectedStaff) {
        // Update existing staff
        const updateData: StaffUpdate = {
          name: formData.name,
          email: formData.email,
          permissions: formData.permissions,
        };
        if (formData.password) {
          updateData.password = formData.password;
        }
        await staffApi.update(selectedStaff.id, updateData);
        toast.success('Staff member updated successfully');
      } else {
        // Create new staff
        const createData: StaffCreate = {
          name: formData.name,
          email: formData.email,
          password: formData.password,
          role: 'staff',
          permissions: formData.permissions,
        };
        await staffApi.create(createData);
        toast.success('Staff member created successfully');
      }
      
      await loadStaff();
      setDialogOpen(false);
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to save staff member');
    }
  };

  const togglePermission = (permissionId: string) => {
    setFormData(prev => ({
      ...prev,
      permissions: {
        ...prev.permissions,
        [permissionId]: !prev.permissions[permissionId],
      },
    }));
  };

  const getActivePermissions = (permissions: Record<string, boolean>) => {
    return Object.entries(permissions)
      .filter(([_, value]) => value === true)
      .map(([key]) => key);
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

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold gradient-text">Staff Management</h1>
            <p className="text-muted-foreground mt-1">
              Manage clinic staff and their permissions
            </p>
          </div>
          <Button onClick={handleAddStaff} className="gap-2">
            <UserPlus className="w-4 h-4" />
            Add Staff Member
          </Button>
        </div>

        <Card className="glass-card">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <UsersIcon className="w-5 h-5" />
              Staff Members ({staffMembers.length})
            </CardTitle>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Name</TableHead>
                  <TableHead>Email</TableHead>
                  <TableHead>Permissions</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {staffMembers.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={5} className="text-center text-muted-foreground py-8">
                      No staff members found. Create your first staff account.
                    </TableCell>
                  </TableRow>
                ) : (
                  staffMembers.map((staff) => {
                    const activePerms = getActivePermissions(staff.permissions);
                    return (
                      <TableRow key={staff.id}>
                        <TableCell className="font-medium">{staff.name}</TableCell>
                        <TableCell>{staff.email}</TableCell>
                        <TableCell>
                          <div className="flex flex-wrap gap-1">
                            {activePerms.length > 0 ? (
                              activePerms.slice(0, 2).map(perm => (
                                <Badge key={perm} variant="secondary" className="text-xs">
                                  {perm.replace('_', ' ')}
                                </Badge>
                              ))
                            ) : (
                              <span className="text-xs text-muted-foreground">No permissions</span>
                            )}
                            {activePerms.length > 2 && (
                              <Badge variant="outline" className="text-xs">
                                +{activePerms.length - 2} more
                              </Badge>
                            )}
                          </div>
                        </TableCell>
                        <TableCell>
                          <Badge variant={staff.is_active ? 'default' : 'secondary'} className={staff.is_active ? 'bg-green-500' : ''}>
                            {staff.is_active ? 'Active' : 'Inactive'}
                          </Badge>
                        </TableCell>
                        <TableCell className="text-right">
                          <div className="flex justify-end gap-2">
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => handleEditStaff(staff)}
                            >
                              <Edit2 className="w-4 h-4 mr-1" />
                              Edit
                            </Button>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => handleDeleteStaff(staff)}
                              className="text-red-500"
                            >
                              <Trash2 className="w-4 h-4 mr-1" />
                              Delete
                            </Button>
                          </div>
                        </TableCell>
                      </TableRow>
                    );
                  })
                )}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      </div>

      {/* Create/Edit Staff Dialog */}
      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent className="sm:max-w-[600px]">
          <DialogHeader>
            <DialogTitle>
              {selectedStaff ? 'Edit Staff Member' : 'Add New Staff Member'}
            </DialogTitle>
            <DialogDescription>
              {selectedStaff
                ? 'Update staff information and permissions'
                : 'Create a new staff account with specific permissions'}
            </DialogDescription>
          </DialogHeader>

          <div className="grid gap-4 py-4">
            <div className="grid gap-2">
              <Label htmlFor="name">Full Name *</Label>
              <Input
                id="name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="John Doe"
              />
            </div>

            <div className="grid gap-2">
              <Label htmlFor="email">Email *</Label>
              <Input
                id="email"
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                placeholder="john@example.com"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="grid gap-2">
                <Label htmlFor="password">
                  Password {!selectedStaff && '*'}
                  {selectedStaff && <span className="text-xs text-muted-foreground ml-1">(leave blank to keep current)</span>}
                </Label>
                <Input
                  id="password"
                  type="password"
                  value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                  placeholder={selectedStaff ? "Leave blank to keep current" : "Minimum 6 characters"}
                />
              </div>

              <div className="grid gap-2">
                <Label htmlFor="confirmPassword">
                  Confirm Password {!selectedStaff && '*'}
                </Label>
                <Input
                  id="confirmPassword"
                  type="password"
                  value={formData.confirmPassword}
                  onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
                  placeholder="Confirm password"
                />
              </div>
            </div>

            <div className="grid gap-2">
              <Label>Permissions *</Label>
              <div className="space-y-3 border rounded-lg p-4">
                {AVAILABLE_PERMISSIONS.map((permission) => (
                  <div key={permission.id} className="flex items-start space-x-3">
                    <Checkbox
                      id={permission.id}
                      checked={formData.permissions[permission.id] || false}
                      onCheckedChange={() => togglePermission(permission.id)}
                    />
                    <div className="grid gap-1">
                      <Label
                        htmlFor={permission.id}
                        className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 cursor-pointer"
                      >
                        {permission.label}
                      </Label>
                      <p className="text-xs text-muted-foreground">
                        {permission.description}
                      </p>
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
            <Button onClick={handleSave}>
              {selectedStaff ? 'Update Staff' : 'Create Staff'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Staff Member</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete{' '}
              <span className="font-semibold">{staffToDelete?.name}</span>? This action cannot be undone.
              The staff member will no longer be able to access the system.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={confirmDelete} className="bg-red-500 hover:bg-red-600">
              Delete Staff
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </DashboardLayout>
  );
};

export default StaffManagement;
