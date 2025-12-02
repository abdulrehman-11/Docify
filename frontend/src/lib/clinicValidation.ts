/**
 * Clinic Validation Service
 * 
 * This service validates appointment times against clinic hours and holidays
 * from the database. It ensures appointments can only be booked during valid times.
 */

import { clinicApi } from '@/lib/api';
import type { ClinicHours, ClinicHoliday } from '@/lib/api/types';

// Cache for clinic data to avoid repeated API calls
let clinicHoursCache: ClinicHours[] | null = null;
let holidaysCache: ClinicHoliday[] | null = null;
let cacheExpiry: number = 0;
const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes

export interface ValidationResult {
  isValid: boolean;
  error?: string;
  details?: {
    isHoliday?: boolean;
    holidayName?: string;
    isClosedDay?: boolean;
    dayName?: string;
    outsideHours?: boolean;
    openTime?: string;
    closeTime?: string;
    isBreakTime?: boolean;
    breakStart?: string;
    breakEnd?: string;
  };
}

export interface ClinicSchedule {
  hours: ClinicHours[];
  holidays: ClinicHoliday[];
}

/**
 * Get clinic hours and holidays, with caching
 */
export async function getClinicSchedule(forceRefresh = false): Promise<ClinicSchedule> {
  const now = Date.now();
  
  if (!forceRefresh && clinicHoursCache && holidaysCache && now < cacheExpiry) {
    return { hours: clinicHoursCache, holidays: holidaysCache };
  }
  
  try {
    const [hours, holidays] = await Promise.all([
      clinicApi.getHours(),
      clinicApi.getHolidays()
    ]);
    
    clinicHoursCache = hours;
    holidaysCache = holidays;
    cacheExpiry = now + CACHE_DURATION;
    
    return { hours, holidays };
  } catch (error) {
    console.error('Failed to fetch clinic schedule:', error);
    // Return cached data if available, even if expired
    if (clinicHoursCache && holidaysCache) {
      return { hours: clinicHoursCache, holidays: holidaysCache };
    }
    throw error;
  }
}

/**
 * Clear the cache (useful when clinic hours/holidays are updated)
 */
export function clearClinicScheduleCache(): void {
  clinicHoursCache = null;
  holidaysCache = null;
  cacheExpiry = 0;
}

/**
 * Get day name from day of week number
 */
function getDayName(dayOfWeek: number): string {
  const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
  return days[dayOfWeek] || 'Unknown';
}

/**
 * Convert JavaScript Date day (0=Sunday) to our backend format (0=Monday)
 */
function getBackendDayOfWeek(date: Date): number {
  const jsDay = date.getDay(); // 0=Sunday, 1=Monday, etc.
  // Convert to 0=Monday, 1=Tuesday, ..., 6=Sunday
  return jsDay === 0 ? 6 : jsDay - 1;
}

/**
 * Parse time string (HH:MM or HH:MM:SS) to minutes from midnight
 */
function parseTimeToMinutes(timeStr: string): number {
  const parts = timeStr.split(':');
  const hours = parseInt(parts[0], 10);
  const minutes = parseInt(parts[1], 10);
  return hours * 60 + minutes;
}

/**
 * Format minutes to time string HH:MM AM/PM
 */
function formatMinutesToTime(minutes: number): string {
  const hours = Math.floor(minutes / 60);
  const mins = minutes % 60;
  const period = hours >= 12 ? 'PM' : 'AM';
  const displayHours = hours % 12 || 12;
  return `${displayHours}:${mins.toString().padStart(2, '0')} ${period}`;
}

/**
 * Check if a date is a holiday
 */
function checkHoliday(date: Date, holidays: ClinicHoliday[]): { isHoliday: boolean; holiday?: ClinicHoliday } {
  const dateStr = formatDateToYYYYMMDD(date);
  const holiday = holidays.find(h => h.date === dateStr);
  return { isHoliday: !!holiday && holiday.is_full_day, holiday };
}

/**
 * Format date to YYYY-MM-DD string
 */
