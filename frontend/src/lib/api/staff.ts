import apiClient from './client';
import {
  Staff,
  StaffCreate,
  StaffUpdate,
  StaffListResponse,
  StaffLogin,
  StaffLoginResponse,
} from './types';

export const staffApi = {
  /**
   * Authenticate staff member
   */
  async login(credentials: StaffLogin): Promise<StaffLoginResponse> {
    const response = await apiClient.post('/staff/login', credentials);
    return response.data;
  },

  /**
   * Create a new staff member (admin only)
   */
  async create(data: StaffCreate): Promise<Staff> {
    const response = await apiClient.post('/staff', data);
    return response.data;
  },

  /**
   * Get all staff members with pagination
   */
  async list(params?: {
    page?: number;
    page_size?: number;
    is_active?: boolean;
  }): Promise<StaffListResponse> {
    const response = await apiClient.get('/staff', { params });
    return response.data;
  },

  /**
   * Get a staff member by ID
   */
  async getById(id: number): Promise<Staff> {
    const response = await apiClient.get(`/staff/${id}`);
    return response.data;
  },

  /**
   * Update a staff member (admin only)
   */
  async update(id: number, data: StaffUpdate): Promise<Staff> {
    const response = await apiClient.put(`/staff/${id}`, data);
    return response.data;
  },

  /**
   * Delete a staff member (soft delete, admin only)
   */
  async delete(id: number): Promise<void> {
    await apiClient.delete(`/staff/${id}`);
  },
};
