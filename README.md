# 🛡️ RakshaNet - Intelligent Crisis Protection Network

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Django](https://img.shields.io/badge/Django-4.2.8-green.svg)](https://www.djangoproject.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Live Demo](https://img.shields.io/badge/Live%20Demo-RakshaNet-success)](https://rakshanet.onrender.com)

**RakshaNet** is an intelligent disaster management and crisis protection platform designed to connect disaster-affected people with NGOs and volunteers for rapid response and resource allocation.

## Live Deployment

- Permanent link: https://rakshanet.onrender.com

## 🌟 Key Features

### For All Users
- 🤖 **AI-Powered Priority Scoring** - Automatic urgency detection and crisis prioritization
- 💬 **Real-time Crisis Chat** - Coordinate response efforts with multi-party communication
- 📍 **Location-based Services** - Geolocation support for proximity matching
- 🌐 **Multi-language Support** - Interface available in 10+ Indian languages
- 🗺️ **Interactive Map Dashboard** - Visual crisis tracking with Leaflet maps
- 📱 **Responsive Design** - Mobile-friendly interface for field operations

### Role-Specific Features

#### 👥 Common Users (Affected People)
- Submit crisis requests with urgency levels
- Track request status and responses
- View AI-suggested resources for their situation
- Access priority insights dashboard

#### 🏛️ NGOs/Admins
- Manage crisis requests and assign volunteers
- AI-powered resource allocation recommendations
- Inventory management system
- Volunteer assignment workflow
- Operational insights dashboard

#### 🙋 Volunteers
- View and accept nearby crisis assignments
- Location-based request suggestions
- Assignment history tracking
- AI fit score for optimal task matching
- Profile management with skills and availability

## 🚀 Quick Start

See [QUICKSTART.md](QUICKSTART.md) for detailed setup instructions.

### Basic Setup
```bash
# Clone the repository
git clone https://github.com/yourusername/RakshaNet.git
cd RakshaNet

# Navigate to Django project
cd RakshaNet

# Install dependencies
pip install -r requirements.txt

# Setup database
python manage.py migrate

# Populate initial data (disaster types, resources, etc.)
python manage.py populate_initial_data

# Create admin user
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

Visit `http://localhost:8000` for local development or https://rakshanet.onrender.com for the live deployment.

## 📁 Project Structure

```
RakshaNet/
├── RakshaNet/                  # Django project directory
│   ├── blog/                   # Blog application
│   ├── raksha/                 # Main crisis management app
│   │   ├── models.py          # Database models
│   │   ├── views.py           # View logic
│   │   ├── role_views.py      # Role-specific dashboards
│   │   ├── utils.py           # AI utilities
│   │   ├── templates/         # HTML templates
│   │   └── api/               # REST API endpoints
│   ├── users/                 # User management
│   ├── django_start/          # Project settings
│   ├── media/                 # User uploads
│   ├── staticfiles/           # Static assets
│   └── manage.py              # Django management script
├── docs/                       # Documentation
├── Dockerfile                  # Docker configuration
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## 🧠 AI Features

RakshaNet includes intelligent features powered by rule-based AI:

- **Urgency Inference** - Analyzes crisis descriptions to automatically determine urgency levels
- **Resource Matching** - Suggests appropriate resources based on crisis type and description
- **Proximity Scoring** - Matches volunteers with nearby requests based on location
- **Priority Ranking** - Scores and ranks crisis requests for optimal response allocation
- **Operational Insights** - Provides dashboards with AI-generated recommendations

## 🛠️ Technology Stack

- **Backend**: Django 4.2.8, Django REST Framework
- **Database**: SQLite (development), PostgreSQL (production ready)
- **Frontend**: Bootstrap 4, JavaScript, Leaflet.js
- **Forms**: Django Crispy Forms with Bootstrap 4
- **Authentication**: Django built-in auth system
- **API**: RESTful API with DRF

## 📚 Documentation

Comprehensive documentation is available in the [docs/](docs/) directory:

- [Features Overview](docs/FEATURES.md)
- [Testing Guide](docs/TESTING_GUIDE.md)
- [Deployment Checklist](docs/DEPLOYMENT_CHECKLIST.md)
- [Quick Reference Guide](docs/QUICK_REFERENCE_GUIDE.md)
- [Deployment Guide](docs/DEPLOY.md)

## 🧪 Running Tests

```bash
python manage.py test
```

## 🚢 Deployment

The application can be deployed using:

- **Docker**: Use the included `Dockerfile`
- **Heroku**: Use the `Procfile` for configuration
- **Render**: Use `render.yaml` for automatic deployment

See [docs/DEPLOYMENT_CHECKLIST.md](docs/DEPLOYMENT_CHECKLIST.md) for detailed deployment instructions.

## 🔒 Security Considerations

- Never commit `db.sqlite3`, `.env`, or sensitive files
- Use environment variables for production secrets
- Update `SECRET_KEY` and `DEBUG=False` in production
- Configure `ALLOWED_HOSTS` appropriately
- Use HTTPS for production deployments

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](RakshaNet/LICENSE) file for details.

## 👥 Authors

- **Development Team** - RakshaNet Project

## 🙏 Acknowledgments

- Django community for excellent documentation
- Bootstrap for responsive UI components
- Leaflet.js for mapping capabilities
- All contributors and testers

## 📞 Support

For issues and questions:
- Create an issue on GitHub
- Check documentation in the `docs/` folder
- Review the [Quick Start Guide](QUICKSTART.md)

---

**Built with ❤️ for crisis response and disaster management**
