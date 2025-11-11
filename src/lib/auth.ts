export type UserRole = 'admin' | 'staff';

export interface User {
  email: string;
  name: string;
  role: UserRole;
  permissions?: string[];
}

const MOCK_USERS = {
  'admin@clinic.com': {
    password: 'Admin123',
    user: {
      email: 'admin@clinic.com',
      name: 'Admin User',
      role: 'admin' as UserRole,
    },
  },
  'staff@clinic.com': {
    password: 'Staff123',
    user: {
      email: 'staff@clinic.com',
      name: 'Staff Member',
      role: 'staff' as UserRole,
      permissions: ['view_appointments', 'add_appointments', 'edit_appointments'],
    },
  },
};

export const login = (email: string, password: string): User | null => {
  const userRecord = MOCK_USERS[email as keyof typeof MOCK_USERS];
  if (userRecord && userRecord.password === password) {
    sessionStorage.setItem('user', JSON.stringify(userRecord.user));
    return userRecord.user;
  }
  return null;
};

export const logout = (): void => {
  sessionStorage.removeItem('user');
};

export const getCurrentUser = (): User | null => {
  const userStr = sessionStorage.getItem('user');
  if (userStr) {
    try {
      return JSON.parse(userStr);
    } catch {
      return null;
    }
  }
  return null;
};

export const isAuthenticated = (): boolean => {
  return getCurrentUser() !== null;
};

export const hasPermission = (permission: string): boolean => {
  const user = getCurrentUser();
  if (!user) return false;
  if (user.role === 'admin') return true;
  return user.permissions?.includes(permission) || false;
};
