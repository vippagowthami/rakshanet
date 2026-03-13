# 🧪 RakshaNet - Complete Testing Guide

## 📋 Pre-Testing Setup

### 1. Apply Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 2. Create Language Files (if not done)
```bash
mkdir locale
python manage.py makemessages -l hi -l te -l kn -l ta -l ml -l bn -l mr -l gu -l or
python manage.py compilemessages
```

### 3. Populate Initial Data
```bash
python manage.py populate_initial_data
```

### 4. Create Superuser
```bash
python manage.py createsuperuser
```

### 5. Start Development Server
```bash
python manage.py runserver
```

---

## 👥 Test User Accounts Setup

Create three test users with different roles:

### NGO Admin User
1. Go to `/register/`
2. Create user: `ngo_admin` / `testpass123`
3. Login to Django Admin (`/admin/`)
4. Set Profile role = 1 (NGO/Admin)
5. Logout and login as `ngo_admin`

### Volunteer User
1. Go to `/register/`
2. Create user: `volunteer1` / `testpass123`
3. Login to Django Admin
4. Set Profile role = 2 (Volunteer)
5. Logout and login as `volunteer1`

### Common User
1. Go to `/register/`
2. Create user: `user1` / `testpass123`
3. Profile role = 3 (Common User) - Default

---

## ✅ TESTING CHECKLIST

## 🔴 **CRISIS REQUEST CRUD (User Role)**

### ✅ CREATE Crisis Request
**URL:** `/raksha/user/requests/create/`
- [ ] Form loads correctly
- [ ] All disaster types appear in dropdown
- [ ] Location field accepts text
- [ ] GPS "Get Current Location" button works
- [ ] Latitude/Longitude auto-fill when GPS clicked
- [ ] Urgency level dropdown works (Critical, High, Medium, Low)
- [ ] Image upload works
- [ ] Description field accepts text
- [ ] Resource requirements field works
- [ ] People affected accepts numbers
- [ ] Contact number field works
- [ ] Form validates required fields
- [ ] Success message shows after creation
- [ ] Redirects to dashboard or detail page

### ✅ READ/VIEW Crisis Request
**URL:** `/raksha/user/requests/<id>/`
- [ ] Request details display correctly
- [ ] Disaster type badge shows
- [ ] Location with map marker icon displays
- [ ] Urgency level badge shows with correct color
- [ ] Status badge displays (Pending, Verified, Assigned, etc.)
- [ ] Image shows if uploaded
- [ ] Reporter name displays
- [ ] Contact number shows
- [ ] Created date/time displays
- [ ] Assigned volunteers section shows if any
- [ ] Donations section shows if any
- [ ] Verification status displays
- [ ] Edit button appears for pending/verified requests
- [ ] Delete button appears for pending/verified requests

### ✅ UPDATE/EDIT Crisis Request
**URL:** `/raksha/user/requests/<id>/edit/`
- [ ] Only owner or NGO can access
- [ ] Form pre-fills with existing data
- [ ] All fields are editable
- [ ] Can update image
- [ ] Can change urgency level
- [ ] Can modify description
- [ ] Save button updates request
- [ ] Success message appears
- [ ] Redirects to detail page
- [ ] Cannot edit if status is Completed/Cancelled

### ✅ DELETE Crisis Request
**URL:** `/raksha/user/requests/<id>/delete/`
- [ ] Only owner or NGO can access
- [ ] Confirmation page shows
- [ ] Request details display on confirmation
- [ ] Warning message appears
- [ ] Delete button confirms deletion
- [ ] Cancel button returns to list
- [ ] Success message after deletion
- [ ] Request removed from database
- [ ] Redirects to request history

### ✅ Request History
**URL:** `/raksha/user/requests/history/`
- [ ] All user's requests display
- [ ] Statistics show (Total, Pending, In Progress, Completed)
- [ ] Table shows all columns (ID, Type, Location, Status, etc.)
- [ ] Pagination works (20 per page)
- [ ] Status badges color-coded
- [ ] Urgency badges color-coded
- [ ] View button opens detail page
- [ ] Edit button appears for editable requests
- [ ] Delete button appears for pending requests
- [ ] Can filter by status
- [ ] Search works

---

## 🏢 **NGO FEATURES CRUD**

### ✅ NGO Dashboard
**URL:** `/raksha/ngo/dashboard/`
- [ ] Statistics cards show (Pending Requests, Active Volunteers, etc.)
- [ ] Recent crisis requests table displays
- [ ] Available volunteers count shows
- [ ] Active alerts display
- [ ] Quick action buttons work
- [ ] Only accessible by NGO role

