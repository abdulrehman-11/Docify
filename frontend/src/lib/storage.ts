import {
  Doctor,
  Appointment,
  Service,
  ClinicInfo,
  AuditLog,
  KnowledgeBaseItem,
  NotificationTemplate,
  StaffMember,
  mockDoctors,
  mockAppointments,
  mockServices,
  mockClinicInfo,
  mockAuditLogs,
  mockKnowledgeBase,
  mockNotificationTemplates,
  mockStaffMembers,
} from './mockData';

const STORAGE_KEYS = {
  DOCTORS: 'clinic_doctors',
  APPOINTMENTS: 'clinic_appointments',
  SERVICES: 'clinic_services',
  CLINIC_INFO: 'clinic_info',
  AUDIT_LOGS: 'clinic_audit_logs',
  KNOWLEDGE_BASE: 'clinic_knowledge_base',
  NOTIFICATION_TEMPLATES: 'clinic_notification_templates',
  STAFF_MEMBERS: 'clinic_staff_members',
};

// Initialize localStorage with mock data if empty
const initializeStorage = () => {
  if (!localStorage.getItem(STORAGE_KEYS.DOCTORS)) {
    localStorage.setItem(STORAGE_KEYS.DOCTORS, JSON.stringify(mockDoctors));
  }
  if (!localStorage.getItem(STORAGE_KEYS.APPOINTMENTS)) {
    localStorage.setItem(STORAGE_KEYS.APPOINTMENTS, JSON.stringify(mockAppointments));
  }
  if (!localStorage.getItem(STORAGE_KEYS.SERVICES)) {
    localStorage.setItem(STORAGE_KEYS.SERVICES, JSON.stringify(mockServices));
  }
  if (!localStorage.getItem(STORAGE_KEYS.CLINIC_INFO)) {
    localStorage.setItem(STORAGE_KEYS.CLINIC_INFO, JSON.stringify(mockClinicInfo));
  }
  if (!localStorage.getItem(STORAGE_KEYS.AUDIT_LOGS)) {
    localStorage.setItem(STORAGE_KEYS.AUDIT_LOGS, JSON.stringify(mockAuditLogs));
  }
  if (!localStorage.getItem(STORAGE_KEYS.KNOWLEDGE_BASE)) {
    localStorage.setItem(STORAGE_KEYS.KNOWLEDGE_BASE, JSON.stringify(mockKnowledgeBase));
  }
  if (!localStorage.getItem(STORAGE_KEYS.NOTIFICATION_TEMPLATES)) {
    localStorage.setItem(STORAGE_KEYS.NOTIFICATION_TEMPLATES, JSON.stringify(mockNotificationTemplates));
  }
  if (!localStorage.getItem(STORAGE_KEYS.STAFF_MEMBERS)) {
    localStorage.setItem(STORAGE_KEYS.STAFF_MEMBERS, JSON.stringify(mockStaffMembers));
  }
};

initializeStorage();

// Doctors
export const getDoctors = (): Doctor[] => {
  const data = localStorage.getItem(STORAGE_KEYS.DOCTORS);
  return data ? JSON.parse(data) : mockDoctors;
};

export const saveDoctor = (doctor: Doctor): void => {
  const doctors = getDoctors();
  const index = doctors.findIndex((d) => d.id === doctor.id);
  if (index >= 0) {
    doctors[index] = doctor;
  } else {
    doctors.push(doctor);
  }
  localStorage.setItem(STORAGE_KEYS.DOCTORS, JSON.stringify(doctors));
  addAuditLog('Provider Updated', `Updated provider: ${doctor.name}`);
};

export const deleteDoctor = (id: string): void => {
  const doctors = getDoctors();
  const filtered = doctors.filter((d) => d.id !== id);
  localStorage.setItem(STORAGE_KEYS.DOCTORS, JSON.stringify(filtered));
  addAuditLog('Provider Deleted', `Deleted provider with ID: ${id}`);
};

// Appointments
export const getAppointments = (): Appointment[] => {
  const data = localStorage.getItem(STORAGE_KEYS.APPOINTMENTS);
  return data ? JSON.parse(data) : mockAppointments;
};

export const saveAppointment = (appointment: Appointment): void => {
  const appointments = getAppointments();
  const index = appointments.findIndex((a) => a.id === appointment.id);
  if (index >= 0) {
    appointments[index] = appointment;
    addAuditLog('Appointment Updated', `Updated appointment for ${appointment.patientName}`);
  } else {
    appointments.push(appointment);
    addAuditLog('Appointment Created', `Created appointment for ${appointment.patientName}`);
  }
  localStorage.setItem(STORAGE_KEYS.APPOINTMENTS, JSON.stringify(appointments));
};

export const deleteAppointment = (id: string): void => {
  const appointments = getAppointments();
  const appointment = appointments.find((a) => a.id === id);
  const filtered = appointments.filter((a) => a.id !== id);
  localStorage.setItem(STORAGE_KEYS.APPOINTMENTS, JSON.stringify(filtered));
  if (appointment) {
    addAuditLog('Appointment Deleted', `Deleted appointment for ${appointment.patientName}`);
  }
};

export const updateAppointmentStatus = (id: string, status: Appointment['status']): void => {
  const appointments = getAppointments();
  const index = appointments.findIndex((a) => a.id === id);
  if (index >= 0) {
    appointments[index].status = status;
    localStorage.setItem(STORAGE_KEYS.APPOINTMENTS, JSON.stringify(appointments));
    addAuditLog('Appointment Status Changed', `Changed appointment status to ${status} for ${appointments[index].patientName}`);
  }
};

