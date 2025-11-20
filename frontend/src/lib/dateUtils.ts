/**
 * Date utility functions for handling UTC timestamps from backend
 */

/**
 * Parse a datetime string from the backend and return a Date object
 * 
 * The backend sends ISO8601 strings in UTC "wall clock time" (e.g., "2025-11-20T14:00:00+00:00")
 * We parse this and display it as the same wall clock time locally.
 * 
 * @param dateString - ISO8601 datetime string from backend (e.g., "2025-11-20T14:00:00+00:00")
 * @returns Date object representing the same wall clock time
 */
export function parseUTCDate(dateString: string): Date {
  if (!dateString) {
    throw new Error('Invalid date string');
  }
  
  console.log('🔍 Parsing date from backend:', dateString);
  
  // Extract date/time components without timezone conversion
  const isoStr = dateString.replace(/[Z+].*$/, ''); // Remove Z or +00:00
  
  // Parse as local time (which preserves the wall clock time)
  const date = new Date(isoStr);
  
  // Check if parsing was successful
  if (isNaN(date.getTime())) {
    console.error('❌ Failed to parse date:', dateString);
    throw new Error(`Invalid date format: ${dateString}`);
  }
  
  console.log('   ✅ Parsed as wall clock time:', date.toLocaleString());
  console.log('   📍 Display time:', date.toString());
  
  return date;
}

/**
 * Format a datetime string from backend for display
 * @param dateString - ISO8601 datetime string from backend
 * @param formatStr - Format string (default: 'MMM dd, yyyy - hh:mm a')
 * @returns Formatted date string in local timezone
 */
export function formatBackendDate(dateString: string, formatStr: string = 'MMM dd, yyyy - hh:mm a'): string {
  try {
    const date = parseUTCDate(dateString);
    // Use Intl.DateTimeFormat for reliable local timezone conversion
    if (formatStr === 'MMM dd, yyyy - hh:mm a') {
      const dateOptions: Intl.DateTimeFormatOptions = {
        month: 'short',
        day: '2-digit',
        year: 'numeric',
      };
      const timeOptions: Intl.DateTimeFormatOptions = {
        hour: '2-digit',
        minute: '2-digit',
        hour12: true,
      };
      const datePart = date.toLocaleDateString('en-US', dateOptions);
      const timePart = date.toLocaleTimeString('en-US', timeOptions);
      return `${datePart} - ${timePart}`;
    }
    return date.toLocaleString();
  } catch (error) {
    console.error('Error formatting date:', dateString, error);
    return 'Invalid date';
  }
}

/**
 * Convert local datetime-local input value to naive ISO string for backend
 * 
 * IMPORTANT: Appointments are stored in "wall clock time" (UTC without timezone conversion).
 * If a user selects 2:00 PM in the datetime-local input, we want to store it as 2:00 PM UTC,
 * NOT convert it to UTC based on the user's timezone.
 * 
 * For example:
 * - User in PKT (UTC+5) selects "2025-11-20T14:00" (2:00 PM local)
 * - We send "2025-11-20T14:00:00" to backend (treated as 2:00 PM UTC)
 * - NOT "2025-11-20T09:00:00+00:00" (which would be 9:00 AM UTC)
 * 
 * @param localDateTimeString - Value from datetime-local input (e.g., "2025-11-14T14:00")
 * @returns Naive ISO8601 string (e.g., "2025-11-14T14:00:00")
 */
export function localDateTimeToUTC(localDateTimeString: string): string {
  console.log('🔄 Converting datetime-local to naive ISO:', localDateTimeString);
  
  // datetime-local format is "YYYY-MM-DDTHH:MM"
  // We want to keep the same wall clock time, just add seconds if missing
  let isoString = localDateTimeString;
  
  // Add :00 for seconds if not present
  if (isoString.length === 16) {
    isoString += ':00';
  }
  
  console.log('   📍 Input from datetime-local:', localDateTimeString);
  console.log('   🌍 Output (naive ISO):', isoString);
  console.log('   ⚠️  Note: No timezone conversion - wall clock time preserved');
  
  return isoString;
}

/**
 * Convert UTC ISO string from backend to local datetime-local format for input
 * 
 * Since appointments are stored in wall clock time (as naive UTC), we extract
 * the date/time components directly without timezone conversion.
 * 
 * @param utcDateString - ISO8601 datetime string from backend (e.g., "2025-11-20T14:00:00+00:00")
 * @returns Local datetime string for datetime-local input (YYYY-MM-DDTHH:MM)
 */
export function utcToLocalDateTime(utcDateString: string): string {
  // Parse the ISO string and extract components
  // Remove timezone info and just use the date/time values
  const isoStr = utcDateString.replace(/[Z+].*$/, ''); // Remove Z or +00:00
  const match = isoStr.match(/^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2})/);
  
  if (!match) {
    throw new Error(`Invalid datetime format: ${utcDateString}`);
  }
  
  const [, year, month, day, hours, minutes] = match;
  const result = `${year}-${month}-${day}T${hours}:${minutes}`;
  
  console.log('🔄 Converting backend datetime to datetime-local:', utcDateString, '=>', result);
  
  return result;
}