### ✅ Crisis Request Verification
**URL:** `/raksha/ngo/verify/<id>/`
- [ ] Request details display
- [ ] Verify/Reject radio buttons appear
- [ ] NGO assignment dropdown works
- [ ] Notes field accepts text
- [ ] Save updates status to Verified/Rejected
- [ ] NGO gets assigned
- [ ] Notification created for reporter
- [ ] Success message appears

### ✅ SHELTER Management (Full CRUD)

#### CREATE Shelter
**URL:** `/raksha/ngo/shelters/create/`
- [ ] Form loads
- [ ] Name field works
- [ ] Disaster types (multiple selection) works
- [ ] Location field works
- [ ] GPS button auto-fills coordinates
- [ ] Capacity accepts numbers
- [ ] Current occupancy accepts numbers
- [ ] Status dropdown works (Active, Full, Inactive)
- [ ] Contact number field works
- [ ] Facilities textarea works
- [ ] Description textarea works
- [ ] Form validates required fields
- [ ] Success message after creation

#### LIST Shelters
**URL:** `/raksha/ngo/shelters/`
- [ ] All NGO's shelters display
- [ ] Table shows name, location, capacity, status
- [ ] Occupancy percentage calculated
- [ ] Edit button for each shelter
- [ ] Delete button for each shelter
- [ ] Add New Shelter button works
- [ ] Pagination works (20 per page)

#### EDIT Shelter
**URL:** `/raksha/ngo/shelters/<id>/edit/`
- [ ] Form pre-fills with existing data
- [ ] All fields editable
- [ ] Can change status
- [ ] Can update capacity
- [ ] Save updates shelter
- [ ] Last updated timestamp changes
- [ ] Success message appears

#### DELETE Shelter
**URL:** `/raksha/ngo/shelters/<id>/delete/`
- [ ] Confirmation page shows
- [ ] Shelter details display
- [ ] Warning if occupied
- [ ] Delete button removes shelter
- [ ] Cancel button returns to list
- [ ] Success message after deletion

### ✅ INVENTORY Management (Full CRUD)

#### ADD Inventory
**URL:** `/raksha/ngo/inventory/add/`
- [ ] Form loads
- [ ] Resource type dropdown works
- [ ] NGO dropdown (auto-select current NGO)
- [ ] Quantity accepts numbers
- [ ] Unit field works (kg, liters, pieces, etc.)
- [ ] Expiry date picker works
- [ ] Date picker restricts past dates
- [ ] Location field works
- [ ] Notes textarea works
- [ ] Form validates required fields
- [ ] Success message after adding

#### LIST Inventory
**URL:** `/raksha/ngo/inventory/`
- [ ] All inventory items display
- [ ] Table shows resource type, quantity, unit, expiry
- [ ] Expired items highlighted in red
- [ ] Last updated timestamp shows
- [ ] Edit button for each item
- [ ] Delete button for each item
- [ ] Add New Item button works
- [ ] Pagination works (20 per page)
- [ ] Can search by resource type
- [ ] Can filter by expiry status

#### EDIT Inventory
**URL:** `/raksha/ngo/inventory/<id>/edit/`
- [ ] Form pre-fills with existing data
- [ ] All fields editable
- [ ] Can update quantity
- [ ] Can change expiry date
- [ ] Save updates item
- [ ] Last updated timestamp changes
- [ ] Success message appears
- [ ] Delete button appears at bottom

#### DELETE Inventory
**URL:** `/raksha/ngo/inventory/<id>/delete/`
- [ ] Confirmation page shows
- [ ] Item details display
- [ ] Warning for high-quantity items
- [ ] Delete button removes item
- [ ] Cancel button returns to list
- [ ] Success message after deletion

### ✅ ALERT Management

#### CREATE Alert
**URL:** `/raksha/ngo/alerts/create/`
- [ ] Form loads
- [ ] Disaster type dropdown works
- [ ] Severity dropdown (Info, Warning, Critical, Extreme)
- [ ] Message textarea works
- [ ] Affected area field works
- [ ] Radius accepts numbers (km)
- [ ] Expiry datetime picker works
- [ ] Latitude/Longitude fields work
- [ ] Form validates required fields
- [ ] Success message after creation

