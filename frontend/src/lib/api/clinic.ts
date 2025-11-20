import apiClient from './client';
import {
  ClinicHours,
  ClinicHoursUpdate,
} from './types';

export const clinicApi = {
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
};
