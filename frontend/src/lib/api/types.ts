/**
 * TypeScript types matching the backend API
 */

// Patient types
export interface Patient {
  id: number;
  name: string;
  email: string;
  phone: string;
  insurance_provider: string | null;
  created_at: string;
  updated_at: string;
}

export interface PatientCreate {
  name: string;
  email: string;
  phone: string;
  insurance_provider?: string;
}

export interface PatientUpdate {
  name?: string;
  email?: string;
  phone?: string;
  insurance_provider?: string;
}

export interface PatientListResponse {
  total: number;
  page: number;
  page_size: number;
  patients: Patient[];
}

// Appointment types
export type AppointmentStatus = 'CONFIRMED' | 'CANCELLED' | 'RESCHEDULED' | 'COMPLETED';

export interface Appointment {
  id: number;
  patient_id: number;
  patient_name: string;
  patient_email: string;
  patient_phone: string;
  start_time: string; // ISO8601 datetime
  end_time: string; // ISO8601 datetime
  reason: string;
  status: AppointmentStatus;
  cancellation_reason: string | null;
  created_at: string;
  updated_at: string;
}

export interface AppointmentCreate {
  patient_id: number;
  start_time: string;
  end_time: string;
  reason: string;
}

export interface AppointmentUpdate {
  start_time?: string;
  end_time?: string;
  reason?: string;
  status?: AppointmentStatus;
  cancellation_reason?: string;
}

export interface AppointmentListResponse {
  total: number;
  page: number;
  page_size: number;
  appointments: Appointment[];
}

export interface AvailabilitySlot {
  start: string;
  end: string;
}

export interface AvailabilityRequest {
  start_date: string;
  end_date: string;
}

export interface AvailabilityResponse {
  slots: AvailabilitySlot[];
}

// Clinic Hours types
export interface ClinicHours {
  id: number;
  day_of_week: number; // 0=Monday, 6=Sunday
  start_time: string; // HH:MM:SS
  end_time: string; // HH:MM:SS
  is_active: boolean;
  created_at: string;
}

export interface ClinicHoursUpdate {
  start_time?: string;
  end_time?: string;
  is_active?: boolean;
}

// Dashboard types
export interface DashboardStats {
  total_appointments_today: number;
  total_appointments_upcoming: number;
  total_patients: number;
  confirmed_appointments: number;
  cancelled_appointments: number;
  completed_appointments: number;
}

export interface TodayAppointment {
  id: number;
  patient_name: string;
  patient_phone: string;
  start_time: string;
  end_time: string;
  reason: string;
  status: string;
}

export interface UpcomingAppointment {
  id: number;
  patient_name: string;
  patient_email: string;
  patient_phone: string;
  start_time: string;
  end_time: string;
  reason: string;
  status: string;
}

// API Error type
export interface ApiError {
  detail: string;
}

// Staff types
export interface Staff {
  id: number;
  name: string;
  email: string;
  role: string;
  permissions: Record<string, boolean>;
  is_active: boolean;
  created_by: number | null;
  created_at: string;
  updated_at: string;
}

export interface StaffCreate {
  name: string;
  email: string;
  password: string;
  role?: string;
  permissions?: Record<string, boolean>;
}

export interface StaffUpdate {
  name?: string;
  email?: string;
  password?: string;
  role?: string;
  permissions?: Record<string, boolean>;
  is_active?: boolean;
}

export interface StaffListResponse {
  total: number;
  page: number;
  page_size: number;
  staff: Staff[];
}

export interface StaffLogin {
  email: string;
  password: string;
}

export interface StaffLoginResponse {
  access_token: string;
  token_type: string;
  user: Staff;
}