// Services
export const getServices = (): Service[] => {
  const data = localStorage.getItem(STORAGE_KEYS.SERVICES);
  return data ? JSON.parse(data) : mockServices;
};

export const saveService = (service: Service): void => {
  const services = getServices();
  const index = services.findIndex((s) => s.id === service.id);
  if (index >= 0) {
    services[index] = service;
  } else {
    services.push(service);
  }
  localStorage.setItem(STORAGE_KEYS.SERVICES, JSON.stringify(services));
  addAuditLog('Service Updated', `Updated service: ${service.name}`);
};

export const deleteService = (id: string): void => {
  const services = getServices();
  const filtered = services.filter((s) => s.id !== id);
  localStorage.setItem(STORAGE_KEYS.SERVICES, JSON.stringify(filtered));
  addAuditLog('Service Deleted', `Deleted service with ID: ${id}`);
};

// Clinic Info
export const getClinicInfo = (): ClinicInfo => {
  const data = localStorage.getItem(STORAGE_KEYS.CLINIC_INFO);
  return data ? JSON.parse(data) : mockClinicInfo;
};

export const saveClinicInfo = (info: ClinicInfo): void => {
  localStorage.setItem(STORAGE_KEYS.CLINIC_INFO, JSON.stringify(info));
  addAuditLog('Clinic Info Updated', 'Updated clinic information');
};

// Audit Logs
export const getAuditLogs = (): AuditLog[] => {
  const data = localStorage.getItem(STORAGE_KEYS.AUDIT_LOGS);
  return data ? JSON.parse(data) : mockAuditLogs;
};

export const addAuditLog = (action: string, details: string): void => {
  const logs = getAuditLogs();
  const user = JSON.parse(sessionStorage.getItem('user') || '{}');
  const newLog: AuditLog = {
    id: Date.now().toString(),
    action,
    user: user.name || 'System',
    timestamp: new Date().toISOString(),
    details,
  };
  logs.unshift(newLog);
  localStorage.setItem(STORAGE_KEYS.AUDIT_LOGS, JSON.stringify(logs.slice(0, 100))); // Keep last 100 logs
};

// Knowledge Base
export const getKnowledgeBase = (): KnowledgeBaseItem[] => {
  const data = localStorage.getItem(STORAGE_KEYS.KNOWLEDGE_BASE);
  return data ? JSON.parse(data) : mockKnowledgeBase;
};

export const saveKnowledgeBaseItem = (item: KnowledgeBaseItem): void => {
  const items = getKnowledgeBase();
  const index = items.findIndex((i) => i.id === item.id);
  if (index >= 0) {
    items[index] = item;
  } else {
    items.push(item);
  }
  localStorage.setItem(STORAGE_KEYS.KNOWLEDGE_BASE, JSON.stringify(items));
  addAuditLog('Knowledge Base Updated', `Updated KB item: ${item.question}`);
};

export const deleteKnowledgeBaseItem = (id: string): void => {
  const items = getKnowledgeBase();
  const filtered = items.filter((i) => i.id !== id);
  localStorage.setItem(STORAGE_KEYS.KNOWLEDGE_BASE, JSON.stringify(filtered));
  addAuditLog('Knowledge Base Item Deleted', `Deleted KB item with ID: ${id}`);
};

// Notification Templates
export const getNotificationTemplates = (): NotificationTemplate[] => {
  const data = localStorage.getItem(STORAGE_KEYS.NOTIFICATION_TEMPLATES);
  return data ? JSON.parse(data) : mockNotificationTemplates;
};

export const saveNotificationTemplate = (template: NotificationTemplate): void => {
  const templates = getNotificationTemplates();
  const index = templates.findIndex((t) => t.id === template.id);
  if (index >= 0) {
    templates[index] = template;
  } else {
    templates.push(template);
  }
  localStorage.setItem(STORAGE_KEYS.NOTIFICATION_TEMPLATES, JSON.stringify(templates));
  addAuditLog('Notification Template Updated', `Updated template: ${template.name}`);
};

export const deleteNotificationTemplate = (id: string): void => {
  const templates = getNotificationTemplates();
  const filtered = templates.filter((t) => t.id !== id);
  localStorage.setItem(STORAGE_KEYS.NOTIFICATION_TEMPLATES, JSON.stringify(filtered));
  addAuditLog('Notification Template Deleted', `Deleted template with ID: ${id}`);
};

// Staff Members
export const getStaffMembers = (): StaffMember[] => {
  const data = localStorage.getItem(STORAGE_KEYS.STAFF_MEMBERS);
  return data ? JSON.parse(data) : mockStaffMembers;
};

export const saveStaffMember = (staff: StaffMember): void => {
  const staffMembers = getStaffMembers();
  const index = staffMembers.findIndex((s) => s.id === staff.id);
  if (index >= 0) {
    staffMembers[index] = staff;
  } else {
    staffMembers.push(staff);
  }
  localStorage.setItem(STORAGE_KEYS.STAFF_MEMBERS, JSON.stringify(staffMembers));
  addAuditLog('Staff Member Updated', `Updated staff: ${staff.name}`);
};

export const deleteStaffMember = (id: string): void => {
  const staffMembers = getStaffMembers();
  const filtered = staffMembers.filter((s) => s.id !== id);
  localStorage.setItem(STORAGE_KEYS.STAFF_MEMBERS, JSON.stringify(filtered));
  addAuditLog('Staff Member Deleted', `Deleted staff with ID: ${id}`);
};
