# Calendar View - Quick Reference

## Visual Layout

```
┌─────────────────────────────────────────────────────────────────┐
│  Appointments Calendar                            [Month] [Week] │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  [< Prev]          January 2024              [Today]  [Next >]   │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Sun    Mon    Tue    Wed    Thu    Fri    Sat            │ │
│  ├────────────────────────────────────────────────────────────┤ │
│  │   28     29     30     31     1      2      3             │ │
│  │                              ┌─────┐                       │ │
│  │                              │ 10AM│ (Blue - Confirmed)    │ │
│  │                              └─────┘                       │ │
│  ├────────────────────────────────────────────────────────────┤ │
│  │   4      5      6      7      8      9     10             │ │
│  │         ┌─────┐        ┌─────┐                            │ │
│  │         │ 2PM │        │ 9AM │ (Green - Completed)        │ │
│  │         └─────┘        └─────┘                            │ │
│  │                        ┌─────┐                            │ │
│  │                        │ 3PM │ (Red - Cancelled)          │ │
│  │                        └─────┘                            │ │
│  ├────────────────────────────────────────────────────────────┤ │
│  │  11     12     13     14     15     16     17             │ │
│  │  ┌──────────┐                                             │ │
│  │  │   TODAY  │                                             │ │
│  │  └──────────┘                                             │ │
│  ├────────────────────────────────────────────────────────────┤ │
│  │  18     19     20     21     22     23     24             │ │
│  │         ┌─────┐                                           │ │
│  │         │ 1PM │ (Yellow - Rescheduled)                    │ │
│  │         └─────┘                                           │ │
│  │         ┌─────┐                                           │ │
│  │         │+2 more                                          │ │
│  │         └─────┘                                           │ │
│  ├────────────────────────────────────────────────────────────┤ │
│  │  25     26     27     28     29     30     31             │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                   │
│  Legend:                                                          │
│  🔵 Confirmed  🟢 Completed  🔴 Cancelled  🟡 Rescheduled       │
└─────────────────────────────────────────────────────────────────┘
```

## Component Structure

```tsx
<Card className="glass-card">
  <CardHeader>
    {/* Title and View Toggle */}
    <div className="flex justify-between">
      <CardTitle>Appointments Calendar</CardTitle>
      <div>
        <Button>Month</Button>
        <Button>Week</Button>
      </div>
    </div>
    
    {/* Navigation */}
    <div className="flex justify-between">
      <Button>← Prev</Button>
      <h3>January 2024</h3>
      <div>
        <Button>Today</Button>
        <Button>Next →</Button>
      </div>
    </div>
  </CardHeader>

  <CardContent>
    {/* Calendar Grid */}
    <div className="grid grid-cols-7">
      {/* Day Headers */}
      <div>Sun</div> ... <div>Sat</div>
      
      {/* Date Cells */}
      {days.map(day => (
        <div onClick={() => onDateClick(day.date)}>
          <div>{day.number}</div>
          
          {/* Appointments */}
          {day.appointments.map(apt => (
            <div onClick={() => onAppointmentClick(apt)}>
              {apt.patient_name} - {apt.time}
            </div>
          ))}
        </div>
      ))}
    </div>
    
    {/* Status Legend */}
    <div className="flex gap-4">
      <Badge>🔵 Confirmed</Badge>
      <Badge>🟢 Completed</Badge>
      <Badge>🔴 Cancelled</Badge>
      <Badge>🟡 Rescheduled</Badge>
    </div>
  </CardContent>
</Card>
```

## Color Coding

| Status | Background | Border | Text |
|--------|-----------|--------|------|
| **Confirmed** | `bg-blue-500/20` | `border-blue-500/30` | Blue text |
| **Completed** | `bg-green-500/20` | `border-green-500/30` | Green text |
| **Cancelled** | `bg-red-500/20` | `border-red-500/30` | Red text |
| **Rescheduled** | `bg-yellow-500/20` | `border-yellow-500/30` | Yellow text |

## States

### Current Date
```tsx
className="border-2 border-primary/50 bg-primary/5"
```

### Other Month Dates
```tsx
className="text-muted-foreground/40"
```

### Hover Effects
```tsx
className="hover:bg-accent/10 cursor-pointer transition-colors"
```

## Usage in Dashboards

### Admin Dashboard
```tsx
// Located between Stats Grid and Today's Appointments
<div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
  {/* Stats Cards */}
</div>

<CalendarView 
  onDateClick={(date) => navigate('/admin/appointments')}
  onAppointmentClick={(apt) => navigate('/admin/appointments')}
/>

<div className="grid gap-6 lg:grid-cols-2">
  {/* Today's Appointments & Statistics */}
</div>
```

### Staff Dashboard
```tsx
// Located between Stats Grid and Today's Schedule
<div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
  {/* Stats Cards */}
</div>

<CalendarView 
  onDateClick={(date) => navigate('/staff/appointments')}
  onAppointmentClick={(apt) => navigate('/staff/appointments')}
/>

<Card>
  {/* Today's Schedule */}
</Card>
```

## Interactions

### Click on Empty Date
1. User clicks on date cell (e.g., January 15)
2. `handleDateClick` function fires
3. Navigates to appointments page
4. (Future) Can pre-fill date in appointment creation form

### Click on Appointment
1. User clicks on appointment block
2. `handleAppointmentClick` function fires
3. Navigates to appointments page
4. (Future) Can pre-select appointment for editing

### Toggle Month/Week
1. User clicks Month/Week button
2. State updates: `setView('month')` or `setView('week')`
3. Calendar re-renders with new view
4. Date range recalculates

### Navigate Prev/Next
1. User clicks Prev/Next button
2. Current date updates (1 month or 1 week)
3. Calendar re-renders
4. Appointments reload for new date range

### Go to Today
1. User clicks Today button
2. Current date sets to `new Date()`
3. Calendar scrolls to current month/week
4. Current date highlighted

## Responsive Behavior

### Desktop (≥1024px)
- Full 7-column grid
- Spacious day cells
- 2+ appointments visible per day
- Full navigation controls

### Tablet (768px - 1023px)
- 7-column grid (slightly compressed)
- Smaller day cells
- 1-2 appointments visible
- Compact navigation

### Mobile (<768px)
- Week view recommended
- Scrollable horizontal calendar
- Single appointment per day visible
- Minimal navigation controls

## Performance

### Optimization Techniques
1. **Memoization**: Use `useMemo` for date calculations
2. **Virtual Scrolling**: Only render visible dates
3. **Debounced API Calls**: Limit appointment refetching
4. **Lazy Loading**: Load appointments on demand

### Data Flow
```
1. Component mounts
   ↓
2. Calculate date range (month/week)
   ↓
3. Fetch appointments from API
   ↓
4. Group appointments by date
   ↓
5. Render calendar grid
   ↓
6. User interaction (click/navigate)
   ↓
7. Update state → Re-render
```

## Accessibility

- ✅ Keyboard navigation support
- ✅ ARIA labels for screen readers
- ✅ Focus indicators on interactive elements
- ✅ High contrast color combinations
- ✅ Semantic HTML structure

## Browser Support

- ✅ Chrome/Edge (latest)
- ✅ Firefox (latest)
- ✅ Safari (latest)
- ✅ Mobile browsers (iOS Safari, Chrome Mobile)
