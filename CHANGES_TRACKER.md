# 🔄 RakshaNet - Changes Tracker (In Progress & Future)

This file tracks all changes in progress and planned for RakshaNet. Update this file BEFORE pushing changes to GitHub.

> **How to Use:** 
> 1. When starting work on a feature, add it as "In Progress"
> 2. Update status as you work
> 3. When merged, copy to CHANGELOG.md and mark as "✅ Complete"
> 4. Keep dates, PR links, and commit hashes

---

## 📊 Status Indicators

- 🔄 **In Progress** — Currently being worked on
- 📋 **Planned** — Scheduled for development
- ⚠️ **Testing** — In testing/QA phase
- 🔗 **PR Ready** — Ready for pull request review
- ✅ **Complete** → Move to CHANGELOG.md

---

## 🔄 Currently In Progress

### None at this time
All recent changes have been merged and deployed.

---

## 📋 Planned Features (Next Sprint)

### Feature: Advanced Search & Filtering
**Status:** 📋 Planned  
**Priority:** High  
**Assigned to:** [TBD]  
**Timeline:** 2-3 weeks  

**Description:** 
Implement advanced search and filtering on crisis requests page for NGOs to quickly find relevant requests by:
- Disaster type filter
- Urgency level filter
- Status filter (pending, in-progress, completed)
- Date range filter
- Location-based search (radius from NGO)
- Volunteer skill matching
- Resource availability filter

**Affected Files:**
- `RakshaNet/raksha/templates/raksha/ngo_dashboard.html` (new search UI)
- `RakshaNet/raksha/views.py` (search logic)
- `RakshaNet/raksha/models.py` (add search indexes if needed)
- `RakshaNet/raksha/api/views.py` (API endpoint for filters)

**Database Changes:** None expected (use existing fields)

**Testing:** 
- [ ] Unit tests for filter logic
- [ ] Integration tests for combined filters
- [ ] Manual testing with real data

**Deployment:** 
- [ ] Update DEPLOYMENT_STATUS.md with new feature
- [ ] Test on staging environment
- [ ] Deploy to production via Render auto-deploy

---

### Feature: Real-Time Chat Notifications
**Status:** 📋 Planned  
**Priority:** Medium  
**Assigned to:** [TBD]  
**Timeline:** 3-4 weeks  

**Description:**
Add real-time notifications for community chat and coordination chat using WebSockets:
- Browser notifications for new messages
- Desktop notification badge
- Sound alert option
- Read/unread status
- Typing indicators
- Message delivery confirmation

**Affected Files:**
- `RakshaNet/raksha/templates/raksha/community_chat.html` (new notifications UI)
- Create `RakshaNet/raksha/consumers.py` (WebSocket consumer)
- `RakshaNet/raksha/routing.py` (new Django Channels routing)
- `RakshaNet/settings.py` (add Django Channels config)
- `RakshaNet/raksha/static/js/chat-notifications.js` (new JS)

**New Dependencies:** 
- `channels>=4.0.0`
- `channels-redis>=4.1.0`
- `daphne>=4.0.0`

**Database Changes:** 
- Add ChatNotification model
- Add read_at field to existing chat messages

**Testing:**
- [ ] Test WebSocket connections
- [ ] Test notification delivery
- [ ] Test concurrent users
- [ ] Test browser compatibility

**Deployment:**
- [ ] Add Channels to requirements.txt
- [ ] Update Dockerfile to use Daphne
- [ ] Configure Redis on Render (optional paid upgrade)
- [ ] Update docker-compose for local testing
- [ ] Database migrations

---

### Feature: Mobile App Version
**Status:** 📋 Planned  
**Priority:** High  
**Assigned to:** [TBD]  
**Timeline:** 6-8 weeks  

**Description:**
Create React Native mobile app for iOS and Android with:
- Request help functionality
- Real-time notifications
- Offline mode
- Location sharing
- Emergency quick call
- Volunteer assignment viewing
- Chat messaging

**Affected Files:**
- Create new directory: `rakshanet-mobile/` (separate project)
- Create API endpoints if needed in Django
- `RakshaNet/raksha/api/` (enhance existing API)

**New Technologies:**
- React Native
- Expo (for easier development)
- Redux (state management)
- React Navigation
- Geolocation APIs
- Push Notifications (Firebase)

**Testing:**
- [ ] iOS simulator testing
- [ ] Android emulator testing
- [ ] Real device testing
- [ ] App store submission requirements

**Deployment:**
- [ ] Apple App Store
- [ ] Google Play Store
- [ ] Beta testing (TestFlight, Google Play Beta)

---

## ⚠️ Testing & QA

### None currently

---

## 🔗 Pull Requests & Commits

### Recent Merged PRs

| PR | Title | Status | Merged Date | Commit |
|----|-------|--------|-------------|--------|
| #1 | Responsive Design Enhancements | ✅ Merged | Apr 6, 2026 | 4835576 |
| #2 | Live Deployment Configuration | ✅ Merged | Apr 6, 2026 | 684aab5 |

---

## 🐛 Known Issues & Bugs

### Issue: Render Free Tier Auto-Sleep
**Severity:** Low  
**Status:** Known Limitation  
**Affected:** Production deployment  
**Description:** Service sleeps after 15 minutes of inactivity on free tier
**Workaround:** Upgrade to Starter Plan ($7/month) or implement uptime monitor
**Fix Timeline:** Optional upgrade

