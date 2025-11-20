export interface Doctor {
  id: string;
  name: string;
  specialty: string;
  image: string;
  email: string;
  phone: string;
  schedule: {
    day: string;
    startTime: string;
    endTime: string;
  }[];
  rating: number;
  reviews: number;
  bio: string;
}

export interface Appointment {
  id: string;
  doctorId: string;
  patientName: string;
  patientEmail: string;
  patientPhone: string;
  service: string;
  date: string;
  time: string;
  status: 'scheduled' | 'cancelled' | 'completed';
  notes?: string;
  createdBy: string;
  createdAt: string;
}

export interface Service {
  id: string;
  name: string;
  duration: number;
  description: string;
}

export interface ClinicInfo {
  name: string;
  address: string;
  phone: string;
  email: string;
  hours: {
    day: string;
    open: string;
    close: string;
  }[];
}

export interface AuditLog {
  id: string;
  action: string;
  user: string;
  timestamp: string;
  details: string;
}

export interface KnowledgeBaseItem {
  id: string;
  category: string;
  question: string;
  answer: string;
  lastUpdated: string;
}

export interface NotificationTemplate {
  id: string;
  name: string;
  subject: string;
  body: string;
  type: 'appointment_confirmation' | 'appointment_reminder' | 'appointment_cancellation' | 'custom';
}

export interface StaffMember {
  id: string;
  name: string;
  email: string;
  role: 'staff';
  permissions: string[];
  assignedDoctors: string[];
  createdAt: string;
}

export const mockDoctors: Doctor[] = [
  {
    id: '1',
    name: 'Dr. Sarah Johnson',
    specialty: 'General Physician',
    image: 'https://images.unsplash.com/photo-1559839734-2b71ea197ec2?w=400&h=400&fit=crop',
    email: 'sarah.johnson@clinic.com',
    phone: '+92-300-1234567',
    schedule: [
      { day: 'Monday', startTime: '09:00', endTime: '17:00' },
      { day: 'Tuesday', startTime: '09:00', endTime: '17:00' },
      { day: 'Wednesday', startTime: '09:00', endTime: '17:00' },
      { day: 'Thursday', startTime: '09:00', endTime: '17:00' },
      { day: 'Friday', startTime: '09:00', endTime: '14:00' },
    ],
    rating: 4.8,
    reviews: 156,
    bio: 'Dr. Johnson has over 15 years of experience in general medicine and is dedicated to providing compassionate care.',
  },
  {
    id: '2',
    name: 'Dr. Michael Chen',
    specialty: 'Cardiologist',
    image: 'https://images.unsplash.com/photo-1612349317150-e413f6a5b16d?w=400&h=400&fit=crop',
    email: 'michael.chen@clinic.com',
    phone: '+92-300-2345678',
    schedule: [
      { day: 'Monday', startTime: '10:00', endTime: '18:00' },
      { day: 'Wednesday', startTime: '10:00', endTime: '18:00' },
      { day: 'Friday', startTime: '10:00', endTime: '16:00' },
    ],
    rating: 4.9,
    reviews: 203,
    bio: 'Specialized in cardiovascular health with expertise in preventive cardiology and heart disease management.',
  },
  {
    id: '3',
    name: 'Dr. Emily Rodriguez',
    specialty: 'Pediatrician',
    image: 'https://images.unsplash.com/photo-1594824476967-48c8b964273f?w=400&h=400&fit=crop',
    email: 'emily.rodriguez@clinic.com',
    phone: '+92-300-3456789',
    schedule: [
      { day: 'Tuesday', startTime: '08:00', endTime: '16:00' },
      { day: 'Thursday', startTime: '08:00', endTime: '16:00' },
      { day: 'Saturday', startTime: '09:00', endTime: '13:00' },
    ],
    rating: 4.9,
    reviews: 178,
    bio: 'Passionate about child health and development, providing gentle care for children of all ages.',
  },
];

export const mockServices: Service[] = [
  { id: '1', name: 'General Consultation', duration: 30, description: 'Standard medical consultation' },
  { id: '2', name: 'Follow-up Visit', duration: 15, description: 'Follow-up appointment' },
  { id: '3', name: 'Health Checkup', duration: 45, description: 'Comprehensive health examination' },
  { id: '4', name: 'Vaccination', duration: 20, description: 'Immunization services' },
  { id: '5', name: 'Lab Tests', duration: 30, description: 'Laboratory testing services' },
];

