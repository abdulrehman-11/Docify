/**
 * Notification Context for global notification state management
 */
import React, { createContext, useContext, useState, useEffect, useCallback, ReactNode } from 'react';
import { notificationApi, Notification } from '@/lib/api';
import { appointmentApi } from '@/lib/api';
import { toast } from 'sonner';
import { parseISO, differenceInMinutes, isBefore, isAfter } from 'date-fns';

interface NotificationContextType {
  notifications: Notification[];
  unreadCount: number;
  loading: boolean;
  showFloatingNotification: (notification: Notification) => void;
  floatingNotifications: Notification[];
  dismissFloatingNotification: (id: number) => void;
  markAsRead: (id: number) => Promise<void>;
  markAllAsRead: () => Promise<void>;
  refreshNotifications: () => Promise<void>;
}

const NotificationContext = createContext<NotificationContextType | undefined>(undefined);

export const useNotifications = () => {
  const context = useContext(NotificationContext);
  if (!context) {
    throw new Error('useNotifications must be used within NotificationProvider');
  }
  return context;
};

interface NotificationProviderProps {
  children: ReactNode;
  userRole?: 'admin' | 'staff';
}

const POLL_INTERVAL = 30000; // 30 seconds
const UPCOMING_APPOINTMENT_CHECK_INTERVAL = 60000; // 1 minute
const UPCOMING_APPOINTMENT_THRESHOLD = 5; // minutes

export const NotificationProvider: React.FC<NotificationProviderProps> = ({ children, userRole }) => {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [loading, setLoading] = useState(false);
  const [floatingNotifications, setFloatingNotifications] = useState<Notification[]>([]);
  const [checkedAppointments, setCheckedAppointments] = useState<Set<number>>(new Set());

  const showFloatingNotification = useCallback((notification: Notification) => {
    setFloatingNotifications(prev => {
      // Only keep max 3 floating notifications
      const newNotifications = [notification, ...prev].slice(0, 3);
      return newNotifications;
    });

    // Auto-dismiss after 30 seconds
    setTimeout(() => {
      setFloatingNotifications(prev => prev.filter(n => n.id !== notification.id));
    }, 30000);
  }, []);

  const dismissFloatingNotification = useCallback((id: number) => {
    setFloatingNotifications(prev => prev.filter(n => n.id !== id));
  }, []);

  const fetchNotifications = useCallback(async () => {
    if (!userRole) {
      return;
    }

    try {
      const data = await notificationApi.getNotifications({
        user_role: userRole,
        limit: 50,
      });
      
      setNotifications(data.notifications);
      setUnreadCount(data.unread_count);
    } catch (error) {
      console.error('Failed to fetch notifications:', error);
    }
  }, [userRole]);

  const checkUpcomingAppointments = useCallback(async () => {
    if (!userRole) return;

    try {
      const now = new Date();
      const fiveMinutesFromNow = new Date(now.getTime() + UPCOMING_APPOINTMENT_THRESHOLD * 60000);
      
      // Get today's appointments
      const today = now.toISOString().split('T')[0];
      const { appointments } = await appointmentApi.getAll({
        startDate: today,
        endDate: today,
        status: 'CONFIRMED',
      });

      appointments.forEach((appointment) => {
        const startTime = parseISO(appointment.start_time);
        const minutesUntil = differenceInMinutes(startTime, now);

        // Check if appointment is within 5 minutes and hasn't been checked yet
        if (
          minutesUntil > 0 &&
          minutesUntil <= UPCOMING_APPOINTMENT_THRESHOLD &&
          !checkedAppointments.has(appointment.id) &&
          isBefore(now, startTime) &&
          isAfter(fiveMinutesFromNow, startTime)
        ) {
          // Create floating notification
          const notification: Notification = {
            id: Date.now() + appointment.id, // Temporary ID for floating notification
            user_role: userRole,
            staff_id: null,
            type: 'APPOINTMENT_UPCOMING',
            title: 'Upcoming Appointment',
            message: `Appointment with ${appointment.patient_name} starting in ${minutesUntil} minute${minutesUntil !== 1 ? 's' : ''}`,
            data: {
              appointment_id: appointment.id,
              patient_name: appointment.patient_name,
              appointment_time: appointment.start_time,
              reason: appointment.reason,
            },
            is_read: false,
            created_at: new Date().toISOString(),
            read_at: null,
          };

          showFloatingNotification(notification);
          
          // Mark as checked so we don't show it again
          setCheckedAppointments(prev => new Set(prev).add(appointment.id));
        }
      });
    } catch (error) {
      console.error('Failed to check upcoming appointments:', error);
    }
  }, [userRole, showFloatingNotification]);

  const markAsRead = useCallback(async (id: number) => {
    try {
      await notificationApi.markAsRead(id);
      setNotifications(prev =>
        prev.map(n => (n.id === id ? { ...n, is_read: true } : n))
      );
      setUnreadCount(prev => Math.max(0, prev - 1));
    } catch (error) {
      console.error('Failed to mark notification as read:', error);
      toast.error('Failed to mark notification as read');
    }
  }, []);

  const markAllAsRead = useCallback(async () => {
    if (!userRole) return;

    try {
      await notificationApi.markAllAsRead({ user_role: userRole });
      setNotifications(prev => prev.map(n => ({ ...n, is_read: true })));
      setUnreadCount(0);
      toast.success('All notifications marked as read');
    } catch (error) {
      console.error('Failed to mark all as read:', error);
      toast.error('Failed to mark all as read');
    }
  }, [userRole]);

  const refreshNotifications = useCallback(async () => {
    setLoading(true);
    await fetchNotifications();
    setLoading(false);
  }, [fetchNotifications]);

  // Initial fetch
  useEffect(() => {
    if (userRole) {
      fetchNotifications();
    }
  }, [userRole, fetchNotifications]);

  // Poll for new notifications
  useEffect(() => {
    if (!userRole) return;

    const interval = setInterval(() => {
      fetchNotifications();
    }, POLL_INTERVAL);

    return () => clearInterval(interval);
  }, [userRole, fetchNotifications]);

  // Check for upcoming appointments
  useEffect(() => {
    if (!userRole) return;

    checkUpcomingAppointments();
    const interval = setInterval(() => {
      checkUpcomingAppointments();
    }, UPCOMING_APPOINTMENT_CHECK_INTERVAL);

    return () => clearInterval(interval);
  }, [userRole, checkUpcomingAppointments]);

  const value: NotificationContextType = {
    notifications,
    unreadCount,
    loading,
    showFloatingNotification,
    floatingNotifications,
    dismissFloatingNotification,
    markAsRead,
    markAllAsRead,
    refreshNotifications,
  };

  return <NotificationContext.Provider value={value}>{children}</NotificationContext.Provider>;
};