function formatDateToYYYYMMDD(date: Date): string {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

/**
 * Validate if a given datetime is within clinic operating hours
 */
export async function validateAppointmentTime(
  appointmentDate: Date,
  durationMinutes: number = 30
): Promise<ValidationResult> {
  try {
    const { hours, holidays } = await getClinicSchedule();
    
    // Check for holiday
    const { isHoliday, holiday } = checkHoliday(appointmentDate, holidays);
    if (isHoliday && holiday) {
      return {
        isValid: false,
        error: `Clinic is closed on ${holiday.name}`,
        details: {
          isHoliday: true,
          holidayName: holiday.name
        }
      };
    }
    
    // Get clinic hours for this day of week
    const dayOfWeek = getBackendDayOfWeek(appointmentDate);
    const dayHours = hours.find(h => h.day_of_week === dayOfWeek);
    
    // Check if clinic is open on this day
    if (!dayHours || !dayHours.is_active) {
      return {
        isValid: false,
        error: `Clinic is closed on ${getDayName(dayOfWeek)}s`,
        details: {
          isClosedDay: true,
          dayName: getDayName(dayOfWeek)
        }
      };
    }
    
    // If it's a holiday with modified hours, use those instead
    let openTime = dayHours.start_time;
    let closeTime = dayHours.end_time;
    
    if (holiday && !holiday.is_full_day && holiday.start_time && holiday.end_time) {
      openTime = holiday.start_time;
      closeTime = holiday.end_time;
    }
    
    // Get appointment time in minutes from midnight
    const appointmentMinutes = appointmentDate.getHours() * 60 + appointmentDate.getMinutes();
    const appointmentEndMinutes = appointmentMinutes + durationMinutes;
    
    // Parse clinic hours
    const openMinutes = parseTimeToMinutes(openTime);
    const closeMinutes = parseTimeToMinutes(closeTime);
    
    // Check if appointment is within operating hours
    if (appointmentMinutes < openMinutes) {
      return {
        isValid: false,
        error: `Appointment time is before clinic opens at ${formatMinutesToTime(openMinutes)}`,
        details: {
          outsideHours: true,
          openTime: formatMinutesToTime(openMinutes),
          closeTime: formatMinutesToTime(closeMinutes)
        }
      };
    }
    
    if (appointmentEndMinutes > closeMinutes) {
      return {
        isValid: false,
        error: `Appointment would end after clinic closes at ${formatMinutesToTime(closeMinutes)}`,
        details: {
          outsideHours: true,
          openTime: formatMinutesToTime(openMinutes),
          closeTime: formatMinutesToTime(closeMinutes)
        }
      };
    }
    
    // Check break time (if exists)
    if (dayHours.break_start && dayHours.break_end) {
      const breakStartMinutes = parseTimeToMinutes(dayHours.break_start);
      const breakEndMinutes = parseTimeToMinutes(dayHours.break_end);
      
      // Check if appointment overlaps with break time
      const appointmentOverlapsBreak = 
        (appointmentMinutes < breakEndMinutes && appointmentEndMinutes > breakStartMinutes);
      
      if (appointmentOverlapsBreak) {
        return {
          isValid: false,
          error: `Appointment overlaps with break time (${formatMinutesToTime(breakStartMinutes)} - ${formatMinutesToTime(breakEndMinutes)})`,
          details: {
            isBreakTime: true,
            breakStart: formatMinutesToTime(breakStartMinutes),
            breakEnd: formatMinutesToTime(breakEndMinutes)
          }
        };
      }
    }
    
    return { isValid: true };
  } catch (error) {
    console.error('Validation error:', error);
    // In case of error, allow booking but log it
    return { isValid: true };
  }
}

/**
 * Get available time slots for a given date
 */
export async function getAvailableTimeSlots(
  date: Date,
  slotDurationMinutes: number = 30
): Promise<{ start: string; end: string }[]> {
  const { hours, holidays } = await getClinicSchedule();
  
  // Check for holiday
  const { isHoliday, holiday } = checkHoliday(date, holidays);
  if (isHoliday) {
    return []; // No slots on full day holidays
  }
  
  // Get clinic hours for this day
  const dayOfWeek = getBackendDayOfWeek(date);
  const dayHours = hours.find(h => h.day_of_week === dayOfWeek);
  
  if (!dayHours || !dayHours.is_active) {
    return []; // Clinic closed this day
  }
  
  // Determine operating hours (use holiday modified hours if applicable)
  let openTime = dayHours.start_time;
  let closeTime = dayHours.end_time;
  
  if (holiday && !holiday.is_full_day && holiday.start_time && holiday.end_time) {
    openTime = holiday.start_time;
    closeTime = holiday.end_time;
  }
  
  const openMinutes = parseTimeToMinutes(openTime);
  const closeMinutes = parseTimeToMinutes(closeTime);
  
  // Get break time if exists
  let breakStartMinutes: number | null = null;
  let breakEndMinutes: number | null = null;
  
  if (dayHours.break_start && dayHours.break_end) {
    breakStartMinutes = parseTimeToMinutes(dayHours.break_start);
    breakEndMinutes = parseTimeToMinutes(dayHours.break_end);
  }
  
  // Generate slots
  const slots: { start: string; end: string }[] = [];
  
  for (let minutes = openMinutes; minutes + slotDurationMinutes <= closeMinutes; minutes += slotDurationMinutes) {
    const slotEndMinutes = minutes + slotDurationMinutes;
    
    // Skip slots that overlap with break time
    if (breakStartMinutes !== null && breakEndMinutes !== null) {
      if (minutes < breakEndMinutes && slotEndMinutes > breakStartMinutes) {
        continue;
      }
    }
    
    const startHours = Math.floor(minutes / 60);
    const startMins = minutes % 60;
    const endHours = Math.floor(slotEndMinutes / 60);
    const endMins = slotEndMinutes % 60;
    
    slots.push({
      start: `${startHours.toString().padStart(2, '0')}:${startMins.toString().padStart(2, '0')}`,
      end: `${endHours.toString().padStart(2, '0')}:${endMins.toString().padStart(2, '0')}`
    });
  }
  
  return slots;
}

/**
 * Check if a specific date is a closed day (weekend or holiday)
 */
export async function isClosedDay(date: Date): Promise<{ isClosed: boolean; reason?: string }> {
  const { hours, holidays } = await getClinicSchedule();
  
  // Check holiday first
  const { isHoliday, holiday } = checkHoliday(date, holidays);
  if (isHoliday && holiday) {
    return { isClosed: true, reason: `Holiday: ${holiday.name}` };
  }
  
  // Check if clinic is open this day of week
  const dayOfWeek = getBackendDayOfWeek(date);
  const dayHours = hours.find(h => h.day_of_week === dayOfWeek);
  
  if (!dayHours || !dayHours.is_active) {
    return { isClosed: true, reason: `Clinic is closed on ${getDayName(dayOfWeek)}s` };
  }
  
  return { isClosed: false };
}

/**
 * Get clinic hours for display purposes
 */
export async function getClinicHoursForDate(date: Date): Promise<{
  isOpen: boolean;
  openTime?: string;
  closeTime?: string;
  breakStart?: string;
  breakEnd?: string;
  holidayName?: string;
} | null> {
  const { hours, holidays } = await getClinicSchedule();
  
  // Check holiday
  const { isHoliday, holiday } = checkHoliday(date, holidays);
  if (isHoliday && holiday) {
    return { isOpen: false, holidayName: holiday.name };
  }
  
  // Get regular hours
  const dayOfWeek = getBackendDayOfWeek(date);
  const dayHours = hours.find(h => h.day_of_week === dayOfWeek);
  
  if (!dayHours || !dayHours.is_active) {
    return { isOpen: false };
  }
  
  // If holiday with modified hours
  if (holiday && !holiday.is_full_day && holiday.start_time && holiday.end_time) {
    return {
      isOpen: true,
      openTime: holiday.start_time.substring(0, 5),
      closeTime: holiday.end_time.substring(0, 5),
      holidayName: holiday.name
    };
  }
  
  return {
    isOpen: true,
    openTime: dayHours.start_time?.substring(0, 5),
    closeTime: dayHours.end_time?.substring(0, 5),
    breakStart: dayHours.break_start?.substring(0, 5) || undefined,
    breakEnd: dayHours.break_end?.substring(0, 5) || undefined
  };
}
