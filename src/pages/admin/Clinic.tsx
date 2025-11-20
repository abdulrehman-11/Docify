import { useState, useEffect } from 'react';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Building2, Phone, Mail, MapPin, Clock, Save } from 'lucide-react';
import { ClinicInfo } from '@/lib/mockData';
import { getClinicInfo, saveClinicInfo } from '@/lib/storage';
import { toast } from 'sonner';

const Clinic = () => {
  const [clinicInfo, setClinicInfo] = useState<ClinicInfo | null>(null);
  const [isEditing, setIsEditing] = useState(false);

  const daysOfWeek = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];

  useEffect(() => {
    setClinicInfo(getClinicInfo());
  }, []);

  const handleSave = () => {
    if (!clinicInfo) return;

    if (!clinicInfo.name || !clinicInfo.address || !clinicInfo.phone || !clinicInfo.email) {
      toast.error('Please fill in all required fields');
      return;
    }

    saveClinicInfo(clinicInfo);
    setIsEditing(false);
    toast.success('Clinic information updated successfully');
  };

  const updateHours = (day: string, field: 'open' | 'close', value: string) => {
    if (!clinicInfo) return;
    const updatedHours = clinicInfo.hours.map(h =>
      h.day === day ? { ...h, [field]: value } : h
    );
    setClinicInfo({ ...clinicInfo, hours: updatedHours });
  };

  if (!clinicInfo) {
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
      <div className="space-y-6 animate-fade-in">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Clinic Information</h1>
            <p className="text-muted-foreground mt-2">Manage your clinic's contact details and operating hours</p>
          </div>
          {!isEditing ? (
            <Button onClick={() => setIsEditing(true)} className="bg-primary hover-lift">
              Edit Information
            </Button>
          ) : (
            <div className="flex gap-2">
              <Button variant="outline" onClick={() => {
                setClinicInfo(getClinicInfo());
                setIsEditing(false);
              }}>
                Cancel
              </Button>
              <Button onClick={handleSave} className="bg-primary hover-lift">
                <Save className="w-4 h-4 mr-2" />
                Save Changes
              </Button>
            </div>
          )}
        </div>

        <div className="grid gap-6 lg:grid-cols-2">
          {/* Basic Information */}
          <Card className="glass-card">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Building2 className="w-5 h-5" />
                Basic Information
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="name">Clinic Name *</Label>
                <Input
                  id="name"
                  value={clinicInfo.name}
                  onChange={(e) => setClinicInfo({ ...clinicInfo, name: e.target.value })}
                  disabled={!isEditing}
                  className={!isEditing ? 'bg-muted' : ''}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="address" className="flex items-center gap-2">
                  <MapPin className="w-4 h-4" />
                  Address *
                </Label>
                <Input
                  id="address"
                  value={clinicInfo.address}
                  onChange={(e) => setClinicInfo({ ...clinicInfo, address: e.target.value })}
                  disabled={!isEditing}
                  className={!isEditing ? 'bg-muted' : ''}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="phone" className="flex items-center gap-2">
                  <Phone className="w-4 h-4" />
                  Phone Number *
                </Label>
                <Input
                  id="phone"
                  value={clinicInfo.phone}
                  onChange={(e) => setClinicInfo({ ...clinicInfo, phone: e.target.value })}
                  disabled={!isEditing}
                  className={!isEditing ? 'bg-muted' : ''}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="email" className="flex items-center gap-2">
                  <Mail className="w-4 h-4" />
                  Email Address *
                </Label>
                <Input
                  id="email"
                  type="email"
                  value={clinicInfo.email}
                  onChange={(e) => setClinicInfo({ ...clinicInfo, email: e.target.value })}
                  disabled={!isEditing}
                  className={!isEditing ? 'bg-muted' : ''}
                />
              </div>
            </CardContent>
          </Card>

          {/* Operating Hours */}
          <Card className="glass-card">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Clock className="w-5 h-5" />
                Operating Hours
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {daysOfWeek.map((day) => {
                  const dayHours = clinicInfo.hours.find(h => h.day === day);
                  return (
                    <div key={day} className="grid grid-cols-5 gap-3 items-center">
                      <span className="col-span-2 font-medium text-sm">{day}</span>
                      {isEditing ? (
                        <>
                          <Input
                            type="time"
                            value={dayHours?.open || ''}
                            onChange={(e) => updateHours(day, 'open', e.target.value)}
                            className="col-span-1 h-9 text-sm"
                          />
                          <Input
                            type="time"
                            value={dayHours?.close || ''}
                            onChange={(e) => updateHours(day, 'close', e.target.value)}
                            className="col-span-1 h-9 text-sm"
                          />
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => updateHours(day, 'open', 'Closed')}
                            className="text-xs"
                          >
                            Closed
                          </Button>
                        </>
                      ) : (
                        <span className="col-span-3 text-sm text-muted-foreground">
                          {dayHours?.open === 'Closed' ? 'Closed' : `${dayHours?.open} - ${dayHours?.close}`}
                        </span>
                      )}
                    </div>
                  );
                })}
              </div>
              {isEditing && (
                <p className="text-xs text-muted-foreground mt-4">
                  Click "Closed" for days the clinic is not open
                </p>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Preview Card */}
        <Card className="glass-card">
          <CardHeader>
            <CardTitle>Preview</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="p-6 bg-gradient-to-br from-primary/10 to-accent/10 rounded-xl">
              <h2 className="text-2xl font-bold mb-4">{clinicInfo.name}</h2>
              <div className="grid md:grid-cols-2 gap-6">
                <div className="space-y-3">
                  <div className="flex items-start gap-3">
                    <MapPin className="w-5 h-5 text-primary mt-0.5" />
                    <div>
                      <p className="font-medium text-sm">Address</p>
                      <p className="text-sm text-muted-foreground">{clinicInfo.address}</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <Phone className="w-5 h-5 text-primary mt-0.5" />
                    <div>
                      <p className="font-medium text-sm">Phone</p>
                      <p className="text-sm text-muted-foreground">{clinicInfo.phone}</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <Mail className="w-5 h-5 text-primary mt-0.5" />
                    <div>
                      <p className="font-medium text-sm">Email</p>
                      <p className="text-sm text-muted-foreground">{clinicInfo.email}</p>
                    </div>
                  </div>
                </div>
                <div>
                  <div className="flex items-center gap-2 mb-3">
                    <Clock className="w-5 h-5 text-primary" />
                    <p className="font-medium text-sm">Hours of Operation</p>
                  </div>
                  <div className="space-y-1">
                    {clinicInfo.hours.map((h) => (
                      <div key={h.day} className="flex justify-between text-sm">
                        <span className="text-muted-foreground">{h.day}</span>
                        <span className="font-medium">
                          {h.open === 'Closed' ? 'Closed' : `${h.open} - ${h.close}`}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
};

export default Clinic;

