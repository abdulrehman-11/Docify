import { useState, useEffect } from 'react';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Clock, Save, Edit2, X } from 'lucide-react';
import { clinicApi } from '@/lib/api';
import type { ClinicHours, ClinicHoursUpdate } from '@/lib/api/types';
import { toast } from 'sonner';

const daysOfWeek = [
  { id: 0, name: 'Monday' },
  { id: 1, name: 'Tuesday' },
  { id: 2, name: 'Wednesday' },
  { id: 3, name: 'Thursday' },
  { id: 4, name: 'Friday' },
  { id: 5, name: 'Saturday' },
  { id: 6, name: 'Sunday' },
];

const Clinic = () => {
  const [clinicHours, setClinicHours] = useState<ClinicHours[]>([]);
  const [loading, setLoading] = useState(true);
  const [editingDay, setEditingDay] = useState<number | null>(null);
  const [editForm, setEditForm] = useState<{
    start_time: string;
    end_time: string;
    is_active: boolean;
  }>({
    start_time: '',
    end_time: '',
    is_active: true,
  });

  useEffect(() => {
    loadClinicHours();
  }, []);

  const loadClinicHours = async () => {
    try {
      setLoading(true);
      const data = await clinicApi.getHours();
      setClinicHours(data);
    } catch (error: any) {
      toast.error('Failed to load clinic hours');
    } finally {
      setLoading(false);
    }
  };

  const getHoursForDay = (dayOfWeek: number) => {
    return clinicHours.find((h) => h.day_of_week === dayOfWeek);
  };

  const startEditing = (dayOfWeek: number) => {
    const hours = getHoursForDay(dayOfWeek);
    if (hours) {
      setEditForm({
        start_time: hours.start_time,
        end_time: hours.end_time,
        is_active: hours.is_active,
      });
      setEditingDay(dayOfWeek);
    }
  };

  const cancelEditing = () => {
    setEditingDay(null);
    setEditForm({
      start_time: '',
      end_time: '',
      is_active: true,
    });
  };

  const saveHours = async (dayOfWeek: number) => {
    const hours = getHoursForDay(dayOfWeek);
    if (!hours) return;

    try {
      const updateData: ClinicHoursUpdate = {
        start_time: editForm.start_time,
        end_time: editForm.end_time,
        is_active: editForm.is_active,
      };

      await clinicApi.updateHours(hours.id, updateData);
      toast.success('Clinic hours updated successfully');
      await loadClinicHours();
      cancelEditing();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to update clinic hours');
    }
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
        <div>
          <h1 className="text-3xl font-bold gradient-text">Clinic Hours</h1>
          <p className="text-muted-foreground mt-1">
            Manage clinic operating hours
          </p>
        </div>

        <Card className="glass-card">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Clock className="w-5 h-5" />
              Operating Hours
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {daysOfWeek.map((day) => {
                const hours = getHoursForDay(day.id);
                const isEditing = editingDay === day.id;
                
                return (
                  <div key={day.id} className="flex items-center gap-4 p-4 glass rounded-xl">
                    <div className="w-32">
                      <Label className="text-base font-medium">{day.name}</Label>
                    </div>
                    
                    {isEditing ? (
                      <>
                        <div className="flex-1 flex items-center gap-4">
                          <div className="flex items-center gap-2">
                            <Switch
                              checked={editForm.is_active}
                              onCheckedChange={(checked) => 
                                setEditForm({ ...editForm, is_active: checked })
                              }
                            />
                            <Label className="text-sm">
                              {editForm.is_active ? 'Open' : 'Closed'}
                            </Label>
                          </div>
                          
                          {editForm.is_active && (
                            <>
                              <div className="flex items-center gap-2">
                                <Label className="text-sm">From:</Label>
                                <Input
                                  type="time"
                                  value={editForm.start_time}
                                  onChange={(e) => 
                                    setEditForm({ ...editForm, start_time: e.target.value })
                                  }
                                  className="w-32"
                                />
                              </div>
                              <div className="flex items-center gap-2">
                                <Label className="text-sm">To:</Label>
                                <Input
                                  type="time"
                                  value={editForm.end_time}
                                  onChange={(e) => 
                                    setEditForm({ ...editForm, end_time: e.target.value })
                                  }
                                  className="w-32"
                                />
                              </div>
                            </>
                          )}
                        </div>
                        
                        <div className="flex gap-2">
                          <Button
                            size="sm"
                            onClick={() => saveHours(day.id)}
                          >
                            <Save className="w-4 h-4 mr-1" />
                            Save
                          </Button>
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={cancelEditing}
                          >
                            <X className="w-4 h-4 mr-1" />
                            Cancel
                          </Button>
                        </div>
                      </>
                    ) : (
                      <>
                        <div className="flex-1">
                          {hours?.is_active ? (
                            <p className="text-sm">
                              {hours.start_time} - {hours.end_time}
                            </p>
                          ) : (
                            <p className="text-sm text-muted-foreground">Closed</p>
                          )}
                        </div>
                        
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => startEditing(day.id)}
                        >
                          <Edit2 className="w-4 h-4 mr-1" />
                          Edit
                        </Button>
                      </>
                    )}
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

export default Clinic;
