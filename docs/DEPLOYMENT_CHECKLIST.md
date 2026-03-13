# 🚀 DEPLOYMENT CHECKLIST - RakshaNet

## 📋 Pre-Deployment Steps

### ✅ 1. Environment Setup
- [ ] Python 3.8+ installed
- [ ] Virtual environment created and activated
- [ ] All dependencies installed (`pip install -r requirements.txt`)
- [ ] PostgreSQL database setup (for production)
- [ ] Environment variables configured

### ✅ 2. Django Settings Configuration

#### Production Settings (`settings.py`)
```python
# Security
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com', 'your-server-ip']
SECRET_KEY = os.environ.get('SECRET_KEY')  # Use environment variable

# Database (PostgreSQL recommended)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

# Static and Media Files
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Security Headers
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
```

### ✅ 3. Database Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### ✅ 4. Static Files Collection
```bash
python manage.py collectstatic --noinput
```

### ✅ 5. Create Superuser
```bash
python manage.py createsuperuser
```

### ✅ 6. Populate Initial Data
```bash
python manage.py populate_initial_data
```

### ✅ 7. Compile Message Files (for multilingual support)
```bash
python manage.py compilemessages
```

---

## 🖥️ Server Setup

### Option 1: Deploy on Heroku

#### Steps:
1. **Install Heroku CLI**
   ```bash
   # Windows
   # Download from https://devcenter.heroku.com/articles/heroku-cli
   ```

2. **Create Heroku App**
   ```bash
   heroku login
   heroku create rakshanet-app
   ```

3. **Add PostgreSQL**
   ```bash
   heroku addons:create heroku-postgresql:hobby-dev
   ```

4. **Set Environment Variables**
   ```bash
   heroku config:set SECRET_KEY=your-secret-key
   heroku config:set DEBUG=False
   heroku config:set ALLOWED_HOSTS=rakshanet-app.herokuapp.com
   ```

5. **Deploy**
   ```bash
   git push heroku main
   heroku run python manage.py migrate
   heroku run python manage.py createsuperuser
   heroku run python manage.py populate_initial_data
   heroku run python manage.py compilemessages
   ```

6. **Open App**
   ```bash
   heroku open
   ```

### Option 2: Deploy on Render.com

#### Steps:
1. **Create account on Render.com**

2. **Create Web Service**
   - Connect GitHub repository
   - Select branch: `main`
   - Build Command: `pip install -r requirements.txt; python manage.py collectstatic --noinput; python manage.py migrate`
   - Start Command: `gunicorn django_start.wsgi:application`

3. **Add PostgreSQL Database**
   - Create PostgreSQL instance
   - Copy DATABASE_URL

4. **Set Environment Variables**
   - `SECRET_KEY`: Your secret key
   - `DEBUG`: False
   - `ALLOWED_HOSTS`: your-app.onrender.com
   - `DATABASE_URL`: PostgreSQL connection string

5. **Deploy**
   - Click "Manual Deploy" or push to GitHub

### Option 3: VPS (DigitalOcean/AWS/Linode)

#### Steps:
1. **Setup Server (Ubuntu 20.04/22.04)**
   ```bash
   sudo apt update
   sudo apt upgrade -y
   sudo apt install python3-pip python3-dev libpq-dev postgresql postgresql-contrib nginx curl
   ```

2. **Install PostgreSQL**
   ```bash
   sudo -u postgres psql
   CREATE DATABASE rakshanet;
   CREATE USER rakshanet_user WITH PASSWORD 'your_password';
   ALTER ROLE rakshanet_user SET client_encoding TO 'utf8';
   ALTER ROLE rakshanet_user SET default_transaction_isolation TO 'read committed';
   ALTER ROLE rakshanet_user SET timezone TO 'Asia/Kolkata';
   GRANT ALL PRIVILEGES ON DATABASE rakshanet TO rakshanet_user;
   \q
   ```

