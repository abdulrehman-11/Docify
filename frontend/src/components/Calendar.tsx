import { useState } from 'react';
import { format, startOfMonth, endOfMonth, eachDayOfInterval, isSameMonth, isSameDay, addMonths, subMonths, isToday } from 'date-fns';
import { ChevronLeft, ChevronRight, Plus, Search, Filter } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Appointment } from '@/lib/mockData';
import { cn } from '@/lib/utils';

interface CalendarProps {
  appointments: Appointment[];
  selectedDate: Date;
  onDateSelect: (date: Date) => void;
  doctorId: string;
}

export const Calendar = ({ appointments, selectedDate, onDateSelect, doctorId }: CalendarProps) => {
  const [currentMonth, setCurrentMonth] = useState(selectedDate);

  const monthStart = startOfMonth(currentMonth);
  const monthEnd = endOfMonth(currentMonth);
  const monthDays = eachDayOfInterval({ start: monthStart, end: monthEnd });

  const getAppointmentsForDay = (day: Date) => {
    return appointments.filter(
      (apt) =>
        apt.doctorId === doctorId &&
        apt.status !== 'cancelled' &&
        isSameDay(new Date(apt.date), day)
    );
  };

  const handlePrevMonth = () => setCurrentMonth(subMonths(currentMonth, 1));
  const handleNextMonth = () => setCurrentMonth(addMonths(currentMonth, 1));

  return (
    <div className="glass-card p-6 rounded-2xl">
      {/* Calendar Header */}
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-bold">
          {format(currentMonth, 'MMMM yyyy')}
        </h2>
        <div className="flex gap-2">
          <Button
            variant="outline"
            size="icon"
            onClick={handlePrevMonth}
            className="hover-lift"
          >
            <ChevronLeft className="w-4 h-4" />
          </Button>
          <Button
            variant="outline"
            size="icon"
            onClick={handleNextMonth}
            className="hover-lift"
          >
            <ChevronRight className="w-4 h-4" />
          </Button>
        </div>
      </div>

      {/* Calendar Grid */}
      <div className="grid grid-cols-7 gap-2">
        {/* Day names */}
        {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map((day) => (
          <div
            key={day}
            className="text-center text-sm font-medium text-muted-foreground py-2"
          >
            {day}
          </div>
        ))}

        {/* Empty cells for days before month starts */}
        {Array.from({ length: monthStart.getDay() }).map((_, i) => (
          <div key={`empty-${i}`} className="aspect-square" />
        ))}

        {/* Calendar days */}
        {monthDays.map((day) => {
          const dayAppointments = getAppointmentsForDay(day);
          const isSelected = isSameDay(day, selectedDate);
          const isCurrentDay = isToday(day);

          return (
            <button
              key={day.toISOString()}
              onClick={() => onDateSelect(day)}
              className={cn(
                'aspect-square p-2 rounded-xl transition-all relative hover:bg-muted',
                isSelected && 'bg-primary text-primary-foreground hover:bg-primary/90',
                !isSameMonth(day, currentMonth) && 'opacity-40',
                isCurrentDay && !isSelected && 'ring-2 ring-primary'
              )}
            >
              <div className="text-sm font-medium">{format(day, 'd')}</div>
              {dayAppointments.length > 0 && (
                <div className="absolute bottom-1 left-1/2 -translate-x-1/2 flex gap-0.5">
                  {dayAppointments.slice(0, 3).map((apt, i) => (
                    <div
                      key={i}
                      className={cn(
                        'w-1 h-1 rounded-full',
                        isSelected ? 'bg-primary-foreground' : 'bg-primary'
                      )}
                    />
                  ))}
                </div>
              )}
            </button>
          );
        })}
      </div>
    </div>
  );
};
