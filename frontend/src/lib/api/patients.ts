import apiClient from './client';
import {
  Patient,
  PatientCreate,
  PatientUpdate,
  PatientListResponse,
} from './types';

export const patientApi = {
  /**
   * Get all patients with pagination and optional search
   */
  async getAll(
    page = 1,
    pageSize = 50,
    search?: string
  ): Promise<PatientListResponse> {
    const params = new URLSearchParams({
      page: page.toString(),
      page_size: pageSize.toString(),
    });
    if (search) {
      params.append('search', search);
    }

    const response = await apiClient.get(`/patients?${params.toString()}`);
    return response.data;
  },

  /**
   * Get a single patient by ID
   */
  async getById(id: number): Promise<Patient> {
    const response = await apiClient.get(`/patients/${id}`);
    return response.data;
  },

  /**
   * Create a new patient
   */
  async create(data: PatientCreate): Promise<Patient> {
    const response = await apiClient.post('/patients', data);
    return response.data;
  },

  /**
   * Update an existing patient
   */
  async update(id: number, data: PatientUpdate): Promise<Patient> {
    const response = await apiClient.put(`/patients/${id}`, data);
    return response.data;
  },

  /**
   * Delete a patient
   */
  async delete(id: number): Promise<void> {
    await apiClient.delete(`/patients/${id}`);
  },
};
