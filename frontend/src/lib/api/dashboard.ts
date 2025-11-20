import apiClient from './client';
import {
  DashboardStats,
  TodayAppointment,
  UpcomingAppointment,
} from './types';

export const dashboardApi = {
  /**
   * Get dashboard statistics
   */
  async getStats(): Promise<DashboardStats> {
    const response = await apiClient.get('/dashboard/stats');
    return response.data;
  },

  /**
   * Get today's appointments
   */
  async getTodayAppointments(): Promise<TodayAppointment[]> {
    const response = await apiClient.get('/dashboard/today');
    return response.data;
  },

  /**
   * Get upcoming appointments
   */
  async getUpcomingAppointments(days = 7): Promise<UpcomingAppointment[]> {
    const response = await apiClient.get(`/dashboard/upcoming?days=${days}`);
    return response.data;
  },
};
