export type UserRole = 'admin' | 'staff';

export interface User {
  email: string;
  name: string;
  role: UserRole;
  permissions?: string[];
  assignedDoctors?: string[];
}

export interface UserCredential {
  email: string;
  password: string;
  user: User;
}

const STORAGE_KEY = 'clinic_users';

// Initialize default users in localStorage
const initializeUsers = () => {
  const existingUsers = localStorage.getItem(STORAGE_KEY);
  if (!existingUsers) {
    const defaultUsers: Record<string, UserCredential> = {
      'admin@clinic.com': {
        email: 'admin@clinic.com',
        password: 'Admin123',
        user: {
          email: 'admin@clinic.com',
          name: 'Admin User',
          role: 'admin' as UserRole,
        },
      },
      'staff@clinic.com': {
        email: 'staff@clinic.com',
        password: 'Staff123',
        user: {
          email: 'staff@clinic.com',
          name: 'Staff Member',
          role: 'staff' as UserRole,
          permissions: ['view_appointments', 'add_appointments', 'edit_appointments', 'cancel_appointments'],
          assignedDoctors: ['1', '3'],
        },
      },
    };
    localStorage.setItem(STORAGE_KEY, JSON.stringify(defaultUsers));
  }
};

initializeUsers();

const getUsers = (): Record<string, UserCredential> => {
  const users = localStorage.getItem(STORAGE_KEY);
  return users ? JSON.parse(users) : {};
};

const saveUsers = (users: Record<string, UserCredential>) => {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(users));
};

export const login = (email: string, password: string): User | null => {
  const users = getUsers();
  const userRecord = users[email];
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

export const createStaffAccount = (
  email: string,
  password: string,
  name: string,
  permissions: string[],
  assignedDoctors: string[]
): boolean => {
  const users = getUsers();
  
  // Check if email already exists
  if (users[email]) {
    return false;
  }

  users[email] = {
    email,
    password,
    user: {
      email,
      name,
      role: 'staff',
      permissions,
      assignedDoctors,
    },
  };

  saveUsers(users);
  return true;
};

export const updateStaffAccount = (
  email: string,
  name: string,
  permissions: string[],
  assignedDoctors: string[],
  newPassword?: string
): boolean => {
  const users = getUsers();
  
  if (!users[email] || users[email].user.role !== 'staff') {
    return false;
  }

  users[email].user.name = name;
  users[email].user.permissions = permissions;
  users[email].user.assignedDoctors = assignedDoctors;
  
  if (newPassword) {
    users[email].password = newPassword;
  }

  saveUsers(users);
  return true;
};

export const deleteStaffAccount = (email: string): boolean => {
  const users = getUsers();
  
  if (!users[email] || users[email].user.role !== 'staff') {
    return false;
  }

  delete users[email];
  saveUsers(users);
  return true;
};

export const getAllStaffAccounts = (): User[] => {
  const users = getUsers();
  return Object.values(users)
    .filter(u => u.user.role === 'staff')
    .map(u => u.user);
};
