# Frontend Integration Guide

## 🔌 Connecting Your React Frontend to the API

### Base URL Configuration

In your React frontend, set the API base URL:

```typescript
// src/lib/api.ts or src/config.ts
export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
```

### Environment Variable (.env)

```env
VITE_API_URL=http://localhost:8000
```

---

## 📡 API Endpoints Reference for Frontend

### Patients

```typescript
// List patients with pagination
GET /patients?page=1&page_size=50&search=john

// Get single patient
GET /patients/{id}

// Create patient
POST /patients
Body: { name, email, phone, insurance_provider? }

// Update patient
PUT /patients/{id}
Body: { name?, email?, phone?, insurance_provider? }

// Delete patient
DELETE /patients/{id}
```

### Appointments

```typescript
// List appointments with filters
GET /appointments?page=1&page_size=50&status=CONFIRMED&patient_id=1&start_date=2025-11-15T00:00:00Z

// Get single appointment
GET /appointments/{id}

// Create appointment
POST /appointments
Body: { patient_id, start_time, end_time, reason }

// Update appointment
PUT /appointments/{id}
Body: { start_time?, end_time?, reason?, status?, cancellation_reason? }

// Cancel appointment
POST /appointments/{id}/cancel
Body: { cancellation_reason? }

// Check availability
POST /appointments/availability
Body: { start_date: "2025-11-15T09:00:00Z", end_date: "2025-11-15T17:00:00Z" }
```

### Dashboard

```typescript
// Get statistics
GET /dashboard/stats
// Returns: { total_appointments_today, total_appointments_upcoming, total_patients, ... }

// Today's appointments
GET /dashboard/today

// Upcoming appointments
GET /dashboard/upcoming?days=7
```

### Clinic Hours

```typescript
// Get all clinic hours
GET /clinic/hours

// Update clinic hours
PUT /clinic/hours/{id}
Body: { start_time?, end_time?, is_active? }
```

---

## 💻 Sample React/TypeScript Code

### API Client Setup

```typescript
// src/lib/api-client.ts
import axios from 'axios';

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

export default apiClient;
```

### Fetch Patients Example

```typescript
// src/services/patientService.ts
import apiClient from '@/lib/api-client';

export interface Patient {
  id: number;
  name: string;
  email: string;
  phone: string;
  insurance_provider: string | null;
  created_at: string;
  updated_at: string;
}

export interface PatientListResponse {
  total: number;
  page: number;
  page_size: number;
  patients: Patient[];
}

export const patientService = {
  async getAll(page = 1, pageSize = 50, search?: string): Promise<PatientListResponse> {
    const params = new URLSearchParams({
      page: page.toString(),
      page_size: pageSize.toString(),
    });
    if (search) params.append('search', search);
    
    const response = await apiClient.get(`/patients?${params}`);
    return response.data;
  },

  async getById(id: number): Promise<Patient> {
    const response = await apiClient.get(`/patients/${id}`);
    return response.data;
  },

  async create(data: Omit<Patient, 'id' | 'created_at' | 'updated_at'>): Promise<Patient> {
    const response = await apiClient.post('/patients', data);
    return response.data;
  },

  async update(id: number, data: Partial<Patient>): Promise<Patient> {
    const response = await apiClient.put(`/patients/${id}`, data);
    return response.data;
  },

  async delete(id: number): Promise<void> {
    await apiClient.delete(`/patients/${id}`);
  },
};
```

### Fetch Appointments Example

```typescript
// src/services/appointmentService.ts
import apiClient from '@/lib/api-client';

export interface Appointment {
  id: number;
  patient_id: number;
  patient_name: string;
  patient_email: string;
  patient_phone: string;
  start_time: string;
  end_time: string;
  reason: string;
  status: 'CONFIRMED' | 'CANCELLED' | 'RESCHEDULED' | 'COMPLETED';
  cancellation_reason: string | null;
  created_at: string;
  updated_at: string;
}

export const appointmentService = {
  async getAll(params?: {
    page?: number;
    page_size?: number;
    status?: string;
    patient_id?: number;
    start_date?: string;
    end_date?: string;
  }): Promise<{ total: number; page: number; page_size: number; appointments: Appointment[] }> {
    const searchParams = new URLSearchParams();
    if (params?.page) searchParams.append('page', params.page.toString());
    if (params?.page_size) searchParams.append('page_size', params.page_size.toString());
    if (params?.status) searchParams.append('status', params.status);
    if (params?.patient_id) searchParams.append('patient_id', params.patient_id.toString());
    if (params?.start_date) searchParams.append('start_date', params.start_date);
    if (params?.end_date) searchParams.append('end_date', params.end_date);
    
    const response = await apiClient.get(`/appointments?${searchParams}`);
    return response.data;
  },

  async checkAvailability(startDate: string, endDate: string) {
    const response = await apiClient.post('/appointments/availability', {
      start_date: startDate,
      end_date: endDate,
    });
    return response.data.slots;
  },

  async create(data: {
    patient_id: number;
    start_time: string;
    end_time: string;
    reason: string;
  }): Promise<Appointment> {
    const response = await apiClient.post('/appointments', data);
    return response.data;
  },

  async cancel(id: number, reason?: string): Promise<Appointment> {
    const response = await apiClient.post(`/appointments/${id}/cancel`, {
      cancellation_reason: reason,
    });
    return response.data;
  },
};
```

