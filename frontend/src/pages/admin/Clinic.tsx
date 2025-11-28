import { useState, useEffect } from 'react';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Checkbox } from '@/components/ui/checkbox';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Calendar } from '@/components/ui/calendar';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { Clock, Save, Edit2, X, Coffee, CalendarDays, Plus, Trash2, CalendarOff, Copy } from 'lucide-react';
import { clinicApi } from '@/lib/api';
import type { ClinicHours, ClinicHoursUpdate, ClinicHoliday, ClinicHolidayCreate, ClinicHoursBulkUpdate } from '@/lib/api/types';
import { toast } from 'sonner';
import { format } from 'date-fns';
import { cn } from '@/lib/utils';

const daysOfWeek = [
  { id: 0, name: 'Monday', short: 'Mon' },
  { id: 1, name: 'Tuesday', short: 'Tue' },
  { id: 2, name: 'Wednesday', short: 'Wed' },
  { id: 3, name: 'Thursday', short: 'Thu' },
  { id: 4, name: 'Friday', short: 'Fri' },
  { id: 5, name: 'Saturday', short: 'Sat' },
  { id: 6, name: 'Sunday', short: 'Sun' },
];

const Clinic = () => {
  // Clinic Hours State
  const [clinicHours, setClinicHours] = useState<ClinicHours[]>([]);
  const [loading, setLoading] = useState(true);
  const [editingDay, setEditingDay] = useState<number | null>(null);
  const [editForm, setEditForm] = useState<{
    start_time: string;
    end_time: string;
    is_active: boolean;
    break_start: string;
    break_end: string;
    has_break: boolean;
  }>({
    start_time: '',
    end_time: '',
    is_active: true,
    break_start: '',
    break_end: '',
    has_break: false,
  });

  // Bulk Update State
  const [showBulkUpdate, setShowBulkUpdate] = useState(false);
  const [selectedDays, setSelectedDays] = useState<number[]>([]);
  const [bulkForm, setBulkForm] = useState<{
    start_time: string;
    end_time: string;
    is_active: boolean;
    break_start: string;
    break_end: string;
    has_break: boolean;
  }>({
    start_time: '09:00',
    end_time: '17:00',
    is_active: true,
    break_start: '12:00',
    break_end: '13:00',
    has_break: false,
  });

  // Holidays State
  const [holidays, setHolidays] = useState<ClinicHoliday[]>([]);
  const [holidayDialogOpen, setHolidayDialogOpen] = useState(false);
  const [editingHoliday, setEditingHoliday] = useState<ClinicHoliday | null>(null);
  const [holidayForm, setHolidayForm] = useState<{
    date: Date | undefined;
    name: string;
    is_full_day: boolean;
    start_time: string;
    end_time: string;
  }>({
    date: undefined,
    name: '',
    is_full_day: true,
    start_time: '09:00',
    end_time: '17:00',
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [hoursData, holidaysData] = await Promise.all([
        clinicApi.getHours(),
        clinicApi.getHolidays()
      ]);
      setClinicHours(hoursData);
      setHolidays(holidaysData);
    } catch (error: any) {
      toast.error('Failed to load clinic data');
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
        start_time: hours.start_time?.substring(0, 5) || '09:00',
        end_time: hours.end_time?.substring(0, 5) || '17:00',
        is_active: hours.is_active,
        break_start: hours.break_start?.substring(0, 5) || '',
        break_end: hours.break_end?.substring(0, 5) || '',
        has_break: !!(hours.break_start && hours.break_end),
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
      break_start: '',
      break_end: '',
      has_break: false,
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
        break_start: editForm.has_break && editForm.break_start ? editForm.break_start : null,
        break_end: editForm.has_break && editForm.break_end ? editForm.break_end : null,
      };

      await clinicApi.updateHours(hours.id, updateData);
      toast.success('Clinic hours updated successfully');
      await loadData();
      cancelEditing();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to update clinic hours');
    }
  };

  const handleBulkUpdate = async () => {
    if (selectedDays.length === 0) {
      toast.error('Please select at least one day');
      return;
    }

    try {
      const bulkData: ClinicHoursBulkUpdate = {
        day_of_weeks: selectedDays,
        start_time: bulkForm.start_time,
        end_time: bulkForm.end_time,
        is_active: bulkForm.is_active,
        break_start: bulkForm.has_break && bulkForm.break_start ? bulkForm.break_start : null,
        break_end: bulkForm.has_break && bulkForm.break_end ? bulkForm.break_end : null,
      };

      await clinicApi.bulkUpdateHours(bulkData);
      toast.success(`Applied hours to ${selectedDays.length} days`);
      await loadData();
      setShowBulkUpdate(false);
      setSelectedDays([]);
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to bulk update');
    }
  };

  const copyToAllDays = async (dayOfWeek: number) => {
    const hours = getHoursForDay(dayOfWeek);
    if (!hours) return;

    try {
      const bulkData: ClinicHoursBulkUpdate = {
        day_of_weeks: [0, 1, 2, 3, 4, 5, 6],
        start_time: hours.start_time?.substring(0, 5),
        end_time: hours.end_time?.substring(0, 5),
        is_active: hours.is_active,
        break_start: hours.break_start?.substring(0, 5) || null,
        break_end: hours.break_end?.substring(0, 5) || null,
      };

      await clinicApi.bulkUpdateHours(bulkData);
      toast.success('Applied to all days');
      await loadData();
    } catch (error: any) {
      toast.error('Failed to copy to all days');
    }
  };

  // Holiday functions
  const openAddHoliday = () => {
    setEditingHoliday(null);
    setHolidayForm({
      date: undefined,
      name: '',
      is_full_day: true,
      start_time: '09:00',
      end_time: '17:00',
    });
    setHolidayDialogOpen(true);
  };

  const openEditHoliday = (holiday: ClinicHoliday) => {
    setEditingHoliday(holiday);
    setHolidayForm({
      date: new Date(holiday.date),
      name: holiday.name,
      is_full_day: holiday.is_full_day,
      start_time: holiday.start_time?.substring(0, 5) || '09:00',
      end_time: holiday.end_time?.substring(0, 5) || '17:00',
    });
    setHolidayDialogOpen(true);
  };

  const saveHoliday = async () => {
    if (!holidayForm.date || !holidayForm.name) {
      toast.error('Please fill in all required fields');
      return;
    }

    try {
      const data: ClinicHolidayCreate = {
        date: format(holidayForm.date, 'yyyy-MM-dd'),
        name: holidayForm.name,
        is_full_day: holidayForm.is_full_day,
        start_time: !holidayForm.is_full_day ? holidayForm.start_time : null,
        end_time: !holidayForm.is_full_day ? holidayForm.end_time : null,
      };

      if (editingHoliday) {
        await clinicApi.updateHoliday(editingHoliday.id, data);
        toast.success('Holiday updated successfully');
      } else {
        await clinicApi.createHoliday(data);
        toast.success('Holiday added successfully');
      }

      await loadData();
      setHolidayDialogOpen(false);
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to save holiday');
    }
  };

  const deleteHoliday = async (id: number) => {
    try {
      await clinicApi.deleteHoliday(id);
      toast.success('Holiday deleted');
      await loadData();
    } catch (error: any) {
      toast.error('Failed to delete holiday');
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
          <h1 className="text-3xl font-bold gradient-text">Clinic Settings</h1>
          <p className="text-muted-foreground mt-1">
            Manage operating hours, breaks, and holidays
          </p>
        </div>

        <Tabs defaultValue="hours" className="space-y-4">
          <TabsList className="grid w-full grid-cols-2 max-w-md">
            <TabsTrigger value="hours" className="flex items-center gap-2">
              <Clock className="w-4 h-4" />
              Operating Hours
            </TabsTrigger>
            <TabsTrigger value="holidays" className="flex items-center gap-2">
              <CalendarOff className="w-4 h-4" />
              Holidays
            </TabsTrigger>
          </TabsList>

          {/* Operating Hours Tab */}
          <TabsContent value="hours" className="space-y-4">
            {/* Bulk Update Card */}
            <Card className="glass-card">
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle className="text-lg flex items-center gap-2">
                      <Copy className="w-5 h-5" />
                      Apply to Multiple Days
                    </CardTitle>
                    <CardDescription>
                      Set the same hours for multiple days at once
                    </CardDescription>
                  </div>
                  <Button
                    variant={showBulkUpdate ? "secondary" : "outline"}
                    onClick={() => setShowBulkUpdate(!showBulkUpdate)}
                  >
                    {showBulkUpdate ? 'Cancel' : 'Bulk Edit'}
                  </Button>
                </div>
              </CardHeader>
              
              {showBulkUpdate && (
                <CardContent className="space-y-4 border-t pt-4">
                  <div className="flex flex-wrap gap-2">
                    {daysOfWeek.map((day) => (
                      <div key={day.id} className="flex items-center space-x-2">
                        <Checkbox
                          id={`bulk-day-${day.id}`}
                          checked={selectedDays.includes(day.id)}
                          onCheckedChange={(checked) => {
                            if (checked) {
                              setSelectedDays([...selectedDays, day.id]);
                            } else {
                              setSelectedDays(selectedDays.filter(d => d !== day.id));
                            }
                          }}
                        />
                        <Label htmlFor={`bulk-day-${day.id}`} className="text-sm cursor-pointer">
                          {day.short}
                        </Label>
                      </div>
                    ))}
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => setSelectedDays([0, 1, 2, 3, 4])}
                    >
                      Weekdays
                    </Button>
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => setSelectedDays([0, 1, 2, 3, 4, 5, 6])}
                    >
                      All
                    </Button>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                    <div className="flex items-center gap-2">
                      <Switch
                        checked={bulkForm.is_active}
                        onCheckedChange={(checked) => 
                          setBulkForm({ ...bulkForm, is_active: checked })
                        }
                      />
                      <Label>{bulkForm.is_active ? 'Open' : 'Closed'}</Label>
                    </div>
                    
                    {bulkForm.is_active && (
                      <>
                        <div className="flex items-center gap-2">
                          <Label className="text-sm whitespace-nowrap">From:</Label>
                          <Input
                            type="time"
                            value={bulkForm.start_time}
                            onChange={(e) => setBulkForm({ ...bulkForm, start_time: e.target.value })}
                            className="w-full"
                          />
                        </div>
                        <div className="flex items-center gap-2">
                          <Label className="text-sm whitespace-nowrap">To:</Label>
                          <Input
                            type="time"
                            value={bulkForm.end_time}
                            onChange={(e) => setBulkForm({ ...bulkForm, end_time: e.target.value })}
                            className="w-full"
                          />
                        </div>
                        <div className="flex items-center gap-2">
                          <Switch
                            checked={bulkForm.has_break}
                            onCheckedChange={(checked) => 
                              setBulkForm({ ...bulkForm, has_break: checked })
                            }
                          />
                          <Label className="text-sm">Add Break</Label>
                        </div>
                      </>
                    )}
                  </div>

                  {bulkForm.is_active && bulkForm.has_break && (
                    <div className="flex items-center gap-4 p-3 bg-muted/50 rounded-lg">
                      <Coffee className="w-4 h-4 text-muted-foreground" />
                      <div className="flex items-center gap-2">
                        <Label className="text-sm">Break:</Label>
                        <Input
                          type="time"
                          value={bulkForm.break_start}
                          onChange={(e) => setBulkForm({ ...bulkForm, break_start: e.target.value })}
                          className="w-28"
                        />
                        <span>-</span>
                        <Input
                          type="time"
                          value={bulkForm.break_end}
                          onChange={(e) => setBulkForm({ ...bulkForm, break_end: e.target.value })}
                          className="w-28"
                        />
                      </div>
                    </div>
                  )}

                  <Button onClick={handleBulkUpdate} disabled={selectedDays.length === 0}>
                    <Save className="w-4 h-4 mr-2" />
                    Apply to {selectedDays.length} Day{selectedDays.length !== 1 ? 's' : ''}
                  </Button>
                </CardContent>
              )}
            </Card>

            {/* Weekly Hours Card */}
            <Card className="glass-card">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Clock className="w-5 h-5" />
                  Weekly Schedule
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {daysOfWeek.map((day) => {
                    const hours = getHoursForDay(day.id);
                    const isEditing = editingDay === day.id;
                    
                    return (
                      <div key={day.id} className="flex flex-col gap-2 p-4 glass rounded-xl">
                        <div className="flex items-center gap-4">
                          <div className="w-28">
                            <Label className="text-base font-medium">{day.name}</Label>
                          </div>
                          
                          {isEditing ? (
                            <>
                              <div className="flex-1 flex flex-wrap items-center gap-4">
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
                                    <div className="flex items-center gap-2">
                                      <Switch
                                        checked={editForm.has_break}
                                        onCheckedChange={(checked) => 
                                          setEditForm({ ...editForm, has_break: checked })
                                        }
                                      />
                                      <Label className="text-sm flex items-center gap-1">
                                        <Coffee className="w-3 h-3" />
                                        Break
                                      </Label>
                                    </div>
                                  </>
                                )}
                              </div>
                              
                              <div className="flex gap-2">
                                <Button size="sm" onClick={() => saveHours(day.id)}>
                                  <Save className="w-4 h-4 mr-1" />
                                  Save
                                </Button>
                                <Button size="sm" variant="ghost" onClick={cancelEditing}>
                                  <X className="w-4 h-4 mr-1" />
                                  Cancel
                                </Button>
                              </div>
                            </>
                          ) : (
                            <>
                              <div className="flex-1 flex items-center gap-4">
                                {hours?.is_active ? (
                                  <>
                                    <p className="text-sm font-medium">
                                      {hours.start_time?.substring(0, 5)} - {hours.end_time?.substring(0, 5)}
                                    </p>
                                    {hours.break_start && hours.break_end && (
                                      <span className="text-xs text-muted-foreground flex items-center gap-1 bg-muted px-2 py-1 rounded">
                                        <Coffee className="w-3 h-3" />
                                        Break: {hours.break_start?.substring(0, 5)} - {hours.break_end?.substring(0, 5)}
                                      </span>
                                    )}
                                  </>
                                ) : (
                                  <p className="text-sm text-muted-foreground">Closed</p>
                                )}
                              </div>
                              
                              <div className="flex gap-1">
                                <Button
                                  size="sm"
                                  variant="ghost"
                                  onClick={() => copyToAllDays(day.id)}
                                  title="Copy to all days"
                                >
                                  <Copy className="w-4 h-4" />
                                </Button>
                                <Button
                                  size="sm"
                                  variant="ghost"
                                  onClick={() => startEditing(day.id)}
                                >
                                  <Edit2 className="w-4 h-4 mr-1" />
                                  Edit
                                </Button>
                              </div>
                            </>
                          )}
                        </div>

                        {/* Break time editing row */}
                        {isEditing && editForm.is_active && editForm.has_break && (
                          <div className="flex items-center gap-4 pl-28 mt-2 p-3 bg-muted/50 rounded-lg">
                            <Coffee className="w-4 h-4 text-muted-foreground" />
                            <div className="flex items-center gap-2">
                              <Label className="text-sm">Break from:</Label>
                              <Input
                                type="time"
                                value={editForm.break_start}
                                onChange={(e) => 
                                  setEditForm({ ...editForm, break_start: e.target.value })
                                }
                                className="w-28"
                              />
                            </div>
                            <div className="flex items-center gap-2">
                              <Label className="text-sm">to:</Label>
                              <Input
                                type="time"
                                value={editForm.break_end}
                                onChange={(e) => 
                                  setEditForm({ ...editForm, break_end: e.target.value })
                                }
                                className="w-28"
                              />
                            </div>
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Holidays Tab */}
          <TabsContent value="holidays" className="space-y-4">
            <Card className="glass-card">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle className="flex items-center gap-2">
                      <CalendarDays className="w-5 h-5" />
                      Clinic Holidays
                    </CardTitle>
                    <CardDescription>
                      Add specific dates when the clinic will be closed or have modified hours
                    </CardDescription>
                  </div>
                  <Button onClick={openAddHoliday}>
                    <Plus className="w-4 h-4 mr-2" />
                    Add Holiday
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                {holidays.length === 0 ? (
                  <div className="text-center py-8 text-muted-foreground">
                    <CalendarOff className="w-12 h-12 mx-auto mb-3 opacity-50" />
                    <p>No holidays added yet</p>
                    <p className="text-sm mt-1">Add holidays like Christmas, New Year, etc.</p>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {holidays.map((holiday) => (
                      <div key={holiday.id} className="flex items-center gap-4 p-4 glass rounded-xl">
                        <div className="flex-shrink-0 w-16 h-16 bg-primary/10 rounded-lg flex flex-col items-center justify-center">
                          <span className="text-xs text-muted-foreground">
                            {format(new Date(holiday.date), 'MMM')}
                          </span>
                          <span className="text-xl font-bold">
                            {format(new Date(holiday.date), 'd')}
                          </span>
                        </div>
                        
                        <div className="flex-1">
                          <h4 className="font-medium">{holiday.name}</h4>
                          <p className="text-sm text-muted-foreground">
                            {format(new Date(holiday.date), 'EEEE, MMMM d, yyyy')}
                          </p>
                          {holiday.is_full_day ? (
                            <span className="text-xs text-red-500 font-medium">Closed all day</span>
                          ) : (
                            <span className="text-xs text-amber-500 font-medium">
                              Modified hours: {holiday.start_time?.substring(0, 5)} - {holiday.end_time?.substring(0, 5)}
                            </span>
                          )}
                        </div>
                        
                        <div className="flex gap-2">
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={() => openEditHoliday(holiday)}
                          >
                            <Edit2 className="w-4 h-4" />
                          </Button>
                          <Button
                            size="sm"
                            variant="ghost"
                            className="text-destructive hover:text-destructive"
                            onClick={() => deleteHoliday(holiday.id)}
                          >
                            <Trash2 className="w-4 h-4" />
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        {/* Holiday Dialog */}
        <Dialog open={holidayDialogOpen} onOpenChange={setHolidayDialogOpen}>
          <DialogContent className="sm:max-w-[425px]">
            <DialogHeader>
              <DialogTitle>
                {editingHoliday ? 'Edit Holiday' : 'Add Holiday'}
              </DialogTitle>
              <DialogDescription>
                Add a date when the clinic will be closed or have modified hours.
              </DialogDescription>
            </DialogHeader>
            
            <div className="space-y-4 py-4">
              <div className="space-y-2">
                <Label>Date</Label>
                <Popover>
                  <PopoverTrigger asChild>
                    <Button
                      variant="outline"
                      className={cn(
                        "w-full justify-start text-left font-normal",
                        !holidayForm.date && "text-muted-foreground"
                      )}
                    >
                      <CalendarDays className="mr-2 h-4 w-4" />
                      {holidayForm.date ? format(holidayForm.date, "PPP") : "Pick a date"}
                    </Button>
                  </PopoverTrigger>
                  <PopoverContent className="w-auto p-0" align="start">
                    <Calendar
                      mode="single"
                      selected={holidayForm.date}
                      onSelect={(date) => setHolidayForm({ ...holidayForm, date })}
                      initialFocus
                    />
                  </PopoverContent>
                </Popover>
              </div>

              <div className="space-y-2">
                <Label htmlFor="holiday-name">Holiday Name</Label>
                <Input
                  id="holiday-name"
                  placeholder="e.g., Christmas Day, Staff Training"
                  value={holidayForm.name}
                  onChange={(e) => setHolidayForm({ ...holidayForm, name: e.target.value })}
                />
              </div>

              <div className="flex items-center space-x-2">
                <Switch
                  id="full-day"
                  checked={holidayForm.is_full_day}
                  onCheckedChange={(checked) => 
                    setHolidayForm({ ...holidayForm, is_full_day: checked })
                  }
                />
                <Label htmlFor="full-day">Full day closure</Label>
              </div>

              {!holidayForm.is_full_day && (
                <div className="space-y-2 p-3 bg-muted/50 rounded-lg">
                  <Label className="text-sm text-muted-foreground">Modified Hours</Label>
                  <div className="flex items-center gap-4">
                    <div className="flex items-center gap-2">
                      <Label className="text-sm">From:</Label>
                      <Input
                        type="time"
                        value={holidayForm.start_time}
                        onChange={(e) => 
                          setHolidayForm({ ...holidayForm, start_time: e.target.value })
                        }
                        className="w-28"
                      />
                    </div>
                    <div className="flex items-center gap-2">
                      <Label className="text-sm">To:</Label>
                      <Input
                        type="time"
                        value={holidayForm.end_time}
                        onChange={(e) => 
                          setHolidayForm({ ...holidayForm, end_time: e.target.value })
                        }
                        className="w-28"
                      />
                    </div>
                  </div>
                </div>
              )}
            </div>

            <DialogFooter>
              <Button variant="outline" onClick={() => setHolidayDialogOpen(false)}>
                Cancel
              </Button>
              <Button onClick={saveHoliday}>
                {editingHoliday ? 'Update' : 'Add'} Holiday
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>
    </DashboardLayout>
  );
};

export default Clinic;
