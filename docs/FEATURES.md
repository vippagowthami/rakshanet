# RakshaNet - Enhanced Multilingual Disaster Management System

## 🌟 New Features Added

### 1. **Multilanguage Support (10 Languages)**
- English
- Hindi (हिन्दी)
- Telugu (తెలుగు)
- Kannada (ಕನ್ನಡ)
- Tamil (தமிழ்)
- Malayalam (മലയാളം)
- Bengali (বাংলা)
- Marathi (मराठी)
- Gujarati (ગુજરાતી)
- Odia (ଓଡ଼ିଆ)

**Features:**
- Language switcher in every page
- Session-based language persistence
- Translatable content using Django i18n
- Indian timezone support

### 2. **Role-Based Features**

#### 🏢 **NGO/Admin Features**
- **NGO Dashboard** (`/raksha/ngo/dashboard/`)
  - View all assigned crisis requests
  - Statistics: Total, Pending, In Progress, Completed
  - Quick actions panel
  - Resource inventory management
  - Volunteer management
  - Donations tracking

- **NGO-Specific Functions:**
  - Create and broadcast emergency alerts
  - Verify crisis requests
  - Manage volunteers
  - Manage emergency shelters
  - Track resource inventory
  - View donations received

#### 🦺 **Volunteer Features**
- **Volunteer Dashboard** (`/raksha/volunteer/dashboard/`)
  - View assigned tasks
  - Accept/reject assignments
  - Update task status (pending → in progress → completed)
  - Toggle availability status
  - Track completed hours and rating
  - View nearby crisis requests
  - Emergency alerts feed

- **Volunteer Profile:**
  - Skills tracking (Medical, Rescue, Logistics, etc.)
  - Vehicle availability
  - Languages spoken
  - Emergency contact
  - Certifications
  - Performance metrics (rating, hours, tasks completed)

#### 👥 **User/People Features**
- **User Dashboard** (`/raksha/user/dashboard/`)
  - Create crisis requests
  - Track request status
  - View active emergency alerts
  - Find nearby shelters
  - Access safety tips
  - View help status

- **Crisis Request Creation:**
  - Upload images/videos
  - Geolocation support
  - Disaster type selection
  - Resource requirements
  - Number of people affected

### 3. **Disaster Management Models**

#### 📋 **DisasterType**
- Natural disasters (Flood, Earthquake, Cyclone, etc.)
- Man-made disasters
- Health emergencies
- Conflict/war situations
- Severity multiplier for priority calculation

#### 🏪 **ResourceType**
- Food & Water
- Medical Supplies
- Shelter & Clothing
- Rescue Equipment
- Communication Tools
- Transportation
- Financial Aid

#### 🏢 **NGOProfile**
- Organization details
- Registration number
- Service areas
- Specialization (disaster types)
- Available resources
- Verification status
- Contact information

#### 🏠 **Shelter**
- Location with coordinates
- Capacity tracking
- Current occupancy
- Managed by NGO
- Facilities list
- Status (active/full/inactive)
- Disaster type support

#### 🚨 **EmergencyAlert**
- Alert title and message
- Severity levels (Info, Warning, Critical, Extreme)
- Affected area
- Radius-based targeting
- Disaster type
- Expiry time
- Issued by NGO/Admin

#### 📦 **ResourceInventory**
- Track available resources at NGOs
- Quantity and unit tracking
- Location information
- Expiry date tracking
- Updated by authorized users

#### 🔔 **Notification**
- Real-time notifications
- Types: Alert, Assignment, Request Update, Donation, System
- Read/unread status
- Link to related pages
- Auto-refresh every 30 seconds

#### ⭐ **Feedback**
- Rate volunteers (1-5 stars)
- Rate NGOs
- System feedback
- Comments and suggestions

#### 📞 **EmergencyContact**
- Area-wise emergency numbers
- Service types (Police, Ambulance, Fire, etc.)
- 24/7 availability status
- Languages supported

#### 💡 **SafetyTip**
- Disaster-specific safety guidelines
- Multilingual support
- Priority-based display
- Active/inactive status

### 4. **Enhanced Crisis Request System**
- Multiple status levels: Submitted → Verified → Approved → Allocated → In Progress → Delivered → Completed
- Disaster type classification
- Priority score calculation
- Image/video upload support
- People affected count
- NGO assignment
- Internal notes for tracking
- Verification by NGO

### 5. **API Endpoints**

All API endpoints available at `/raksha/api/`:

