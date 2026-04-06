# 🚀 RakshaNet Live Deployment Status

## Production Environment

**Live URL:** https://rakshanet-bfr0.onrender.com

### Deployment Platform
- **Service:** Render.com (Docker)
- **Region:** Oregon
- **Plan:** Free Tier
- **Status:** ✅ Active & Monitoring
- **Auto-Deploy:** ✅ Enabled (main branch)
- **SSL/TLS:** ✅ Automatic HTTPS
- **Database:** PostgreSQL

---

## How Continuous Deployment Works

Every time you push to `main` branch on GitHub:

```
1. GitHub detects push to main
   ↓
2. Render webhook triggered
   ↓
3. Dockerfile builds new image
   ↓
4. Database migrations run automatically
   ↓
5. Static files collected
   ↓
6. Gunicorn service starts (3 workers)
   ↓
7. Live at https://rakshanet-bfr0.onrender.com
   
Typical deployment time: 2-3 minutes
```

---

## Quick Deployment Steps

### 1. Make Changes Locally
```bash
# Edit files in your workspace
# Test locally: python manage.py runserver
```

### 2. Commit Changes
```bash
cd RakshaNet
git add .
git commit -m "Your descriptive commit message"
```

### 3. Push to GitHub
```bash
git push origin main
```

### 4. Monitor Deployment
Visit the Render Dashboard to monitor:
- https://dashboard.render.com/
- Select "RakshaNet" service
- Check "Deployments" tab for live build logs

### 5. Verify Live
Once deployment completes, visit:
- https://rakshanet-bfr0.onrender.com

---

## Environment Configuration

### Render Dashboard Environment Variables

All production environment variables are configured in:
**Render Dashboard → RakshaNet Service → Environment**

**Current Active Variables:**
```
SECRET_KEY            = [Auto-generated secure key]
DEBUG                 = False
ALLOWED_HOSTS         = .onrender.com,localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS  = https://*.onrender.com,http://localhost:8000,http://127.0.0.1:8000
CSRF_COOKIE_SECURE    = True
SESSION_COOKIE_SECURE = True
SECURE_SSL_REDIRECT   = True
SECURE_HSTS_SECONDS   = 31536000
DATABASE_URL          = [PostgreSQL connection string]
EMAIL_HOST_USER       = [Optional - for email notifications]
EMAIL_HOST_PASSWORD   = [Optional - for email notifications]
```

### To Add/Update Variables:
1. Go to Render Dashboard
2. Select RakshaNet service
3. Go to "Environment" tab
4. Add or update the key-value pair
5. Changes take effect on next deployment

---

## Git Workflow for Deployment

### Best Practices

```bash
# 1. Always pull latest changes first
git pull origin main

# 2. Create a feature branch for new work (optional)
git checkout -b feature/your-feature-name

# 3. Make changes and test locally
# ... edit files ...
python manage.py runserver
# ... verify changes in http://localhost:8000 ...

# 4. Stage changes
git add .

# 5. Commit with clear messages
git commit -m "feat: Add responsive design improvements"
# Good commit messages:
# - feat: New feature
# - fix: Bug fix
# - docs: Documentation update
# - refactor: Code restructuring

# 6. Merge to main (if using feature branch)
git checkout main
git merge feature/your-feature-name

# 7. Push to GitHub (triggers Render deployment)
git push origin main

# 8. Monitor deployment at dashboard.render.com
```

### Commit Message Examples

```
✅ GOOD:
git commit -m "feat: Add responsive mobile design for all screens"
git commit -m "fix: Correct responsive dropdown menu visibility on tablets"
git commit -m "docs: Update deployment documentation with live URL"

❌ AVOID:
git commit -m "Update"
git commit -m "Changes"
git commit -m "Fix bugs"
```

---

## Troubleshooting

### Issue: Deployment Failed

**Check these things:**
1. **Log into Render Dashboard** → Select RakshaNet → Deployments
2. **View build logs** to identify the error
3. **Common issues:**

| Issue | Solution |
|-------|----------|
| Import Error | Ensure all packages in requirements.txt are installed locally too: `pip install -r requirements.txt` |
| Database Migration Error | Run locally: `python manage.py migrate` before pushing |
| Static Files Error | Ensure static files are collected: `python manage.py collectstatic` |
| Port Configuration | Dockerfile exposes port 8000; Render auto-routes this |
| SECRET_KEY Missing | Render has `generateValue: true` in render.yaml |

### Issue: Site Shows Old Version

**Solutions:**
1. Hard refresh browser: `Ctrl+Shift+R` (Chrome) or `Cmd+Shift+R` (Mac)
2. Clear browser cache in Render dashboard if needed
3. Check deployment status - in progress deployments take 2-3 minutes

### Issue: Can't Access https://rakshanet-bfr0.onrender.com

1. Check if Render service is running:
   - Go to https://dashboard.render.com/
   - Check service status (should be "Live")
2. If service is "Deploying", wait 2-3 minutes
3. If service is "Suspended", it's on free tier and inactive for 15 minutes:
   - Click "Resume" to restart
4. Check for deployment errors in logs

---

## Performance & Limits (Free Tier)

### Render Free Tier Specifications
- **CPU:** 1 vCPU (shared)
- **Memory:** 512 MB
- **Compute Units:** 0.5
- **Inactivity Sleep:** Sleeps after 15 min of no traffic
- **Region:** Oregon