### Dashboard Stats Example

```typescript
// src/services/dashboardService.ts
import apiClient from '@/lib/api-client';

export const dashboardService = {
  async getStats() {
    const response = await apiClient.get('/dashboard/stats');
    return response.data;
  },

  async getTodayAppointments() {
    const response = await apiClient.get('/dashboard/today');
    return response.data;
  },

  async getUpcomingAppointments(days = 7) {
    const response = await apiClient.get(`/dashboard/upcoming?days=${days}`);
    return response.data;
  },
};
```

### React Query Hooks Example

```typescript
// src/hooks/usePatients.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { patientService } from '@/services/patientService';

export const usePatients = (page = 1, pageSize = 50, search?: string) => {
  return useQuery({
    queryKey: ['patients', page, pageSize, search],
    queryFn: () => patientService.getAll(page, pageSize, search),
  });
};

export const useCreatePatient = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: patientService.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['patients'] });
    },
  });
};

export const useDeletePatient = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (id: number) => patientService.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['patients'] });
    },
  });
};
```

---

## 🎨 Component Examples

### Patient List Component

```typescript
import { usePatients } from '@/hooks/usePatients';

export function PatientList() {
  const { data, isLoading, error } = usePatients(1, 50);

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error loading patients</div>;

  return (
    <div>
      <h2>Patients ({data?.total})</h2>
      <table>
        <thead>
          <tr>
            <th>Name</th>
            <th>Email</th>
            <th>Phone</th>
            <th>Insurance</th>
          </tr>
        </thead>
        <tbody>
          {data?.patients.map((patient) => (
            <tr key={patient.id}>
              <td>{patient.name}</td>
              <td>{patient.email}</td>
              <td>{patient.phone}</td>
              <td>{patient.insurance_provider || 'N/A'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
```

---

## 📋 Response Formats

### Patient Response
```json
{
  "id": 1,
  "name": "John Doe",
  "email": "john.doe@example.com",
  "phone": "555-0123",
  "insurance_provider": "Blue Cross",
  "created_at": "2025-11-14T10:00:00Z",
  "updated_at": "2025-11-14T10:00:00Z"
}
```

### Appointment Response
```json
{
  "id": 1,
  "patient_id": 1,
  "patient_name": "John Doe",
  "patient_email": "john.doe@example.com",
  "patient_phone": "555-0123",
  "start_time": "2025-11-15T14:00:00Z",
  "end_time": "2025-11-15T14:30:00Z",
  "reason": "Annual checkup",
  "status": "CONFIRMED",
  "cancellation_reason": null,
  "created_at": "2025-11-14T10:00:00Z",
  "updated_at": "2025-11-14T10:00:00Z"
}
```

### Dashboard Stats Response
```json
{
  "total_appointments_today": 5,
  "total_appointments_upcoming": 15,
  "total_patients": 42,
  "confirmed_appointments": 20,
  "cancelled_appointments": 3,
  "completed_appointments": 100
}
```

---

## 🚀 Getting Started

1. **Start the API server** (backend/api):
   ```bash
   python start.py
   ```

2. **Update your frontend** `.env` file:
   ```env
   VITE_API_URL=http://localhost:8000
   ```

3. **Create API client** and services as shown above

4. **Test the connection**:
   ```typescript
   fetch('http://localhost:8000/health')
     .then(res => res.json())
     .then(data => console.log(data));
   ```

5. **Start building your UI!** All endpoints are ready to use.

---

## 🎯 Tips

- Use React Query or SWR for data fetching
- Implement optimistic updates for better UX
- Add loading states and error handling
- Use TypeScript interfaces for type safety
- Implement pagination on large lists
- Add search/filter functionality
- Format dates using date-fns or dayjs

**Your API is ready - happy coding!** 🚀
