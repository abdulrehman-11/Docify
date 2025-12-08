/**
 * Notification Panel Component
 * Slide-out drawer showing all notifications
 */
import React, { useState } from 'react';
import { Sheet, SheetContent, SheetHeader, SheetTitle } from '@/components/ui/sheet';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import {
  Bell,
  Calendar,
  Clock,
  CheckCircle2,
  X,
  Check,
  Trash2,
  RefreshCw,
  Settings,
} from 'lucide-react';
import { useNotifications } from '@/contexts/NotificationContext';
import { Notification } from '@/lib/api';
import { cn } from '@/lib/utils';
import { formatDistanceToNow, parseISO } from 'date-fns';

interface NotificationPanelProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

const getNotificationIcon = (type: string) => {
  switch (type) {
    case 'APPOINTMENT_CREATED':
    case 'APPOINTMENT_UPCOMING':
    case 'APPOINTMENT_UPDATED':
    case 'APPOINTMENT_RESCHEDULED':
    case 'APPOINTMENT_CANCELLED':
      return Calendar;
    case 'CLINIC_HOURS_UPDATED':
      return Clock;
    default:
      return Bell;
  }
};

const getNotificationColor = (type: string) => {
  switch (type) {
    case 'APPOINTMENT_CREATED':
      return 'bg-blue-500/10 text-blue-500 border-blue-500/20';
    case 'APPOINTMENT_UPCOMING':
      return 'bg-orange-500/10 text-orange-500 border-orange-500/20';
    case 'APPOINTMENT_CANCELLED':
      return 'bg-red-500/10 text-red-500 border-red-500/20';
    case 'APPOINTMENT_UPDATED':
    case 'APPOINTMENT_RESCHEDULED':
      return 'bg-yellow-500/10 text-yellow-500 border-yellow-500/20';
    case 'CLINIC_HOURS_UPDATED':
      return 'bg-green-500/10 text-green-500 border-green-500/20';
    default:
      return 'bg-primary/10 text-primary border-primary/20';
  }
};

interface NotificationItemProps {
  notification: Notification;
  onMarkAsRead: (id: number) => void;
}

const NotificationItem: React.FC<NotificationItemProps> = ({ notification, onMarkAsRead }) => {
  const Icon = getNotificationIcon(notification.type);
  const colorClass = getNotificationColor(notification.type);

  return (
    <div
      className={cn(
        'p-4 rounded-lg border transition-all hover:shadow-md cursor-pointer',
        notification.is_read
          ? 'bg-background/50 border-border/50 opacity-70'
          : 'bg-background/80 border-border glass-card'
      )}
      onClick={() => !notification.is_read && onMarkAsRead(notification.id)}
    >
      <div className="flex items-start gap-3">
        {/* Icon */}
        <div className={cn('p-2 rounded-lg border', colorClass)}>
          <Icon className="w-4 h-4" />
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-2 mb-1">
            <h4 className={cn('font-semibold text-sm', !notification.is_read && 'text-foreground')}>
              {notification.title}
            </h4>
            {!notification.is_read && (
              <div className="w-2 h-2 rounded-full bg-primary flex-shrink-0 mt-1.5" />
            )}
          </div>

          <p className="text-sm text-muted-foreground mb-2 line-clamp-2">{notification.message}</p>

          <div className="flex items-center gap-3 text-xs text-muted-foreground">
            <span>{formatDistanceToNow(parseISO(notification.created_at), { addSuffix: true })}</span>
            {notification.type.includes('APPOINTMENT') && notification.data?.patient_name && (
              <>
                <span>•</span>
                <span className="truncate">{notification.data.patient_name}</span>
              </>
            )}
          </div>
        </div>

        {/* Mark as Read Button */}
        {!notification.is_read && (
          <button
            onClick={(e) => {
              e.stopPropagation();
              onMarkAsRead(notification.id);
            }}
            className="p-1.5 rounded hover:bg-muted transition-colors flex-shrink-0"
            title="Mark as read"
          >
            <Check className="w-4 h-4" />
          </button>
        )}
      </div>
    </div>
  );
};

