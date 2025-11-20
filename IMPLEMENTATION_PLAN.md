# 📋 FRONTEND-BACKEND INTEGRATION PLAN

## 🔍 ANALYSIS SUMMARY

### Backend Database (Neon PostgreSQL)
**Existing Tables:**
1. ✅ `patients` - patient information
2. ✅ `appointments` - appointment bookings
3. ✅ `clinic_hours` - clinic operating hours
4. ✅ `alembic_version` - migrations

**NO TABLES FOR:**
- ❌ Doctors/Providers
- ❌ Services
- ❌ Staff members
- ❌ Users/Authentication
- ❌ Audit logs
- ❌ Knowledge base
- ❌ Notification templates

### Frontend Currently Has (Using Mock Data):
1. ✅ Patients (via appointments - patient info)
2. ✅ Appointments
3. ❌ **Doctors/Providers** - NOT IN DATABASE
4. ❌ **Services** - NOT IN DATABASE
5. ❌ **Staff Management** - NOT IN DATABASE
6. ❌ **Audit Logs** - NOT IN DATABASE
7. ❌ **Knowledge Base** - NOT IN DATABASE
8. ❌ **Notifications** - NOT IN DATABASE
9. ✅ Clinic Info (via clinic_hours)

---

## 🎯 IMPLEMENTATION STRATEGY

### Phase 1: Core Connectivity (PRIORITY)
**Connect what EXISTS in database:**
1. ✅ Patients Management
2. ✅ Appointments Management  
3. ✅ Dashboard Statistics
4. ✅ Clinic Hours

### Phase 2: UI Cleanup (REMOVE)
**Remove/Hide pages that have NO database support:**
1. ❌ Providers page - REMOVE (no doctors table)
2. ❌ Services page - REMOVE (no services table)
3. ❌ Staff page - REMOVE (no staff table)
4. ❌ Audit page - REMOVE (no audit table)
5. ❌ Knowledge page - REMOVE (no knowledge base)
6. ❌ Notifications page - REMOVE (no notifications table)

### Phase 3: Simplify Data Model
**Update interfaces to match backend:**
- Remove `Doctor` references
- Simplify `Appointment` to match backend schema
- Add `Patient` interface matching backend
- Update `ClinicInfo` to use `clinic_hours` table

---

## 📝 DETAILED IMPLEMENTATION STEPS

### Step 1: Create API Client Layer
- [ ] Create `src/lib/api/client.ts` - Axios instance
- [ ] Create `src/lib/api/patients.ts` - Patient API calls
- [ ] Create `src/lib/api/appointments.ts` - Appointment API calls
- [ ] Create `src/lib/api/clinic.ts` - Clinic hours API calls
- [ ] Create `src/lib/api/dashboard.ts` - Dashboard stats API calls
- [ ] Create `src/lib/api/types.ts` - TypeScript interfaces matching backend

### Step 2: Update Type Definitions
- [ ] Create backend-matching types in `src/lib/api/types.ts`
- [ ] Remove unused types (Doctor, Service, Staff, etc.)

### Step 3: Remove Unsupported Pages
- [ ] Delete `src/pages/admin/Providers.tsx`
- [ ] Delete `src/pages/admin/Services.tsx`
- [ ] Delete `src/pages/admin/Staff.tsx`
- [ ] Delete `src/pages/admin/Audit.tsx`
- [ ] Delete `src/pages/admin/Knowledge.tsx`
- [ ] Delete `src/pages/admin/Notifications.tsx`

### Step 4: Update App Routes
- [ ] Remove routes for deleted pages
- [ ] Update sidebar navigation

### Step 5: Update Appointments Page
- [ ] Remove doctor/provider selection (no doctors in DB)
- [ ] Connect to real appointment API
- [ ] Show patient information directly
- [ ] Update appointment creation/editing
- [ ] Implement real-time data fetching