export const mockAppointments: Appointment[] = [
  {
    id: '1',
    doctorId: '1',
    patientName: 'Ahmed Khan',
    patientEmail: 'ahmed@email.com',
    patientPhone: '+92-300-9876543',
    service: 'General Consultation',
    date: '2025-11-12',
    time: '10:00',
    status: 'scheduled',
    notes: 'First visit',
    createdBy: 'admin@clinic.com',
    createdAt: '2025-11-10T14:30:00',
  },
  {
    id: '2',
    doctorId: '1',
    patientName: 'Fatima Ali',
    patientEmail: 'fatima@email.com',
    patientPhone: '+92-300-8765432',
    service: 'Follow-up Visit',
    date: '2025-11-12',
    time: '11:00',
    status: 'scheduled',
    createdBy: 'staff@clinic.com',
    createdAt: '2025-11-10T15:00:00',
  },
  {
    id: '3',
    doctorId: '2',
    patientName: 'Hassan Mahmood',
    patientEmail: 'hassan@email.com',
    patientPhone: '+92-300-7654321',
    service: 'Health Checkup',
    date: '2025-11-11',
    time: '14:00',
    status: 'completed',
    notes: 'Regular checkup',
    createdBy: 'admin@clinic.com',
    createdAt: '2025-11-09T10:00:00',
  },
  {
    id: '4',
    doctorId: '3',
    patientName: 'Ayesha Riaz',
    patientEmail: 'ayesha@email.com',
    patientPhone: '+92-300-6543210',
    service: 'Vaccination',
    date: '2025-11-11',
    time: '09:00',
    status: 'cancelled',
    notes: 'Patient requested cancellation',
    createdBy: 'staff@clinic.com',
    createdAt: '2025-11-08T16:00:00',
  },
  {
    id: '5',
    doctorId: '1',
    patientName: 'Bilal Ahmed',
    patientEmail: 'bilal@email.com',
    patientPhone: '+92-300-5432109',
    service: 'General Consultation',
    date: '2025-11-13',
    time: '15:00',
    status: 'scheduled',
    createdBy: 'admin@clinic.com',
    createdAt: '2025-11-11T08:00:00',
  },
];

export const mockClinicInfo: ClinicInfo = {
  name: 'HealthCare Plus Clinic',
  address: '123 Medical Center, Islamabad, Pakistan',
  phone: '+92-444-555-777',
  email: 'info@healthcareplus.com',
  hours: [
    { day: 'Monday', open: '08:00', close: '18:00' },
    { day: 'Tuesday', open: '08:00', close: '18:00' },
    { day: 'Wednesday', open: '08:00', close: '18:00' },
    { day: 'Thursday', open: '08:00', close: '18:00' },
    { day: 'Friday', open: '08:00', close: '16:00' },
    { day: 'Saturday', open: '09:00', close: '14:00' },
    { day: 'Sunday', open: 'Closed', close: 'Closed' },
  ],
};

export const mockAuditLogs: AuditLog[] = [
  {
    id: '1',
    action: 'Appointment Created',
    user: 'Admin User',
    timestamp: '2025-11-10T14:30:00',
    details: 'Created appointment for Ahmed Khan with Dr. Sarah Johnson',
  },
  {
    id: '2',
    action: 'Appointment Cancelled',
    user: 'Staff Member',
    timestamp: '2025-11-10T15:45:00',
    details: 'Cancelled appointment for Ayesha Riaz',
  },
  {
    id: '3',
    action: 'Provider Added',
    user: 'Admin User',
    timestamp: '2025-11-09T10:00:00',
    details: 'Added new provider: Dr. Michael Chen',
  },
  {
    id: '4',
    action: 'Service Modified',
    user: 'Admin User',
    timestamp: '2025-11-09T11:30:00',
    details: 'Updated duration for Health Checkup service',
  },
  {
    id: '5',
    action: 'Appointment Completed',
    user: 'Staff Member',
    timestamp: '2025-11-11T14:30:00',
    details: 'Marked appointment as completed for Hassan Mahmood',
  },
  {
    id: '6',
    action: 'Clinic Info Updated',
    user: 'Admin User',
    timestamp: '2025-11-08T09:00:00',
    details: 'Updated clinic operating hours',
  },
];