```
GET /raksha/api/disaster-types/           # List disaster types
GET /raksha/api/resource-types/           # List resource types
GET /raksha/api/ngos/                     # List NGO profiles
GET /raksha/api/shelters/                 # List shelters
GET /raksha/api/shelters/available/       # Available shelters only
GET /raksha/api/alerts/                   # Emergency alerts
GET /raksha/api/requests/                 # Crisis requests
GET /raksha/api/requests/my_requests/     # User's own requests
POST /raksha/api/requests/{id}/verify/    # Verify request (NGO only)
GET /raksha/api/volunteers/               # Volunteer profiles
GET /raksha/api/volunteers/available/     # Available volunteers
POST /raksha/api/volunteers/{id}/set_available/  # Toggle availability
GET /raksha/api/assignments/              # Assignments
POST /raksha/api/assignments/{id}/accept/ # Accept assignment
POST /raksha/api/assignments/{id}/complete/ # Complete assignment
GET /raksha/api/donations/                # Donations
GET /raksha/api/inventory/                # Resource inventory
GET /raksha/api/notifications/            # Notifications
GET /raksha/api/notifications/unread/     # Unread notifications
POST /raksha/api/notifications/{id}/mark_read/  # Mark as read
GET /raksha/api/feedback/                 # Feedback
GET /raksha/api/safety-tips/              # Safety tips
```

### 6. **User-Friendly Features**

- **Responsive Design**: Works on mobile, tablet, and desktop
- **Real-time Updates**: Notifications refresh automatically
- **Search & Filter**: All API endpoints support search and filtering
- **Geolocation**: Map integration for location-based features
- **Image Upload**: Support for crisis documentation
- **Role Badges**: Visual indicators for user roles
- **Quick Actions**: One-click access to common tasks
- **Emergency Helpline**: Displayed in footer (112)

### 7. **Scalability Features**

- **REST API**: Full RESTful API for mobile app integration
- **Token Authentication**: Secure API access
- **Pagination**: All list endpoints support pagination
- **Caching**: Session-based language caching
- **Database Optimization**: Indexed fields and select_related queries
- **Modular Design**: Separate apps for different functionalities

## 🚀 Installation & Setup

### 1. **Install Dependencies**

```bash
pip install -r requirements.txt
```

### 2. **Make Migrations**

```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. **Create Locale Directories**

```bash
mkdir locale
python manage.py makemessages -l hi
python manage.py makemessages -l te
python manage.py makemessages -l kn
python manage.py makemessages -l ta
python manage.py makemessages -l ml
python manage.py makemessages -l bn
python manage.py makemessages -l mr
python manage.py makemessages -l gu
python manage.py makemessages -l or
```

### 4. **Compile Messages**

```bash
python manage.py compilemessages
```

### 5. **Create Superuser**

```bash
python manage.py createsuperuser
```

### 6. **Load Initial Data (Optional)**

Create initial disaster types and resources in Django admin.

### 7. **Run Server**

```bash
python manage.py runserver
```

## 📱 Usage Guide

### For NGOs:
1. Register with role "Admin or NGO"
2. Complete NGO profile in admin panel
3. Access NGO dashboard at `/raksha/ngo/dashboard/`
4. Verify crisis requests
5. Manage volunteers and resources
6. Create emergency alerts

### For Volunteers:
1. Register with role "Volunteer"
2. Complete volunteer profile
3. Access volunteer dashboard at `/raksha/volunteer/dashboard/`
4. Accept assignments
5. Update task progress
6. Toggle availability

### For Users/People:
1. Register with role "Common User"
2. Access user dashboard at `/raksha/user/dashboard/`
3. Create crisis requests
4. Track request status
5. View emergency alerts and shelters
6. Access safety tips

## 🔧 Admin Configuration

### Important Setup in Admin Panel:

1. **Disaster Types**: Add common disasters (Flood, Earthquake, Cyclone, Fire, etc.)
2. **Resource Types**: Add resources (Food, Water, Medical, etc.)
3. **NGO Profiles**: Create/verify NGO profiles
4. **Shelters**: Add emergency shelter locations
5. **Emergency Contacts**: Add area-wise emergency numbers
6. **Safety Tips**: Add disaster-specific safety guidelines

## 🌐 API Integration

### Get API Token:
```bash
POST /api-token-auth/
{
    "username": "your_username",
    "password": "your_password"
}
```

### Use Token in Requests:
```bash
Authorization: Token your_token_here
```

## 📊 Database Schema

- **DisasterType**: Disaster classifications
- **ResourceType**: Resource categories
- **NGOProfile**: Extended NGO information
- **VolunteerProfile**: Extended volunteer information
- **CrisisRequest**: Emergency help requests
- **Assignment**: Volunteer task assignments
- **Shelter**: Emergency shelter locations
- **EmergencyAlert**: Broadcast alerts
- **ResourceInventory**: NGO resource tracking
- **Notification**: User notifications
- **Feedback**: Ratings and reviews
- **EmergencyContact**: Important phone numbers
- **SafetyTip**: Disaster safety guidelines

## 🔐 Security Features

- Role-based access control
- Token-based API authentication
- CSRF protection
- Permission classes for API endpoints
- Verified NGO system

## 📈 Future Enhancements

- SMS/Email notifications integration
- Push notifications for mobile apps
- Real-time chat between volunteers and NGOs
- Weather API integration
- Advanced geospatial queries
- Machine learning for priority scoring
- Offline mode support
- QR code for quick registration
- Blockchain for donation transparency

## 🤝 Contributing

This is a disaster management system. Contributions for improvements are welcome!

## 📄 License

See LICENSE file for details.

## 🆘 Emergency Helpline

**National Emergency Number (India): 112**

---

**Built with ❤️ for disaster relief and humanitarian aid**