export const NotificationPanel: React.FC<NotificationPanelProps> = ({ open, onOpenChange }) => {
  const { notifications, unreadCount, loading, markAsRead, markAllAsRead, refreshNotifications } =
    useNotifications();
  const [activeTab, setActiveTab] = useState('all');

  const filterNotifications = (type?: string) => {
    if (!type || type === 'all') return notifications;
    if (type === 'appointments') {
      return notifications.filter((n) => n.type.includes('APPOINTMENT'));
    }
    if (type === 'clinic') {
      return notifications.filter((n) => n.type.includes('CLINIC'));
    }
    return notifications;
  };

  const filteredNotifications = filterNotifications(activeTab);
  const hasUnread = unreadCount > 0;

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent className="w-full sm:w-[480px] sm:max-w-[480px] p-0 glass-card">
        <SheetHeader className="p-6 pb-4 border-b border-border/50">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-primary/10 border border-primary/20">
                <Bell className="w-5 h-5 text-primary" />
              </div>
              <div>
                <SheetTitle className="text-xl">Notifications</SheetTitle>
                {unreadCount > 0 && (
                  <p className="text-sm text-muted-foreground mt-0.5">
                    {unreadCount} unread
                  </p>
                )}
              </div>
            </div>

            <div className="flex items-center gap-2">
              <Button
                variant="ghost"
                size="sm"
                onClick={refreshNotifications}
                disabled={loading}
                className="h-8 w-8 p-0"
              >
                <RefreshCw className={cn('w-4 h-4', loading && 'animate-spin')} />
              </Button>
            </div>
          </div>

          {hasUnread && (
            <div className="flex gap-2 mt-4">
              <Button
                variant="outline"
                size="sm"
                onClick={markAllAsRead}
                className="flex-1 text-xs h-8"
              >
                <CheckCircle2 className="w-3.5 h-3.5 mr-1.5" />
                Mark all as read
              </Button>
            </div>
          )}
        </SheetHeader>

        <Tabs value={activeTab} onValueChange={setActiveTab} className="flex-1">
          <div className="px-6 pt-4">
            <TabsList className="w-full glass">
              <TabsTrigger value="all" className="flex-1 text-xs">
                All
                {notifications.length > 0 && (
                  <Badge variant="secondary" className="ml-2 text-xs px-1.5 py-0">
                    {notifications.length}
                  </Badge>
                )}
              </TabsTrigger>
              <TabsTrigger value="appointments" className="flex-1 text-xs">
                <Calendar className="w-3 h-3 mr-1.5" />
                Appointments
              </TabsTrigger>
              <TabsTrigger value="clinic" className="flex-1 text-xs">
                <Clock className="w-3 h-3 mr-1.5" />
                Clinic
              </TabsTrigger>
            </TabsList>
          </div>

          <div className="h-[calc(100vh-240px)]">
            <TabsContent value="all" className="m-0 h-full">
              <ScrollArea className="h-full px-6 py-4">
                {filteredNotifications.length === 0 ? (
                  <div className="flex flex-col items-center justify-center h-64 text-center">
                    <div className="p-4 rounded-full bg-muted/50 mb-4">
                      <Bell className="w-8 h-8 text-muted-foreground" />
                    </div>
                    <h3 className="font-semibold text-lg mb-1">No notifications</h3>
                    <p className="text-sm text-muted-foreground">
                      You're all caught up!
                    </p>
                  </div>
                ) : (
                  <div className="space-y-3 pb-4">
                    {filteredNotifications.map((notification) => (
                      <NotificationItem
                        key={notification.id}
                        notification={notification}
                        onMarkAsRead={markAsRead}
                      />
                    ))}
                  </div>
                )}
              </ScrollArea>
            </TabsContent>

            <TabsContent value="appointments" className="m-0 h-full">
              <ScrollArea className="h-full px-6 py-4">
                {filterNotifications('appointments').length === 0 ? (
                  <div className="flex flex-col items-center justify-center h-64 text-center">
                    <div className="p-4 rounded-full bg-muted/50 mb-4">
                      <Calendar className="w-8 h-8 text-muted-foreground" />
                    </div>
                    <h3 className="font-semibold text-lg mb-1">No appointment notifications</h3>
                    <p className="text-sm text-muted-foreground">
                      Appointment updates will appear here
                    </p>
                  </div>
                ) : (
                  <div className="space-y-3 pb-4">
                    {filterNotifications('appointments').map((notification) => (
                      <NotificationItem
                        key={notification.id}
                        notification={notification}
                        onMarkAsRead={markAsRead}
                      />
                    ))}
                  </div>
                )}
              </ScrollArea>
            </TabsContent>

            <TabsContent value="clinic" className="m-0 h-full">
              <ScrollArea className="h-full px-6 py-4">
                {filterNotifications('clinic').length === 0 ? (
                  <div className="flex flex-col items-center justify-center h-64 text-center">
                    <div className="p-4 rounded-full bg-muted/50 mb-4">
                      <Clock className="w-8 h-8 text-muted-foreground" />
                    </div>
                    <h3 className="font-semibold text-lg mb-1">No clinic notifications</h3>
                    <p className="text-sm text-muted-foreground">
                      Clinic updates will appear here
                    </p>
                  </div>
                ) : (
                  <div className="space-y-3 pb-4">
                    {filterNotifications('clinic').map((notification) => (
                      <NotificationItem
                        key={notification.id}
                        notification={notification}
                        onMarkAsRead={markAsRead}
                      />
                    ))}
                  </div>
                )}
              </ScrollArea>
            </TabsContent>
          </div>
        </Tabs>
      </SheetContent>
    </Sheet>
  );
};
