/**
 * Clinic Hours Modal for Landing Page
 * Displays clinic operating hours in a beautiful modal
 */
import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Clock, Calendar, Coffee, CheckCircle, AlertCircle } from 'lucide-react';
import { clinicApi } from '@/lib/api';
import { cn } from '@/lib/utils';

interface ClinicHoursModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

const daysOfWeek = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
const CACHE_KEY = 'clinic_hours_cache';
const CACHE_TIMESTAMP_KEY = 'clinic_hours_cache_timestamp';
const CACHE_DURATION = 1000 * 60 * 60 * 24; // 24 hours

export const ClinicHoursModal: React.FC<ClinicHoursModalProps> = ({ open, onOpenChange }) => {
  const [clinicHours, setClinicHours] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [usingCache, setUsingCache] = useState(false);

  useEffect(() => {
    if (open) {
      loadClinicHours();
    }
  }, [open]);

  const loadFromCache = (): any[] | null => {
    try {
      const cached = localStorage.getItem(CACHE_KEY);
      const timestamp = localStorage.getItem(CACHE_TIMESTAMP_KEY);
      
      if (cached && timestamp) {
        const age = Date.now() - parseInt(timestamp);
        if (age < CACHE_DURATION) {
          return JSON.parse(cached);
        }
      }
    } catch (error) {
      console.error('[ClinicHours] Failed to load from cache:', error);
    }
    return null;
  };

  const saveToCache = (hours: any[]) => {
    try {
      localStorage.setItem(CACHE_KEY, JSON.stringify(hours));
      localStorage.setItem(CACHE_TIMESTAMP_KEY, Date.now().toString());
    } catch (error) {
      console.error('[ClinicHours] Failed to save to cache:', error);
    }
  };

  const loadClinicHours = async () => {
    try {
      setLoading(true);
      setUsingCache(false);
      
      const hours = await clinicApi.getHours();
      setClinicHours(hours);
      saveToCache(hours);
    } catch (error) {
      console.error('Failed to load clinic hours from API:', error);
      
      // Fallback to cache if API fails
      const cachedHours = loadFromCache();
      if (cachedHours && cachedHours.length > 0) {
        console.log('[ClinicHours] Using cached data as fallback');
        setClinicHours(cachedHours);
        setUsingCache(true);
      } else {
        setClinicHours([]);
      }
    } finally {
      setLoading(false);
    }
  };

  const formatTime = (time: string) => {
    if (!time) return '';
    const [hours, minutes] = time.split(':');
    const hour = parseInt(hours);
    const ampm = hour >= 12 ? 'PM' : 'AM';
    const displayHour = hour % 12 || 12;
    return `${displayHour}:${minutes} ${ampm}`;
  };

  const getHoursForDay = (dayIndex: number) => {
    return clinicHours.find((h) => h.day_of_week === dayIndex);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="glass-card max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <div className="flex items-center gap-3 mb-2">
            <div className="p-3 rounded-xl bg-primary/10 border border-primary/20">
              <Clock className="w-6 h-6 text-primary" />
            </div>
            <div>
              <DialogTitle className="text-2xl">Clinic Hours</DialogTitle>
              <DialogDescription>Our operating hours for the week</DialogDescription>
            </div>
          </div>
          
          {usingCache && (
            <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-yellow-500/10 border border-yellow-500/20 text-yellow-700 dark:text-yellow-400 text-sm mt-3">
              <AlertCircle className="w-4 h-4" />
              <span>Showing cached data (unable to connect to server)</span>
            </div>
          )}
        </DialogHeader>

        {loading ? (
          <div className="flex items-center justify-center py-12">
            <div className="text-center">
              <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-primary mx-auto mb-3"></div>
              <p className="text-muted-foreground">Loading hours...</p>
            </div>
          </div>
        ) : clinicHours.length === 0 ? (
          <div className="flex items-center justify-center py-12">
            <div className="text-center">
              <AlertCircle className="w-12 h-12 text-muted-foreground mx-auto mb-3" />
              <p className="text-muted-foreground">Unable to load clinic hours</p>
              <p className="text-sm text-muted-foreground mt-1">Please try again later</p>
            </div>
          </div>
        ) : (
          <div className="space-y-3 mt-4">
            {daysOfWeek.map((day, index) => {
              const hours = getHoursForDay(index);
              const isOpen = hours?.is_active;
              const hasBreak = hours?.break_start && hours?.break_end;

              return (
                <div
                  key={day}
                  className={cn(
                    'p-4 rounded-xl border-2 transition-all',
                    isOpen
                      ? 'bg-gradient-to-br from-primary/5 to-accent/5 border-primary/20 hover:border-primary/30'
                      : 'bg-muted/30 border-border/50 opacity-60'
                  )}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div
                        className={cn(
                          'w-2 h-2 rounded-full',
                          isOpen ? 'bg-green-500' : 'bg-red-500'
                        )}
                      />
                      <span className="font-semibold text-foreground">{day}</span>
                    </div>

                    <div className="text-right">
                      {isOpen ? (
                        <div className="space-y-1">
                          <div className="flex items-center gap-2 text-sm font-medium">
                            <Clock className="w-4 h-4 text-primary" />
                            <span>
                              {formatTime(hours.open_time)} - {formatTime(hours.close_time)}
                            </span>
                          </div>
                          {hasBreak && (
                            <div className="flex items-center gap-2 text-xs text-muted-foreground">
                              <Coffee className="w-3.5 h-3.5" />
                              <span>
                                Break: {formatTime(hours.break_start)} - {formatTime(hours.break_end)}
                              </span>
                            </div>
                          )}
                        </div>
                      ) : (
                        <span className="text-sm text-muted-foreground font-medium">Closed</span>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}

        <div className="mt-6 p-4 rounded-xl bg-muted/50 border border-border/50">
          <div className="flex items-start gap-3">
            <Calendar className="w-5 h-5 text-primary mt-0.5" />
            <div className="flex-1">
              <h4 className="font-semibold text-sm mb-1">Need to Book an Appointment?</h4>
              <p className="text-sm text-muted-foreground">
                Call us at{' '}
                <a href="tel:+92444555777" className="text-primary hover:underline font-medium">
                  +92-444-555-777
                </a>{' '}
                or visit our clinic during operating hours.
              </p>
            </div>
          </div>
        </div>

        <div className="mt-4 flex items-center gap-2 text-xs text-muted-foreground">
          <CheckCircle className="w-4 h-4 text-green-500" />
          <span>Hours updated regularly • Last updated: Today</span>
        </div>
      </DialogContent>
    </Dialog>
  );
};