#### LIST Alerts
**URL:** `/raksha/ngo/alerts/`
- [ ] All alerts display
- [ ] Table shows disaster type, severity, message
- [ ] Active alerts highlighted
- [ ] Expired alerts grayed out
- [ ] Edit button for each alert
- [ ] Deactivate button for active alerts
- [ ] Create New Alert button works
- [ ] Pagination works

#### EDIT Alert
**URL:** `/raksha/ngo/alerts/<id>/edit/`
- [ ] Form pre-fills with existing data
- [ ] All fields editable
- [ ] Can change severity
- [ ] Can extend expiry time
- [ ] Save updates alert
- [ ] Success message appears

#### DEACTIVATE Alert
**URL:** `/raksha/ngo/alerts/<id>/deactivate/`
- [ ] Alert marked as inactive
- [ ] No longer shows in public view
- [ ] Success message appears
- [ ] Can reactivate in admin

### ✅ ASSIGNMENT Creation
**URL:** `/raksha/ngo/assignments/create/`
- [ ] Form loads
- [ ] Crisis request dropdown (only verified requests)
- [ ] Volunteer dropdown (available volunteers highlighted)
- [ ] Assigned by auto-filled
- [ ] Notes textarea works
- [ ] Form validates required fields
- [ ] Assignment created
- [ ] Crisis request status changes to "Assigned"
- [ ] Notification sent to volunteer
- [ ] Success message appears

### ✅ NGO Reports
**URL:** `/raksha/ngo/reports/`
- [ ] Date range filters work
- [ ] Total requests count shows
- [ ] Completion statistics display
- [ ] People helped count shows
- [ ] Breakdown by disaster type shows
- [ ] Breakdown by urgency shows
- [ ] Volunteer statistics display
- [ ] Total donations shows
- [ ] Export button (if implemented)

### ✅ NGO Profile Setup
**URL:** `/raksha/ngo/profile-setup/`
- [ ] Form loads
- [ ] Organization name field works
- [ ] Registration number field works
- [ ] Service areas field works
- [ ] Specialization (multiple disaster types) works
- [ ] Available resources (multiple) works
- [ ] Contact number works
- [ ] Email field works
- [ ] Address textarea works
- [ ] GPS button auto-fills coordinates
- [ ] Website URL field works
- [ ] Is verified checkbox (admin only)
- [ ] Save creates/updates NGO profile
- [ ] Success message appears

---

## 🦸 **VOLUNTEER FEATURES**

### ✅ Volunteer Dashboard
**URL:** `/raksha/volunteer/dashboard/`
- [ ] Statistics cards show (Total, Pending, Completed assignments)
- [ ] Pending assignments table displays
- [ ] Hours volunteered shows
- [ ] Current rating displays
- [ ] Availability status shows
- [ ] Toggle availability button works
- [ ] Quick action buttons work
- [ ] Only accessible by Volunteer role

### ✅ Volunteer Profile Setup
**URL:** `/raksha/volunteer/profile-setup/`
- [ ] Form loads
- [ ] Primary skill dropdown works (Medical, Rescue, etc.)
- [ ] Experience years accepts numbers
- [ ] Available checkbox works
- [ ] Phone number field works
- [ ] Alternate phone field works
- [ ] Emergency contact field works
- [ ] Has vehicle checkbox works
- [ ] Vehicle type field shows when vehicle checked
- [ ] Languages spoken field works
- [ ] Certifications textarea works
- [ ] Special equipment textarea works
- [ ] Notes textarea works
- [ ] Save creates/updates profile
- [ ] Success message appears

### ✅ Assignment Details
**URL:** `/raksha/volunteer/assignment/<id>/`
- [ ] Assignment details display
- [ ] Crisis request details show
- [ ] Reporter contact displays
- [ ] NGO coordinator contact displays
- [ ] Location with Google Maps link works
- [ ] Image displays if available
- [ ] Accept button appears for pending assignments
- [ ] Update button appears for accepted/in-progress
- [ ] Status timeline displays
- [ ] Breadcrumb navigation works

### ✅ Accept Assignment
**URL:** `/raksha/volunteer/assignment/<id>/accept/`
- [ ] Assignment status changes to "Accepted"
- [ ] Notification sent to NGO
- [ ] Success message appears
- [ ] Redirects to assignment details