### Issue: Form Long Loading on Mobile
**Severity:** Low  
**Status:** Monitoring  
**Affected:** Mobile devices (slow networks)  
**Description:** Form submission may take 5-10 seconds on slow 3G
**Root Cause:** Gunicorn response time + network latency
**Workaround:** Add loading state animations (already done)
**Fix Timeline:** Next Sprint - optimize database queries

---

## 📝 Change Template

Copy this template when creating a new entry:

```markdown
### Feature: [Feature Name]
**Status:** 📋 Planned  
**Priority:** [Critical/High/Medium/Low]  
**Assigned to:** [Name or TBD]  
**Timeline:** [Duration]  

**Description:** [What and why]

**Affected Files:**
- File 1
- File 2

**New Dependencies:** 
- package@version

**Database Changes:** 
- [Changes or None]

**Testing:**
- [ ] Test type 1
- [ ] Test type 2

**Deployment:**
- [ ] Step 1
- [ ] Step 2
```

---

## 📊 Development Velocity

| Metric | Value |
|--------|-------|
| Features Deployed (Apr 2026) | 2 major |
| Bug Fixes (Apr 2026) | 4 critical |
| Avg Time to Deploy | 2-3 minutes |
| Test Coverage | [To be measured] |
| Current Uptime | 99.5% |

---

## 🎯 Backlog (Future Ideas)

- [ ] Advanced analytics dashboard
- [ ] Multi-factor authentication (2FA)
- [ ] Volunteer scheduling calendar
- [ ] Automated resource allocation AI
- [ ] Video call support for emergencies
- [ ] SMS notifications
- [ ] WhatsApp integration
- [ ] Offline mode support
- [ ] Custom domain mapping
- [ ] Email digest subscriptions
- [ ] Database query optimization & indexes
- [ ] Redis caching layer
- [ ] CDN for static files distribution
- [ ] Rate limiting on APIs
- [ ] API documentation (Swagger/OpenAPI)
- [ ] Backup automation to S3
- [ ] Monitoring & alerting (Sentry)
- [ ] Performance monitoring (New Relic)

---

## 🔒 Security Enhancements (Planned)

- [ ] Implement OWASP Top 10 security checks
- [ ] Add rate limiting to APIs
- [ ] Implement API key authentication
- [ ] Add SQL injection prevention tests
- [ ] Implement XSS protection tests
- [ ] Add CSRF token validation tests
- [ ] Set up security headers audit
- [ ] Implement content security policy (CSP)
- [ ] Add permission testing for all endpoints
- [ ] Implement audit logging for critical actions

---

## 📈 Performance Improvements (Planned)

- [ ] Database query optimization
  - [ ] Add indexes on frequently queried fields
  - [ ] Optimize N+1 queries
  - [ ] Implement caching for static data
  
- [ ] Frontend optimization
  - [ ] Code splitting for landing page
  - [ ] Lazy loading for images
  - [ ] CSS minification
  - [ ] JavaScript bundling
  
- [ ] Infrastructure scaling
  - [ ] Setup CDN for static files
  - [ ] Configure Redis caching
  - [ ] Database connection pooling
  - [ ] Implement database read replicas

---

## 📚 Documentation Improvements (Planned)

- [ ] API documentation (Swagger/OpenAPI)
- [ ] Database schema diagram
- [ ] Architecture diagram
- [ ] Architecture decision records (ADRs)
- [ ] Video tutorials for key features
- [ ] Admin user guide
- [ ] NGO operator guide
- [ ] Volunteer guide
- [ ] Citizen guide
- [ ] Deployment runbooks

---

## 🤝 Collaboration Notes

**Team Communication:**
- Use this file to coordinate between developers
- Update status before end of day
- Mention blockers and dependencies
- Link to relevant issues/PRs

**Code Review:**
- All changes require code review
- Link CHANGELOG entries in PRs
- Reference this tracker in discussions

**Release Process:**
1. Update this file with all changes
2. Create GitHub release with version tag
3. Copy complete entries to CHANGELOG.md
4. Deploy via Render auto-deploy
5. Monitor deployment logs
6. Verify on live site

---

## 🔗 Quick Links

| Resource | Link |
|----------|------|
| Live Site | https://rakshanet-bfr0.onrender.com |
| GitHub Repo | https://github.com/vippagowthami/rakshanet |
| GitHub Issues | https://github.com/vippagowthami/rakshanet/issues |
| Render Dashboard | https://dashboard.render.com/ |
| CHANGELOG | [CHANGELOG.md](CHANGELOG.md) |

---

## 📋 Template: Deployment Checklist

Use this before deploying:

- [ ] All changes documented in CHANGES_TRACKER.md
- [ ] Code reviewed and approved
- [ ] All tests passing
- [ ] CHANGELOG.md updated with release notes
- [ ] Version number incremented in appropriate file
- [ ] Commit message is descriptive
- [ ] Branch is up-to-date with main
- [ ] No merge conflicts
- [ ] Verified locally: `python manage.py check`
- [ ] Verified on live site after deployment
- [ ] Database migrations successful
- [ ] Static files collected properly
- [ ] No new error logs in Render dashboard

---

**Last Updated:** April 6, 2026  
**Next Review Date:** [TBD - Next Sprint]  
**Maintainer:** Vippa Gowthami  
**Repository:** https://github.com/vippagowthami/rakshanet