export const mockKnowledgeBase: KnowledgeBaseItem[] = [
  {
    id: '1',
    category: 'Appointments',
    question: 'How do I book an appointment?',
    answer: 'You can book an appointment by calling our AI receptionist at +92-444-555-777. Simply state your preferred doctor, date, and time, and our AI will find the best available slot for you.',
    lastUpdated: '2025-11-01T10:00:00',
  },
  {
    id: '2',
    category: 'Appointments',
    question: 'Can I cancel or reschedule my appointment?',
    answer: 'Yes, you can cancel or reschedule by calling our AI receptionist. Please provide your appointment ID or patient name for verification.',
    lastUpdated: '2025-11-01T10:00:00',
  },
  {
    id: '3',
    category: 'Services',
    question: 'What services do you offer?',
    answer: 'We offer General Consultation, Follow-up Visits, Health Checkups, Vaccination, and Laboratory Testing services. Each service duration varies from 15 to 45 minutes.',
    lastUpdated: '2025-11-01T10:00:00',
  },
  {
    id: '4',
    category: 'Clinic Hours',
    question: 'What are your clinic hours?',
    answer: 'We are open Monday to Friday from 8:00 AM to 6:00 PM, Saturday from 9:00 AM to 2:00 PM. We are closed on Sundays.',
    lastUpdated: '2025-11-01T10:00:00',
  },
  {
    id: '5',
    category: 'General',
    question: 'Do you accept insurance?',
    answer: 'Yes, we accept most major insurance providers. Please have your insurance card ready when booking your appointment.',
    lastUpdated: '2025-11-01T10:00:00',
  },
];

export const mockNotificationTemplates: NotificationTemplate[] = [
  {
    id: '1',
    name: 'Appointment Confirmation',
    subject: 'Appointment Confirmed - {CLINIC_NAME}',
    body: 'Dear {PATIENT_NAME},\n\nYour appointment has been confirmed.\n\nDoctor: {DOCTOR_NAME}\nDate: {DATE}\nTime: {TIME}\nService: {SERVICE}\n\nLocation: {CLINIC_ADDRESS}\n\nIf you need to reschedule, please call us at {CLINIC_PHONE}.\n\nThank you,\n{CLINIC_NAME}',
    type: 'appointment_confirmation',
  },
  {
    id: '2',
    name: 'Appointment Reminder',
    subject: 'Appointment Reminder - Tomorrow at {TIME}',
    body: 'Dear {PATIENT_NAME},\n\nThis is a reminder of your appointment tomorrow.\n\nDoctor: {DOCTOR_NAME}\nDate: {DATE}\nTime: {TIME}\nService: {SERVICE}\n\nPlease arrive 10 minutes early.\n\nSee you soon!\n{CLINIC_NAME}',
    type: 'appointment_reminder',
  },
  {
    id: '3',
    name: 'Appointment Cancellation',
    subject: 'Appointment Cancelled - {CLINIC_NAME}',
    body: 'Dear {PATIENT_NAME},\n\nYour appointment has been cancelled as requested.\n\nCancelled appointment details:\nDoctor: {DOCTOR_NAME}\nDate: {DATE}\nTime: {TIME}\n\nTo book a new appointment, please call us at {CLINIC_PHONE}.\n\nThank you,\n{CLINIC_NAME}',
    type: 'appointment_cancellation',
  },
];

export const mockStaffMembers: StaffMember[] = [
  {
    id: '1',
    name: 'Staff Member',
    email: 'staff@clinic.com',
    role: 'staff',
    permissions: ['view_appointments', 'add_appointments', 'edit_appointments', 'cancel_appointments'],
    assignedDoctors: ['1', '3'],
    createdAt: '2025-10-01T10:00:00',
  },
  {
    id: '2',
    name: 'John Smith',
    email: 'john.smith@clinic.com',
    role: 'staff',
    permissions: ['view_appointments', 'add_appointments'],
    assignedDoctors: ['2'],
    createdAt: '2025-10-15T10:00:00',
  },
];
