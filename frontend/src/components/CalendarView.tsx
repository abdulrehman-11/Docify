import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ChevronLeft, ChevronRight, Calendar as CalendarIcon } from 'lucide-react';
import { appointmentApi } from '@/lib/api';
import type { Appointment } from '@/lib/api/types';
import { format, startOfMonth, endOfMonth, eachDayOfInterval, isSameMonth, isSameDay, addMonths, subMonths, startOfWeek, endOfWeek, parseISO } from 'date-fns';
import { toast } from 'sonner';
import { cn } from '@/lib/utils';
import { parseUTCDate } from '@/lib/dateUtils';

interface CalendarViewProps {
  onDateClick?: (date: Date) => void;
  onAppointmentClick?: (appointment: Appointment) => void;
}

export const CalendarView = ({ onDateClick, onAppointmentClick }: CalendarViewProps) => {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [loading, setLoading] = useState(false);
  const [view, setView] = useState<'month' | 'week'>('month');

  useEffect(() => {
    loadAppointments();
  }, [currentDate]);

  const loadAppointments = async () => {
    try {
      setLoading(true);
      const response = await appointmentApi.getAll();
      setAppointments(response.appointments);
    } catch (error: any) {
      toast.error('Failed to load appointments');
    } finally {
      setLoading(false);
    }
  };

  const monthStart = startOfMonth(currentDate);
  const monthEnd = endOfMonth(currentDate);
  const calendarStart = startOfWeek(monthStart);
  const calendarEnd = endOfWeek(monthEnd);

  const calendarDays = eachDayOfInterval({
    start: view === 'month' ? calendarStart : startOfWeek(currentDate),
    end: view === 'month' ? calendarEnd : endOfWeek(currentDate),
  });

  const getAppointmentsForDay = (date: Date) => {
    return appointments.filter(apt => {
      const aptDate = parseUTCDate(apt.start_time);
      return isSameDay(aptDate, date);
    });
  };

  const handlePrevious = () => {
    if (view === 'month') {
      setCurrentDate(subMonths(currentDate, 1));
    } else {
      setCurrentDate(new Date(currentDate.setDate(currentDate.getDate() - 7)));
    }
  };

  const handleNext = () => {
    if (view === 'month') {
      setCurrentDate(addMonths(currentDate, 1));
    } else {
      setCurrentDate(new Date(currentDate.setDate(currentDate.getDate() + 7)));
    }
  };

  const handleToday = () => {
    setCurrentDate(new Date());
  };

  const getStatusColor = (status: string) => {
    const colors = {
      CONFIRMED: 'bg-blue-500/20 border-blue-500/50 text-blue-700',
      COMPLETED: 'bg-green-500/20 border-green-500/50 text-green-700',
      CANCELLED: 'bg-red-500/20 border-red-500/50 text-red-700',
      RESCHEDULED: 'bg-yellow-500/20 border-yellow-500/50 text-yellow-700',
    };
    return colors[status as keyof typeof colors] || 'bg-gray-500/20 border-gray-500/50 text-gray-700';
  };

  return (
    <Card className="glass-card">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <CalendarIcon className="w-5 h-5" />
            Calendar
          </CardTitle>
          <div className="flex items-center gap-2">
            <div className="flex glass rounded-lg p-1">
              <Button
                variant={view === 'month' ? 'default' : 'ghost'}
                size="sm"
                onClick={() => setView('month')}
                className="text-xs"
              >
                Month
              </Button>
              <Button
                variant={view === 'week' ? 'default' : 'ghost'}
                size="sm"
                onClick={() => setView('week')}
                className="text-xs"
              >
                Week
              </Button>
            </div>
            <Button variant="outline" size="sm" onClick={handleToday}>
              Today
            </Button>
            <div className="flex glass rounded-lg">
              <Button variant="ghost" size="sm" onClick={handlePrevious}>
                <ChevronLeft className="w-4 h-4" />
              </Button>
              <Button variant="ghost" size="sm" onClick={handleNext}>
                <ChevronRight className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </div>
        <p className="text-lg font-semibold mt-2">
          {format(currentDate, 'MMMM yyyy')}
        </p>
      </CardHeader>
      <CardContent>
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <p className="text-muted-foreground">Loading calendar...</p>
          </div>
        ) : (
          <div className="space-y-2">
            {/* Day headers */}
            <div className="grid grid-cols-7 gap-2 mb-2">
              {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(day => (
                <div key={day} className="text-center text-sm font-medium text-muted-foreground p-2">
                  {day}
                </div>
              ))}
            </div>

            {/* Calendar grid */}
            <div className="grid grid-cols-7 gap-2">
              {calendarDays.map((day, index) => {
                const dayAppointments = getAppointmentsForDay(day);
                const isCurrentMonth = isSameMonth(day, currentDate);
                const isToday = isSameDay(day, new Date());
                
                return (
                  <div
                    key={index}
                    onClick={() => onDateClick?.(day)}
                    className={cn(
                      'min-h-[100px] p-2 rounded-lg border cursor-pointer transition-all hover:shadow-md',
                      isCurrentMonth ? 'glass border-white/10' : 'bg-muted/5 border-transparent opacity-40',
                      isToday && 'ring-2 ring-primary',
                      'hover:scale-[1.02]'
                    )}
                  >
                    <div className={cn(
                      'text-sm font-medium mb-1',
                      isToday && 'text-primary font-bold'
                    )}>
                      {format(day, 'd')}
                    </div>
                    <div className="space-y-1">
                      {dayAppointments.slice(0, 3).map(apt => (
                        <div
                          key={apt.id}
                          onClick={(e) => {
                            e.stopPropagation();
                            onAppointmentClick?.(apt);
                          }}
                          className={cn(
                            'text-xs p-1 rounded border truncate hover:scale-105 transition-transform',
                            getStatusColor(apt.status)
                          )}
                        >
                          <div className="font-medium truncate">
                            {format(parseUTCDate(apt.start_time), 'h:mm a')}
                          </div>
                          <div className="truncate opacity-80">
                            {apt.patient_name}
                          </div>
                        </div>
                      ))}
                      {dayAppointments.length > 3 && (
                        <div className="text-xs text-center text-muted-foreground font-medium">
                          +{dayAppointments.length - 3} more
                        </div>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Legend */}
            <div className="flex flex-wrap gap-4 mt-4 pt-4 border-t border-white/10">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded bg-blue-500/20 border border-blue-500/50"></div>
                <span className="text-xs text-muted-foreground">Confirmed</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded bg-green-500/20 border border-green-500/50"></div>
                <span className="text-xs text-muted-foreground">Completed</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded bg-red-500/20 border border-red-500/50"></div>
                <span className="text-xs text-muted-foreground">Cancelled</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded bg-yellow-500/20 border border-yellow-500/50"></div>
                <span className="text-xs text-muted-foreground">Rescheduled</span>
              </div>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};
