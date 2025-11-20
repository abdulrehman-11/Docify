import { useState, useEffect } from "react";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { Label } from "@/components/ui/label";
import { Users, Search, Plus, Edit, Trash2 } from "lucide-react";
import { patientApi } from "@/lib/api";
import type { Patient } from "@/lib/api/types";
import { toast } from "sonner";

const Patients = () => {
  const [patients, setPatients] = useState<Patient[]>([]);
  const [filteredPatients, setFilteredPatients] = useState<Patient[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [loading, setLoading] = useState(true);
  
  // Dialog states
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  
  // Form states
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    phone: "",
    insurance_provider: "",
  });
  const [selectedPatient, setSelectedPatient] = useState<Patient | null>(null);

  useEffect(() => {
    loadPatients();
  }, []);

  useEffect(() => {
    // Filter patients based on search query
    if (searchQuery.trim() === "") {
      setFilteredPatients(patients);
    } else {
      const query = searchQuery.toLowerCase();
      setFilteredPatients(
        patients.filter(
          (p) =>
            p.name.toLowerCase().includes(query) ||
            p.email.toLowerCase().includes(query) ||
            p.phone.toLowerCase().includes(query) ||
            (p.insurance_provider && p.insurance_provider.toLowerCase().includes(query))
        )
      );
    }
  }, [searchQuery, patients]);

  const loadPatients = async () => {
    try {
      setLoading(true);
      const data = await patientApi.getAll();
      setPatients(data.patients);
      setFilteredPatients(data.patients);
    } catch (error: any) {
      toast.error(error.response?.data?.detail || "Failed to load patients");
    } finally {
      setLoading(false);
    }
  };

  const handleAddPatient = async () => {
    try {
      await patientApi.create(formData);
      toast.success("Patient added successfully");
      setIsAddDialogOpen(false);
      resetForm();
      loadPatients();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || "Failed to add patient");
    }
  };

  const handleEditPatient = async () => {
    if (!selectedPatient) return;
    
    try {
      await patientApi.update(selectedPatient.id, formData);
      toast.success("Patient updated successfully");
      setIsEditDialogOpen(false);
      resetForm();
      loadPatients();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || "Failed to update patient");
    }
  };

  const handleDeletePatient = async () => {
    if (!selectedPatient) return;
    
    try {
      await patientApi.delete(selectedPatient.id);
      toast.success("Patient deleted successfully");
      setIsDeleteDialogOpen(false);
      setSelectedPatient(null);
      loadPatients();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || "Failed to delete patient");
    }
  };

  const openEditDialog = (patient: Patient) => {
    setSelectedPatient(patient);
    setFormData({
      name: patient.name,
      email: patient.email,
      phone: patient.phone,
      insurance_provider: patient.insurance_provider || "",
    });
    setIsEditDialogOpen(true);
  };

  const openDeleteDialog = (patient: Patient) => {
    setSelectedPatient(patient);
    setIsDeleteDialogOpen(true);
  };

  const resetForm = () => {
    setFormData({
      name: "",
      email: "",
      phone: "",
      insurance_provider: "",
    });
    setSelectedPatient(null);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold gradient-text">Patient Management</h1>
            <p className="text-muted-foreground mt-1">
              Manage patient records and information
            </p>
          </div>
          <Button
            onClick={() => {
              resetForm();
              setIsAddDialogOpen(true);
            }}
            className="gradient"
          >
            <Plus className="w-4 h-4 mr-2" />
            Add Patient
          </Button>
        </div>

        <Card className="glass-card">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Users className="w-5 h-5" />
              All Patients
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4" />
                <Input
                  placeholder="Search patients by name, email, phone, or insurance..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10"
                />
              </div>

              {loading ? (
                <div className="text-center py-8 text-muted-foreground">
                  Loading patients...
                </div>
              ) : filteredPatients.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  {searchQuery ? "No patients found matching your search" : "No patients yet"}
                </div>
              ) : (
                <div className="rounded-md border">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Name</TableHead>
                        <TableHead>Email</TableHead>
                        <TableHead>Phone</TableHead>
                        <TableHead>Insurance</TableHead>
                        <TableHead>Registered</TableHead>
                        <TableHead className="text-right">Actions</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {filteredPatients.map((patient) => (
                        <TableRow key={patient.id}>
                          <TableCell className="font-medium">{patient.name}</TableCell>
                          <TableCell>{patient.email}</TableCell>
                          <TableCell>{patient.phone}</TableCell>
                          <TableCell>
                            {patient.insurance_provider || "N/A"}
                          </TableCell>
                          <TableCell>{formatDate(patient.created_at)}</TableCell>
                          <TableCell className="text-right">
                            <div className="flex justify-end gap-2">
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => openEditDialog(patient)}
                              >
                                <Edit className="w-4 h-4" />
                              </Button>
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => openDeleteDialog(patient)}
                              >
                                <Trash2 className="w-4 h-4 text-red-500" />
                              </Button>
                            </div>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Add Patient Dialog */}
      <Dialog open={isAddDialogOpen} onOpenChange={setIsAddDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Add New Patient</DialogTitle>
            <DialogDescription>
              Enter patient information to add them to the system
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label htmlFor="add-name">Name *</Label>
              <Input
                id="add-name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="John Doe"
              />
            </div>
            <div>
              <Label htmlFor="add-email">Email *</Label>
              <Input
                id="add-email"
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                placeholder="john@example.com"
              />
            </div>
            <div>
              <Label htmlFor="add-phone">Phone *</Label>
              <Input
                id="add-phone"
                value={formData.phone}
                onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                placeholder="+1 (555) 123-4567"
              />
            </div>
            <div>
              <Label htmlFor="add-insurance">Insurance Provider</Label>
              <Input
                id="add-insurance"
                value={formData.insurance_provider}
                onChange={(e) =>
                  setFormData({ ...formData, insurance_provider: e.target.value })
                }
                placeholder="Blue Cross Blue Shield"
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsAddDialogOpen(false)}>
              Cancel
            </Button>
            <Button
              onClick={handleAddPatient}
              disabled={!formData.name || !formData.email || !formData.phone}
            >
              Add Patient
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Edit Patient Dialog */}
      <Dialog open={isEditDialogOpen} onOpenChange={setIsEditDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Edit Patient</DialogTitle>
            <DialogDescription>Update patient information</DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label htmlFor="edit-name">Name *</Label>
              <Input
                id="edit-name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              />
            </div>
            <div>
              <Label htmlFor="edit-email">Email *</Label>
              <Input
                id="edit-email"
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              />
            </div>
            <div>
              <Label htmlFor="edit-phone">Phone *</Label>
              <Input
                id="edit-phone"
                value={formData.phone}
                onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
              />
            </div>
            <div>
              <Label htmlFor="edit-insurance">Insurance Provider</Label>
              <Input
                id="edit-insurance"
                value={formData.insurance_provider}
                onChange={(e) =>
                  setFormData({ ...formData, insurance_provider: e.target.value })
                }
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsEditDialogOpen(false)}>
              Cancel
            </Button>
            <Button
              onClick={handleEditPatient}
              disabled={!formData.name || !formData.email || !formData.phone}
            >
              Save Changes
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={isDeleteDialogOpen} onOpenChange={setIsDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Are you sure?</AlertDialogTitle>
            <AlertDialogDescription>
              This will permanently delete the patient record for{" "}
              <strong>{selectedPatient?.name}</strong>. This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={handleDeletePatient} className="bg-red-500">
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </DashboardLayout>
  );
};

export default Patients;
