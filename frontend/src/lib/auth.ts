import { staffApi } from './api';

export type UserRole = 'admin' | 'staff';

export interface User {
  id?: number;
  email: string;
  name: string;
  role: UserRole;
  permissions?: Record<string, boolean>;
}

const ADMIN_EMAIL = 'admin@clinic.com';
const ADMIN_PASSWORD = 'Admin123';
const ADMIN_USER: User = {
  email: ADMIN_EMAIL,
  name: 'Admin User',
  role: 'admin' as UserRole,
  permissions: {},
};

export const login = async (email: string, password: string): Promise<User | null> => {
  try {
    if (email === ADMIN_EMAIL && password === ADMIN_PASSWORD) {
      sessionStorage.setItem('user', JSON.stringify(ADMIN_USER));
      sessionStorage.setItem('auth_token', 'admin_token');
      return ADMIN_USER;
    }
    
    const response = await staffApi.login({ email, password });
    if (response && response.user) {
      const staffUser: User = {
        id: response.user.id,
        email: response.user.email,
        name: response.user.name,
        role: 'staff' as UserRole,
        permissions: response.user.permissions,
      };
      sessionStorage.setItem('user', JSON.stringify(staffUser));
      sessionStorage.setItem('auth_token', response.access_token);
      return staffUser;
    }
    
    return null;
  } catch (error) {
    console.error('Login error:', error);
    return null;
  }
};

export const logout = (): void => {
  sessionStorage.removeItem('user');
  sessionStorage.removeItem('auth_token');
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
  
  if (user.permissions && typeof user.permissions === 'object') {
    return user.permissions[permission] === true;
  }
  
  return false;
};

export const getAuthToken = (): string | null => {
  return sessionStorage.getItem('auth_token');
};
