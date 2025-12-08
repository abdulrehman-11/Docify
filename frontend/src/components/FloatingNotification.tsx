/**
 * Floating Notification Component
 * Bottom-right toast notification with 30s timer and animated progress bar
 */
import React, { useState, useEffect } from 'react';
import { X, Calendar, AlertCircle, CheckCircle, Info, Clock } from 'lucide-react';
import { Notification } from '@/lib/api';
import { cn } from '@/lib/utils';
import { formatDistanceToNow } from 'date-fns';

interface FloatingNotificationProps {
  notification: Notification;
  onDismiss: (id: number) => void;
  index: number;
}

const DURATION_MS = 30000; // 30 seconds

const getNotificationIcon = (type: string) => {
  switch (type) {
    case 'APPOINTMENT_CREATED':
    case 'APPOINTMENT_UPCOMING':
      return Calendar;
    case 'APPOINTMENT_CANCELLED':
      return AlertCircle;
    case 'APPOINTMENT_UPDATED':
    case 'APPOINTMENT_RESCHEDULED':
      return Clock;
    case 'CLINIC_HOURS_UPDATED':
      return CheckCircle;
    default:
      return Info;
  }
};

const getNotificationColor = (type: string) => {
  switch (type) {
    case 'APPOINTMENT_CREATED':
      return 'from-blue-500/20 to-blue-600/20 border-blue-500/30';
    case 'APPOINTMENT_UPCOMING':
      return 'from-orange-500/20 to-orange-600/20 border-orange-500/30';
    case 'APPOINTMENT_CANCELLED':
      return 'from-red-500/20 to-red-600/20 border-red-500/30';
    case 'APPOINTMENT_UPDATED':
    case 'APPOINTMENT_RESCHEDULED':
      return 'from-yellow-500/20 to-yellow-600/20 border-yellow-500/30';
    case 'CLINIC_HOURS_UPDATED':
      return 'from-green-500/20 to-green-600/20 border-green-500/30';
    default:
      return 'from-primary/20 to-accent/20 border-primary/30';
  }
};

const getIconColor = (type: string) => {
  switch (type) {
    case 'APPOINTMENT_CREATED':
      return 'text-blue-500';
    case 'APPOINTMENT_UPCOMING':
      return 'text-orange-500';
    case 'APPOINTMENT_CANCELLED':
      return 'text-red-500';
    case 'APPOINTMENT_UPDATED':
    case 'APPOINTMENT_RESCHEDULED':
      return 'text-yellow-500';
    case 'CLINIC_HOURS_UPDATED':
      return 'text-green-500';
    default:
      return 'text-primary';
  }
};

export const FloatingNotification: React.FC<FloatingNotificationProps> = ({
  notification,
  onDismiss,
  index,
}) => {
  const [progress, setProgress] = useState(100);
  const [isExiting, setIsExiting] = useState(false);

  useEffect(() => {
    const startTime = Date.now();
    const interval = setInterval(() => {
      const elapsed = Date.now() - startTime;
      const remaining = Math.max(0, 100 - (elapsed / DURATION_MS) * 100);
      setProgress(remaining);

      if (remaining === 0) {
        clearInterval(interval);
        handleDismiss();
      }
    }, 16); // ~60fps

    return () => clearInterval(interval);
  }, []);

  const handleDismiss = () => {
    setIsExiting(true);
    setTimeout(() => {
      onDismiss(notification.id);
    }, 300); // Match animation duration
  };

  const Icon = getNotificationIcon(notification.type);
  const colorClasses = getNotificationColor(notification.type);
  const iconColorClass = getIconColor(notification.type);

  // Calculate bottom position based on index (stack them)
  const bottomPosition = 24 + index * 120; // 24px base + 120px per notification

  return (
    <div
      className={cn(
        'fixed right-6 z-50 w-96 max-w-[calc(100vw-3rem)]',
        'transform transition-all duration-300 ease-out',
        isExiting
          ? 'translate-x-[calc(100%+3rem)] opacity-0'
          : 'translate-x-0 opacity-100'
      )}
      style={{ bottom: `${bottomPosition}px` }}
    >
      <div
        className={cn(
          'glass-card rounded-xl border-2 overflow-hidden shadow-2xl',
          'bg-gradient-to-br backdrop-blur-xl',
          colorClasses,
          'animate-slide-in-right'
        )}
      >
        {/* Progress Bar */}
        <div className="h-1 bg-background/20 relative overflow-hidden">
          <div
            className={cn(
              'h-full bg-gradient-to-r transition-all duration-75 ease-linear',
              notification.type === 'APPOINTMENT_UPCOMING'
                ? 'from-orange-400 to-orange-600'
                : notification.type === 'APPOINTMENT_CANCELLED'
                ? 'from-red-400 to-red-600'
                : 'from-primary to-accent'
            )}
            style={{ width: `${progress}%` }}
          />
        </div>

        <div className="p-4">
          <div className="flex items-start gap-3">
            {/* Icon */}
            <div
              className={cn(
                'p-2.5 rounded-xl bg-background/40 backdrop-blur-sm',
                'flex items-center justify-center flex-shrink-0'
              )}
            >
              <Icon className={cn('w-5 h-5', iconColorClass)} />
            </div>

            {/* Content */}
            <div className="flex-1 min-w-0">
              <h4 className="font-semibold text-sm text-foreground mb-1 truncate">
                {notification.title}
              </h4>
              <p className="text-sm text-muted-foreground line-clamp-2">
                {notification.message}
              </p>
              {notification.data?.appointment_time && (
                <p className="text-xs text-muted-foreground mt-1">
                  {formatDistanceToNow(new Date(notification.data.appointment_time), {
                    addSuffix: true,
                  })}
                </p>
              )}
            </div>

            {/* Close Button */}
            <button
              onClick={handleDismiss}
              className={cn(
                'p-1.5 rounded-lg hover:bg-background/40 transition-colors',
                'text-muted-foreground hover:text-foreground flex-shrink-0'
              )}
              aria-label="Dismiss notification"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

// Container for all floating notifications
interface FloatingNotificationsContainerProps {
  notifications: Notification[];
  onDismiss: (id: number) => void;
}

export const FloatingNotificationsContainer: React.FC<FloatingNotificationsContainerProps> = ({
  notifications,
  onDismiss,
}) => {
  return (
    <>
      {notifications.map((notification, index) => (
        <FloatingNotification
          key={notification.id}
          notification={notification}
          onDismiss={onDismiss}
          index={index}
        />
      ))}
    </>
  );
};
