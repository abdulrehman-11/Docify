import apiClient from './client';
import {
  Appointment,
  AppointmentCreate,
  AppointmentUpdate,
  AppointmentListResponse,
  AvailabilityRequest,
  AvailabilityResponse,
  AppointmentStatus,
} from './types';

export const appointmentApi = {
  /**
   * Get all appointments with filters and pagination
   */
  async getAll(params?: {
    page?: number;
    pageSize?: number;
    status?: AppointmentStatus;
    patientId?: number;
    startDate?: string;
    endDate?: string;
  }): Promise<AppointmentListResponse> {
    const searchParams = new URLSearchParams();
    
    if (params?.page) searchParams.append('page', params.page.toString());
    if (params?.pageSize) searchParams.append('page_size', params.pageSize.toString());
    if (params?.status) searchParams.append('status', params.status);
    if (params?.patientId) searchParams.append('patient_id', params.patientId.toString());
    if (params?.startDate) searchParams.append('start_date', params.startDate);
    if (params?.endDate) searchParams.append('end_date', params.endDate);

    const response = await apiClient.get(`/appointments?${searchParams.toString()}`);
    return response.data;
  },

  /**
   * Get a single appointment by ID
   */
  async getById(id: number): Promise<Appointment> {
    const response = await apiClient.get(`/appointments/${id}`);
    return response.data;
  },

  /**
   * Create a new appointment
   */
  async create(data: AppointmentCreate): Promise<Appointment> {
    const response = await apiClient.post('/appointments', data);
    return response.data;
  },

  /**
   * Update an existing appointment
   */
  async update(id: number, data: AppointmentUpdate): Promise<Appointment> {
    const response = await apiClient.put(`/appointments/${id}`, data);
    return response.data;
  },

  /**
   * Cancel an appointment
   */
  async cancel(id: number, reason?: string): Promise<Appointment> {
    const response = await apiClient.post(`/appointments/${id}/cancel`, {
      cancellation_reason: reason,
    });
    return response.data;
  },

  /**
   * Delete an appointment
   */
  async delete(id: number): Promise<void> {
    await apiClient.delete(`/appointments/${id}`);
  },

  /**
   * Check available appointment slots
   */
  async checkAvailability(request: AvailabilityRequest): Promise<AvailabilityResponse> {
    const response = await apiClient.post('/appointments/availability', request);
    return response.data;
  },
};
