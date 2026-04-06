# RakshaNet - Quick Start Guide

## 🌐 Live Deployment

**Production URL:** https://rakshanet-bfr0.onrender.com

For local development, follow the steps below.

## 🚀 Quick Setup (5 Minutes)

### Step 1: Install Dependencies
```bash
cd RakshaNet
pip install -r requirements.txt
```

### Step 2: Database Setup
```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 3: Populate Initial Data
```bash
python manage.py populate_initial_data
```
This will create:
- 15 Disaster Types (Flood, Earthquake, Cyclone, etc.)
- 25 Resource Types (Water, Food, Medical supplies, etc.)
- 10 Emergency Contact Numbers

### Step 4: Create Superuser
```bash
python manage.py createsuperuser
```
Enter username, email, and password.

### Step 5: Create Locale Directories (For Translations)
```bash
# Create locale directory in project root
cd RakshaNet
mkdir locale

# Generate translation files for all languages
python manage.py makemessages -l hi
python manage.py makemessages -l te
python manage.py makemessages -l kn
python manage.py makemessages -l ta
python manage.py makemessages -l ml
python manage.py makemessages -l bn
python manage.py makemessages -l mr
python manage.py makemessages -l gu
python manage.py makemessages -l or

# Compile messages
python manage.py compilemessages
```

### Step 6: Run Server
```bash
python manage.py runserver
```

Visit: http://127.0.0.1:8000/

## 📋 Initial Configuration in Admin Panel

### 1. Access Admin Panel
Go to: http://127.0.0.1:8000/admin/
Login with superuser credentials

### 2. Create NGO Profile
- Navigate to **Raksha → NGO Profiles**
- Click **Add NGO Profile**
- Fill in organization details
- Select specialization (disaster types)
- Mark as **Verified** and **Active**

### 3. Add Shelters
- Navigate to **Raksha → Shelters**
- Add emergency shelter locations with:
  - Name, address
  - Capacity
  - Coordinates (optional)
  - Managed by (select NGO)
  - Facilities
  - Status: Active

### 4. Add Safety Tips
- Navigate to **Raksha → Safety Tips**
- Create safety guidelines for each disaster type
- Set priority (higher = more important)
- Mark as active

## 👥 Testing Different Roles

### Create Test Users:

#### 1. NGO User
```
URL: /register/
Username: test_ngo
Email: ngo@example.com
Role: Admin or NGO
```
After registration:
- Login as superuser in admin
- Create NGOProfile for this user
- Set user's Profile role to 1 (NGO)

#### 2. Volunteer User
```
URL: /register/
Username: test_volunteer
Email: volunteer@example.com
Role: Volunteer
```
After registration:
- Login as this user
- Complete volunteer profile with skills

#### 3. Regular User
```
URL: /register/
Username: test_user
Email: user@example.com
Role: Common User (Need Help)
```

## 🎯 Test Each Dashboard

### NGO Dashboard
```
Login as NGO user
Visit: /raksha/ngo/dashboard/
Test:
- Create emergency alert
- Verify crisis requests
- Manage volunteers
- Check inventory
```

### Volunteer Dashboard
```
Login as volunteer user
Visit: /raksha/volunteer/dashboard/
Test:
- Accept assignments
- Update task status
- Toggle availability
```

### User Dashboard
```
Login as regular user
Visit: /raksha/user/dashboard/
Test:
- Create crisis request
- View emergency alerts
- Find shelters
- Read safety tips
```

## 🌐 Test Multilanguage

1. Look for language dropdown (top-right corner)
2. Select different languages
3. All interface text should change
4. Language preference is saved in session

## 🔌 Test API Endpoints

### Get API Token
```bash
curl -X POST http://127.0.0.1:8000/api-token-auth/ \
  -H "Content-Type: application/json" \
  -d '{"username":"your_username","password":"your_password"}'
```

### List Crisis Requests
```bash
curl http://127.0.0.1:8000/raksha/api/requests/ \
  -H "Authorization: Token YOUR_TOKEN"
```

### Create Crisis Request
```bash
curl -X POST http://127.0.0.1:8000/raksha/api/requests/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Request",
    "phone": "1234567890",
    "description": "Need immediate help",
    "address": "Test Address",
    "urgency": "high",
    "people_affected": 5
  }'
```

## 📱 Available URLs

### Public URLs
- `/` - Home
- `/register/` - User registration
- `/login/` - Login
- `/contact/` - Contact form

### Role-Based Dashboards
- `/raksha/ngo/dashboard/` - NGO Dashboard
- `/raksha/volunteer/dashboard/` - Volunteer Dashboard
- `/raksha/user/dashboard/` - User Dashboard

### Common Features
- `/raksha/alerts/` - Emergency alerts
- `/raksha/shelters/` - Emergency shelters
- `/raksha/safety-tips/` - Safety tips
- `/raksha/notifications/` - Notifications
- `/profile/` - User profile

### API Base
- `/raksha/api/` - All API endpoints
- `/api-token-auth/` - Get API token
- `/api/schema/` - API schema

## 🐛 Troubleshooting

### Issue: Migrations fail
```bash
# Delete db.sqlite3 and __pycache__ folders
python manage.py makemigrations --empty raksha
python manage.py makemigrations
python manage.py migrate
```

### Issue: Templates not found
```bash
# Ensure template directories exist
mkdir -p raksha/templates/raksha
```

### Issue: Static files not loading
```bash
python manage.py collectstatic
```

### Issue: Translations not working
```bash
# Recompile messages
python manage.py compilemessages
# Restart server
```

## 📊 Key Features Summary

✅ **10 Languages** - English, Hindi, Telugu, Kannada, Tamil, Malayalam, Bengali, Marathi, Gujarati, Odia
✅ **3 User Roles** - NGO/Admin, Volunteer, Regular User
✅ **15+ Disaster Types** - Comprehensive disaster classification
✅ **25+ Resource Types** - From food to medical to transport
✅ **Emergency Alerts** - Broadcast system for active threats
✅ **Shelter Management** - Track capacity and availability
✅ **Assignment System** - Match volunteers to crisis requests
✅ **Inventory Tracking** - NGO resource management
✅ **Notifications** - Real-time updates
✅ **Safety Tips** - Disaster-specific guidelines
✅ **RESTful API** - Full API for mobile apps
✅ **Geolocation** - Location-based features
✅ **Rating System** - Feedback for volunteers and NGOs

## 🎉 You're Ready!

Your RakshaNet disaster management system is now fully configured with:
- Multilingual support
- Role-based dashboards
- Complete disaster management features
- API for mobile integration

**Next**: Start creating real crisis requests, managing volunteers, and helping people! 🚀

## 📞 Emergency Numbers (India)

- **National Emergency**: 112
- **Police**: 100
- **Fire**: 101
- **Ambulance**: 102
- **Disaster Management**: 108

---

**Stay Safe, Help Others! 🙏**