### ✅ Update Assignment
**URL:** `/raksha/volunteer/assignment/<id>/update/`
- [ ] Form loads
- [ ] Current assignment info displays
- [ ] Status dropdown works (Accepted, In Progress, Completed, Cancelled)
- [ ] Hours spent field appears when status = Completed
- [ ] Hours spent required for Completed status
- [ ] Notes textarea works
- [ ] Status-specific instructions show
- [ ] Progress bar updates based on status
- [ ] Save updates assignment
- [ ] Timestamps updated (started_at, completed_at)
- [ ] If Completed: volunteer stats updated
- [ ] If Completed: volunteer rating recalculated
- [ ] Success message appears

### ✅ Toggle Availability
**URL:** `/raksha/volunteer/toggle-availability/`
- [ ] AJAX request works (no page reload)
- [ ] Availability status toggles (True ↔ False)
- [ ] Dashboard updates availability badge
- [ ] Success message or notification appears

### ✅ Volunteer History
**URL:** `/raksha/volunteer/history/`
- [ ] All assignments display
- [ ] Statistics show (Total, Completed, Hours, Rating)
- [ ] Table shows all columns
- [ ] Pagination works (20 per page)
- [ ] Details button opens assignment details
- [ ] Update button appears for active assignments
- [ ] Achievement section shows for completed > 0
- [ ] Status badges color-coded

---

## 👤 **USER FEATURES**

### ✅ User Dashboard
**URL:** `/raksha/user/dashboard/`
- [ ] Statistics cards show (Total, Pending, In Progress, Completed)
- [ ] Quick actions buttons work
- [ ] Recent requests table displays (last 10)
- [ ] Active alerts section shows
- [ ] Nearby shelters section shows
- [ ] Help section with emergency numbers
- [ ] View All Requests button works

### ✅ Submit Feedback
**URL:** `/raksha/user/feedback/`
- [ ] Form loads
- [ ] Feedback type dropdown works (Service, Volunteer, NGO, System)
- [ ] Assignment dropdown appears for Service/Volunteer
- [ ] Volunteer rating stars work (clickable 1-5)
- [ ] NGO rating stars work (clickable 1-5)
- [ ] Comment textarea works
- [ ] Fields show/hide based on feedback type (JS)
- [ ] Form validates required fields
- [ ] Save creates feedback
- [ ] If volunteer rated: volunteer rating recalculated
- [ ] Success message appears

---

## 🌐 **MULTILINGUAL SUPPORT**

### ✅ Language Switching
- [ ] Language switcher appears in navbar
- [ ] All 10 languages listed (English, Hindi, Telugu, Kannada, Tamil, Malayalam, Bengali, Marathi, Gujarati, Odia)
- [ ] Clicking language changes interface language
- [ ] Current language highlighted
- [ ] Cookie/session persists language choice
- [ ] All static text translates
- [ ] Form labels translate
- [ ] Button text translates
- [ ] Error messages translate
- [ ] Database content remains in entered language

---

## 🔐 **PERMISSIONS & SECURITY**

### ✅ Role-Based Access Control
- [ ] NGO URLs blocked for non-NGO users (redirect or 403)
- [ ] Volunteer URLs blocked for non-volunteers
- [ ] User can only edit own requests
- [ ] NGO can edit any request
- [ ] Volunteer can only update own assignments
- [ ] Profile forms restricted by role
- [ ] Django admin accessible only by superusers

### ✅ Form Validation
- [ ] Required fields show error if empty
- [ ] Email format validated
- [ ] Phone number format validated
- [ ] Latitude/Longitude range validated (-90 to 90, -180 to 180)
- [ ] File upload size restricted
- [ ] Image file types restricted (jpg, png, gif)
- [ ] Expiry date must be future
- [ ] Quantity must be positive integer

---

## 📱 **RESPONSIVE DESIGN**

### ✅ Mobile Testing (resize browser to 375px width)
- [ ] Navbar collapses to hamburger menu
- [ ] Tables become scrollable or stack
- [ ] Cards stack vertically
- [ ] Forms display properly
- [ ] Buttons full-width on mobile
- [ ] Text readable without horizontal scroll
- [ ] Images scale properly

### ✅ Tablet Testing (resize to 768px width)
- [ ] Grid layouts adjust (2 columns instead of 4)
- [ ] Navigation remains functional
- [ ] All features accessible

---

## 🔔 **NOTIFICATIONS**

### ✅ Notification System
- [ ] Notification bell icon in navbar
- [ ] Unread count badge shows
- [ ] Clicking bell opens dropdown
- [ ] Recent notifications display
- [ ] Notifications created on:
  - [ ] New assignment
  - [ ] Request verified
  - [ ] Assignment accepted by volunteer
  - [ ] Assignment completed