3. **Setup Virtual Environment**
   ```bash
   cd /var/www
   sudo mkdir rakshanet
   cd rakshanet
   sudo python3 -m venv venv
   source venv/bin/activate
   ```

4. **Clone and Install**
   ```bash
   git clone https://github.com/yourusername/RakshaNet.git
   cd RakshaNet
   pip install -r requirements.txt
   pip install gunicorn
   ```

5. **Configure Gunicorn**
   Create `/etc/systemd/system/rakshanet.service`:
   ```ini
   [Unit]
   Description=RakshaNet Django App
   After=network.target

   [Service]
   User=www-data
   Group=www-data
   WorkingDirectory=/var/www/rakshanet/RakshaNet
   ExecStart=/var/www/rakshanet/venv/bin/gunicorn --workers 3 --bind unix:/var/www/rakshanet/rakshanet.sock django_start.wsgi:application

   [Install]
   WantedBy=multi-user.target
   ```

6. **Start Gunicorn**
   ```bash
   sudo systemctl start rakshanet
   sudo systemctl enable rakshanet
   sudo systemctl status rakshanet
   ```

7. **Configure Nginx**
   Create `/etc/nginx/sites-available/rakshanet`:
   ```nginx
   server {
       listen 80;
       server_name yourdomain.com www.yourdomain.com;

       location = /favicon.ico { access_log off; log_not_found off; }
       
       location /static/ {
           alias /var/www/rakshanet/RakshaNet/staticfiles/;
       }
       
       location /media/ {
           alias /var/www/rakshanet/RakshaNet/media/;
       }

       location / {
           include proxy_params;
           proxy_pass http://unix:/var/www/rakshanet/rakshanet.sock;
       }
   }
   ```

8. **Enable Site**
   ```bash
   sudo ln -s /etc/nginx/sites-available/rakshanet /etc/nginx/sites-enabled
   sudo nginx -t
   sudo systemctl reload nginx
   ```

9. **Setup SSL with Let's Encrypt**
   ```bash
   sudo apt install certbot python3-certbot-nginx
   sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
   ```

---

## 🔐 Security Checklist

### ✅ Essential Security Steps
- [ ] `DEBUG = False` in production
- [ ] Strong `SECRET_KEY` (use environment variable)
- [ ] `ALLOWED_HOSTS` configured correctly
- [ ] SSL/HTTPS enabled
- [ ] `SECURE_SSL_REDIRECT = True`
- [ ] `SESSION_COOKIE_SECURE = True`
- [ ] `CSRF_COOKIE_SECURE = True`
- [ ] Database password strong and secure
- [ ] Remove `.env` file from version control (add to `.gitignore`)
- [ ] Limit file upload size in nginx/web server
- [ ] Rate limiting enabled (Django Ratelimit or nginx)
- [ ] CORS headers configured if API used externally
- [ ] Admin URL changed from `/admin/` to custom path
- [ ] Regular security updates

---

## 📊 Monitoring & Maintenance

### ✅ Setup Monitoring
- [ ] Setup logging (Sentry, Loggly, Papertrail)
- [ ] Monitor server resources (CPU, RAM, Disk)
- [ ] Database backup schedule (daily/weekly)
- [ ] Uptime monitoring (UptimeRobot, Pingdom)
- [ ] Error tracking (Sentry.io)
- [ ] Analytics (Google Analytics, Matomo)

### Logging Configuration (`settings.py`)
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': '/var/log/rakshanet/django.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}
```

### Backup Strategy
```bash
# PostgreSQL Database Backup
pg_dump rakshanet > backup_$(date +%Y%m%d_%H%M%S).sql