### Step 6: Update Dashboard
- [ ] Connect to `/dashboard/stats` API
- [ ] Connect to `/dashboard/today` API
- [ ] Connect to `/dashboard/upcoming` API
- [ ] Remove provider/doctor stats

### Step 7: Create Patients Management Page
- [ ] Create new `src/pages/admin/Patients.tsx`
- [ ] List all patients
- [ ] Add/Edit/Delete patients
- [ ] Search functionality

### Step 8: Update Clinic Hours Page
- [ ] Connect to `/clinic/hours` API
- [ ] Update hours display (Mon-Sun)
- [ ] Edit functionality

### Step 9: Update Components
- [ ] Update `AppointmentDialog` to remove doctor selection
- [ ] Update `Calendar` component if needed
- [ ] Remove doctor-related components

### Step 10: Environment Configuration
- [ ] Create `.env` with API_URL
- [ ] Add axios for HTTP requests

### Step 11: Testing
- [ ] Test patient CRUD operations
- [ ] Test appointment CRUD operations
- [ ] Test dashboard data display
- [ ] Test clinic hours display/update

---

## 🗄️ TABLES TO ADD TO DATABASE (Recommendations)

### Critical (For Full Functionality):
1. **`users` table** - For authentication
   ```sql
   - id
   - email
   - password_hash
   - role (admin, staff)
   - name
   - created_at, updated_at
   ```

2. **`services` table** - For service types
   ```sql
   - id
   - name
   - duration (minutes)
   - description
   - price (optional)
   - is_active
   - created_at, updated_at
   ```

### Optional (Future Enhancements):
3. **`providers` table** - If you want doctor management
   ```sql
   - id
   - name
   - specialty
   - email, phone
   - bio
   - is_active
   - created_at, updated_at
   ```

4. **`audit_logs` table** - For activity tracking
   ```sql
   - id
   - user_id
   - action
   - entity_type
   - entity_id
   - details
   - timestamp
   ```

5. **`staff_members` table** - For staff management
   ```sql
   - id
   - user_id (FK to users)
   - department
   - position
   - hire_date
   - created_at, updated_at
   ```

---

## 🚦 EXECUTION ORDER

1. ✅ Create API client infrastructure
2. ✅ Update type definitions
3. ✅ Connect Dashboard (easiest to verify)
4. ✅ Connect Appointments page
5. ✅ Create Patients page
6. ✅ Connect Clinic Hours page
7. ✅ Remove unsupported features
8. ✅ Update navigation/routes
9. ✅ Test everything
10. ✅ Document what needs database tables

---

## ⚠️ IMPORTANT NOTES

1. **Appointment model changes:**
   - Frontend has: `doctorId`, `service`
   - Backend has: `patient_id`, `reason`
   - Need to map accordingly

2. **Status mapping:**
   - Frontend: `'scheduled' | 'cancelled' | 'completed'`
   - Backend: `'CONFIRMED' | 'CANCELLED' | 'RESCHEDULED' | 'COMPLETED'`
   - Map `scheduled` → `CONFIRMED`

3. **Date/Time format:**
   - Backend uses ISO8601 with timezone
   - Frontend needs to format properly

4. **Authentication:**
   - Currently using mock auth
   - Keep for now, recommend `users` table later

---

## 🎯 END RESULT

**Working Features:**
- ✅ Patient management (view, add, edit, delete)
- ✅ Appointment management (view, create, cancel, complete)
- ✅ Dashboard with real statistics
- ✅ Clinic hours management
- ✅ All data from Neon database

**Removed Features:**
- ❌ Providers/Doctors management
- ❌ Services management
- ❌ Staff management
- ❌ Audit logs
- ❌ Knowledge base
- ❌ Notifications

**Recommend Adding to Database:**
1. `users` table (authentication)
2. `services` table (service types)
3. `providers` table (optional - doctors)
4. `audit_logs` table (optional - activity tracking)

---

Ready to proceed with implementation? ✅