### What Happens When Free-Tier Service Sleeps
- Website goes down if no traffic for 15 minutes
- First request after sleep will be slow (15-30 seconds to spin up)
- Automatic restart on next request
- Database remains active

### Scaling to Production
To remove sleep restrictions and improve performance:
1. **Upgrade to Starter Plan** in Render Dashboard
   - Cost: $7/month
   - No auto-sleep
   - Dedicated resources
   - Better performance

---

## Monitoring & Logs

### Access Deployment Logs
1. Go to https://dashboard.render.com/
2. Click on RakshaNet service
3. View "Logs" tab for real-time output
4. View "Deployments" tab for build history

### Common Log Messages

```
Starting build...                    # Build started
Building Docker image...             # Dockerfile processing
Collecting static files...           # Django static files
Running migrations...                # Database setup
Starting web service...              # Gunicorn starting
Your service is live!                # ✅ Deployment successful
```

---

## Database Management

### Production Database
- PostgreSQL hosted by Render
- Connection string in `DATABASE_URL` environment variable
- Automatic Django migrations on each deployment

### Database Operations

```bash
# Locally, to test migrations:
python manage.py migrate

# View migration status:
python manage.py showmigrations

# Create migration for model changes:
python manage.py makemigrations

# Squash old migrations (advanced):
python manage.py squashmigrations raksha 0001 0020
```

### Backing Up Database (Optional)
Render automatically backs up PostgreSQL. For manual backup:
1. Go to Render Dashboard → Databases tab
2. Select your PostgreSQL instance
3. Click "Backups" → "Request Backup"

---

## Email Configuration (Optional)

To enable email notifications for crisis alerts:

1. **Get Gmail App Password:**
   - Go to https://myaccount.google.com/security
   - Enable 2-Factor Authentication
   - Generate App Password for "Mail"
   - Copy the 16-character password

2. **Add to Render Environment:**
   - `EMAIL_HOST` = smtp.gmail.com
   - `EMAIL_PORT` = 587
   - `EMAIL_HOST_USER` = your-email@gmail.com
   - `EMAIL_HOST_PASSWORD` = [16-char app password]
   - `EMAIL_USE_TLS` = True

3. **Test Email Locally:**
   ```bash
   python manage.py shell
   >>> from django.core.mail import send_mail
   >>> send_mail('Test', 'Message', 'from@gmail.com', ['to@example.com'])
   ```

---

## Health Checks

Render monitors service availability:
- **Health Check Endpoint:** `/admin/` (Django admin)
- **Check Interval:** Every 30 seconds
- **Timeout:** 5 seconds
- **Auto-Restart:** On failure after 3 consecutive failures

If service becomes unresponsive, Render automatically restarts the container.

---

## Static Files & Assets

### How Static Files Work

1. **Dockerfile** runs: `python manage.py collectstatic --noinput`
2. All CSS, JS, images collected to `staticfiles/` directory
3. Served by Gunicorn web server
4. Render can optionally use CDN (not configured yet)

### Adding New Static Files

```bash
# Place CSS/JS in app static directory:
# RakshaNet/raksha/static/raksha/css/custom.css
# RakshaNet/raksha/static/raksha/js/script.js
# RakshaNet/blog/static/blog/style.css

# Local: collect files
python manage.py collectstatic

# Push to GitHub (auto-collected on deployment)
git add .
git commit -m "feat: Add new static assets"
git push origin main
```

---

## Security Checklist

✅ **Enabled:**
- [x] HTTPS/SSL (automatic)
- [x] DEBUG = False
- [x] SECURE_SSL_REDIRECT = True
- [x] CSRF protection enabled
- [x] Session cookies secure
- [x] HSTS headers enabled
- [x] Database encrypted connection

📋 **Recommended (not configured yet):**
- [ ] Set up custom domain (instead of .onrender.com)
- [ ] Add rate limiting for APIs
- [ ] Implement DDoS protection
- [ ] Set up monitoring alerts
- [ ] Regular database backups

---

## Useful Links

| Link | Purpose |
|------|---------|
| https://rakshanet-bfr0.onrender.com | Live Production |
| https://dashboard.render.com/ | Deployment Dashboard |
| https://github.com/vippagowthami/rakshanet | GitHub Repository |
| http://localhost:8000 | Local Development |
| http://127.0.0.1:8000/admin/ | Django Admin (local) |

---

## CI/CD Pipeline Status

**Current Setup:**
- ✅ GitHub → Render webhook configured
- ✅ Automatic build on main branch push
- ✅ Docker image build process
- ✅ Database migrations automatic
- ✅ Deployment notifications (if Slack configured)

**Optional Enhancements:**
- [ ] GitHub Actions for testing before deploy
- [ ] Slack notifications on deploy success/failure
- [ ] Automated backups to S3
- [ ] Load balancing (for paid tier)

---

## Support & Next Steps

### If You Need Help
1. Check Render Dashboard logs: https://dashboard.render.com/
2. Review this deployment guide
3. Check Django logs locally: `python manage.py runserver`
4. Review deployment docs: [DEPLOY.md](docs/DEPLOY.md)

### To Improve Deployment
1. Upgrade to Starter Plan for better performance
2. Set up custom domain (e.g., rakshanet.com)
3. Enable CDN for faster static file serving
4. Configure email notifications
5. Set up monitoring and alerting

---

**Last Updated:** April 6, 2026
**Deployment:** Active ✅
**Version:** Latest from `main` branch
