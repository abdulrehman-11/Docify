/**
 * Notification API client
 */
import { apiClient } from './client';

export interface Notification {
  id: number;
  user_role: string | null;
  staff_id: number | null;
  type: string;
  title: string;
  message: string;
  data: Record<string, any> | null;
  is_read: boolean;
  created_at: string;
  read_at: string | null;
}

export interface NotificationListResponse {
  notifications: Notification[];
  total: number;
  unread_count: number;
}

export interface NotificationFilters {
  user_role?: string;
  staff_id?: number;
  is_read?: boolean;
  notification_type?: string;
  skip?: number;
  limit?: number;
}

export const notificationApi = {
  /**
   * Get notifications with filters
   */
  getNotifications: async (filters?: NotificationFilters): Promise<NotificationListResponse> => {
    const params = new URLSearchParams();
    
    if (filters?.user_role) params.append('user_role', filters.user_role);
    if (filters?.staff_id) params.append('staff_id', filters.staff_id.toString());
    if (filters?.is_read !== undefined) params.append('is_read', filters.is_read.toString());
    if (filters?.notification_type) params.append('notification_type', filters.notification_type);
    if (filters?.skip) params.append('skip', filters.skip.toString());
    if (filters?.limit) params.append('limit', filters.limit.toString());
    
    const response = await apiClient.get<NotificationListResponse>(
      `/notifications?${params.toString()}`
    );
    return response.data;
  },

  /**
   * Mark a notification as read
   */
  markAsRead: async (notificationId: number): Promise<Notification> => {
    const response = await apiClient.patch<Notification>(
      `/notifications/${notificationId}`,
      { is_read: true }
    );
    return response.data;
  },

  /**
   * Mark all notifications as read
   */
  markAllAsRead: async (filters?: { user_role?: string; staff_id?: number }): Promise<{ marked_read: number }> => {
    const params = new URLSearchParams();
    if (filters?.user_role) params.append('user_role', filters.user_role);
    if (filters?.staff_id) params.append('staff_id', filters.staff_id.toString());
    
    const response = await apiClient.post<{ marked_read: number }>(
      `/notifications/mark-all-read?${params.toString()}`
    );
    return response.data;
  },

  /**
   * Delete a notification
   */
  deleteNotification: async (notificationId: number): Promise<void> => {
    await apiClient.delete(`/notifications/${notificationId}`);
  },

  /**
   * Get unread notification count
   */
  getUnreadCount: async (filters?: { user_role?: string; staff_id?: number }): Promise<number> => {
    const params = new URLSearchParams();
    if (filters?.user_role) params.append('user_role', filters.user_role);
    if (filters?.staff_id) params.append('staff_id', filters.staff_id.toString());
    
    const response = await apiClient.get<{ unread_count: number }>(
      `/notifications/unread-count?${params.toString()}`
    );
    return response.data.unread_count;
  },
};
