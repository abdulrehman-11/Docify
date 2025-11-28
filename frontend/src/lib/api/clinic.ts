import apiClient from './client';
import {
  ClinicHours,
  ClinicHoursUpdate,
  ClinicHoursBulkUpdate,
  ClinicHoliday,
  ClinicHolidayCreate,
  ClinicHolidayUpdate,
} from './types';

export const clinicApi = {
  // ============ Clinic Hours ============
  
  /**
   * Get clinic hours for all days
   */
  async getHours(): Promise<ClinicHours[]> {
    const response = await apiClient.get('/clinic/hours');
    return response.data;
  },

  /**
   * Update clinic hours for a specific day
   */
  async updateHours(id: number, data: ClinicHoursUpdate): Promise<ClinicHours> {
    const response = await apiClient.put(`/clinic/hours/${id}`, data);
    return response.data;
  },

  /**
   * Clear break time for a specific day
   */
  async clearBreakTime(id: number): Promise<ClinicHours> {
    const response = await apiClient.put(`/clinic/hours/${id}/clear-break`);
    return response.data;
  },

  /**
   * Bulk update clinic hours for multiple days (apply to all selected days)
   */
  async bulkUpdateHours(data: ClinicHoursBulkUpdate): Promise<ClinicHours[]> {
    const response = await apiClient.post('/clinic/hours/bulk', data);
    return response.data;
  },

  // ============ Clinic Holidays ============
  
  /**
   * Get all clinic holidays
   */
  async getHolidays(upcomingOnly: boolean = false): Promise<ClinicHoliday[]> {
    const response = await apiClient.get('/clinic/holidays', {
      params: { upcoming_only: upcomingOnly }
    });
    return response.data;
  },

  /**
   * Get a specific holiday by ID
   */
  async getHoliday(id: number): Promise<ClinicHoliday> {
    const response = await apiClient.get(`/clinic/holidays/${id}`);
    return response.data;
  },

  /**
   * Create a new clinic holiday
   */
  async createHoliday(data: ClinicHolidayCreate): Promise<ClinicHoliday> {
    const response = await apiClient.post('/clinic/holidays', data);
    return response.data;
  },

  /**
   * Update an existing clinic holiday
   */
  async updateHoliday(id: number, data: ClinicHolidayUpdate): Promise<ClinicHoliday> {
    const response = await apiClient.put(`/clinic/holidays/${id}`, data);
    return response.data;
  },

  /**
   * Delete a clinic holiday
   */
  async deleteHoliday(id: number): Promise<void> {
    await apiClient.delete(`/clinic/holidays/${id}`);
  },
};