- [ ] Mark as read functionality
- [ ] Notification links to relevant page

---

## 🔄 **API ENDPOINTS** (Optional Testing)

### ✅ REST API
Base URL: `/raksha/api/`

#### Test with Tools (Postman/curl)
- [ ] GET `/api/disasters/` - Returns disaster types
- [ ] GET `/api/resources/` - Returns resource types
- [ ] GET `/api/crisis-requests/` - Returns crisis requests (paginated)
- [ ] POST `/api/crisis-requests/` - Creates new request (with token)
- [ ] GET `/api/crisis-requests/{id}/` - Returns single request
- [ ] PUT `/api/crisis-requests/{id}/` - Updates request (with token)
- [ ] DELETE `/api/crisis-requests/{id}/` - Deletes request (with token)
- [ ] GET `/api/volunteers/` - Returns volunteers
- [ ] POST `/api/volunteers/{id}/set_available/` - Toggles availability
- [ ] GET `/api/assignments/` - Returns assignments
- [ ] POST `/api/assignments/{id}/accept/` - Accepts assignment
- [ ] POST `/api/assignments/{id}/complete/` - Completes assignment
- [ ] GET `/api/shelters/` - Returns shelters
- [ ] GET `/api/shelters/available/` - Returns only available shelters
- [ ] GET `/api/alerts/` - Returns emergency alerts
- [ ] Authentication with Token works

---

## 🐛 **ERROR HANDLING**

### ✅ Error Pages
- [ ] 404 page shows for non-existent URLs
- [ ] 403 page shows for permission denied
- [ ] 500 page shows for server errors (test in production mode)
- [ ] Form errors display inline
- [ ] Success messages show after actions
- [ ] Warning messages show for dangerous actions

---

## ⚡ **PERFORMANCE**

### ✅ Load Time
- [ ] Dashboard loads in < 2 seconds
- [ ] List pages load in < 3 seconds
- [ ] Form submissions respond in < 1 second
- [ ] Images lazy-load or optimized
- [ ] Pagination limits database queries

### ✅ Database
- [ ] No N+1 query problems
- [ ] Select_related/Prefetch_related used
- [ ] Database indexes on foreign keys
- [ ] Soft deletes (if implemented)

---

## 📊 **DATA INTEGRITY**

### ✅ Data Validation
- [ ] Cannot create assignment with cancelled request
- [ ] Cannot assign unavailable volunteer
- [ ] Shelter occupancy cannot exceed capacity
- [ ] Expired alerts don't show in public view
- [ ] Volunteer statistics accurate after completion
- [ ] Rating calculations correct (average)

---

## 🚀 **FINAL CHECKS**

### ✅ Code Quality
- [ ] No console errors in browser
- [ ] No Python errors in terminal
- [ ] All imports resolve
- [ ] No deprecated code warnings
- [ ] Static files load correctly (`python manage.py collectstatic`)

### ✅ Documentation
- [ ] README.md complete
- [ ] FEATURES.md accurate
- [ ] QUICKSTART.md helpful
- [ ] Code comments where needed
- [ ] API documentation (if applicable)

---

## 🎉 **TESTING COMPLETE!**

Once all checkboxes are ✅:
- Your RakshaNet app is fully functional
- All CRUD operations work
- Role-based features operational
- Multilingual support active
- Ready for production deployment!

---

## 📝 **BUG REPORTING TEMPLATE**

If you find issues:

**Bug Title:** [Brief description]

**Steps to Reproduce:**
1. 
2. 
3. 

**Expected Behavior:**

**Actual Behavior:**

**Error Message (if any):**

**Browser/Device:**

**User Role:**

**Screenshots (if applicable):**

---

## 🔧 **COMMON ISSUES & FIXES**

### Template Not Found
```bash
# Check template paths in settings.py
TEMPLATES[0]['DIRS'] should include templates directories
```

### Static Files Not Loading
```bash
python manage.py collectstatic
# Check STATIC_URL and STATIC_ROOT in settings.py
```

### Database Errors
```bash
python manage.py makemigrations
python manage.py migrate
# If issues persist:
python manage.py migrate --fake-initial
```

### Language Files Not Working
```bash
python manage.py compilemessages
# Ensure LocaleMiddleware in MIDDLEWARE
# Ensure 'django.template.context_processors.i18n' in context_processors
```

---

**Happy Testing! 🚀**
