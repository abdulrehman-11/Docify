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
    user: 'admin@clinic.com',
    timestamp: '2025-11-10T14:30:00',
    details: 'Created appointment for Ahmed Khan with Dr. Sarah Johnson',
  },
  {
    id: '2',
    action: 'Appointment Cancelled',
    user: 'staff@clinic.com',
    timestamp: '2025-11-10T15:45:00',
    details: 'Cancelled appointment for Ali Hassan',
  },
];