# Automated Daily Backup (cron job)
0 2 * * * pg_dump rakshanet > /backups/rakshanet_$(date +\%Y\%m\%d).sql
```

---

## 🧹 Post-Deployment Cleanup

### ✅ Final Checks
- [ ] Test all CRUD operations
- [ ] Test role-based permissions
- [ ] Test form validations
- [ ] Test file uploads
- [ ] Test multilingual switching
- [ ] Test on mobile devices
- [ ] Test in different browsers (Chrome, Firefox, Safari, Edge)
- [ ] Check all links work
- [ ] Verify email notifications (if configured)
- [ ] Verify SMS notifications (if configured)
- [ ] Check API endpoints (if exposed)
- [ ] Load testing (Apache JMeter, Locust)
- [ ] Security scan (OWASP ZAP)

---

## 📱 Optional Enhancements

### ✅ Advanced Features to Add Later
- [ ] Email verification for user registration
- [ ] Password reset via email
- [ ] SMS alerts for emergency notifications (Twilio, AWS SNS)
- [ ] Push notifications (Firebase Cloud Messaging)
- [ ] Real-time chat (Django Channels, WebSocket)
- [ ] Google Maps integration for geolocation
- [ ] Payment gateway for donations (Razorpay, Stripe, PayPal)
- [ ] PDF report generation (ReportLab, WeasyPrint)
- [ ] Excel export for data (openpyxl, xlsxwriter)
- [ ] Advanced search with Elasticsearch
- [ ] Mobile app (React Native, Flutter)
- [ ] Progressive Web App (PWA)
- [ ] Two-factor authentication (2FA)
- [ ] Social login (Google, Facebook)

---

## 🐳 Docker Deployment (Optional)

### Create `Dockerfile`
```dockerfile
FROM python:3.9-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "django_start.wsgi:application"]
```

### Create `docker-compose.yml`
```yaml
version: '3.8'

services:
  db:
    image: postgres:13
    environment:
      POSTGRES_DB: rakshanet
      POSTGRES_USER: rakshanet_user
      POSTGRES_PASSWORD: your_password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  web:
    build: .
    command: gunicorn django_start.wsgi:application --bind 0.0.0.0:8000
    volumes:
      - .:/app
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    ports:
      - "8000:8000"
    depends_on:
      - db
    environment:
      - DEBUG=False
      - SECRET_KEY=your-secret-key
      - DATABASE_URL=postgresql://rakshanet_user:your_password@db:5432/rakshanet

volumes:
  postgres_data:
  static_volume:
  media_volume:
```

### Deploy with Docker
```bash
docker-compose up -d
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py populate_initial_data
```

---

## 📞 Support & Troubleshooting

### Common Deployment Issues

**Issue 1: Static Files Not Loading**
```bash
# Solution
python manage.py collectstatic --noinput
# Check STATIC_ROOT and STATIC_URL in settings.py
# Ensure nginx/web server serves /static/ correctly
```

**Issue 2: Database Connection Error**
```bash
# Solution
# Check DATABASE settings in settings.py
# Verify PostgreSQL is running
sudo systemctl status postgresql
# Check database credentials
```

**Issue 3: Permission Denied**
```bash
# Solution
sudo chown -R www-data:www-data /var/www/rakshanet
sudo chmod -R 755 /var/www/rakshanet
```

**Issue 4: Gunicorn Not Starting**
```bash
# Solution
journalctl -u rakshanet  # Check logs
# Verify socket file path matches nginx config
```

**Issue 5: "DisallowedHost" Error**
```bash
# Solution
# Add your domain to ALLOWED_HOSTS in settings.py
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com', 'server-ip']
```

---

## ✅ Deployment Complete!

Once all steps are completed:
- ✅ RakshaNet is live and accessible
- ✅ Database is configured and migrated
- ✅ Static files are served correctly
- ✅ SSL/HTTPS is enabled
- ✅ Monitoring and backups are in place
- ✅ Security measures are implemented
- ✅ All features are tested and working

**Your disaster management platform is now ready to help communities! 🚀🎉**

---

## 📧 Contact & Support

For deployment assistance:
- Check Django documentation: https://docs.djangoproject.com/
- Review deployment guide: https://docs.djangoproject.com/en/stable/howto/deployment/
- Consult hosting provider documentation

**Good luck with your deployment!** 🌟
