RakshaNet Deployment Guide
==========================

This project includes a `Dockerfile` and `Procfile` for container-based deployment.

Option A — Deploy on Render (recommended, builds from Dockerfile):

1. Create an account at https://render.com and connect your GitHub repository.
2. Create a new Web Service → select your repository and set the following:
   - Environment: Docker
   - Build Command: leave default (Render builds the Dockerfile)
   - Start Command: leave empty (Dockerfile CMD is used)
3. Add the following environment variables in your Render service settings:
   - `SECRET_KEY` — a secure Django secret key
   - `DEBUG` — `False` for production
   - `ALLOWED_HOSTS` — comma-separated list, for example: `your-app.onrender.com,localhost,127.0.0.1`
   - Email settings if you need email notifications
4. Deploy — Render will build the image and provide a public URL.

Option B — Deploy to Heroku (container mode):

1. Install the Heroku CLI and login: `heroku container:login`.
2. Create an app: `heroku create <app-name>`.
3. Build and push the container:
   ```bash
   docker build -t registry.heroku.com/<app-name>/web .
   docker push registry.heroku.com/<app-name>/web
   heroku container:release web -a <app-name>
   ```
4. Set config vars in Heroku (`SECRET_KEY`, `DEBUG=False`, email settings).

Option C — GitHub Actions + GitHub Packages (CI build + publish):

- See `.github/workflows/docker-publish.yml` for a starter workflow that builds and publishes a Docker image to GitHub Container Registry. You will need to set `CR_PAT` (a personal access token) in your repo secrets.

Notes
- Ensure `DEBUG=False` and `ALLOWED_HOSTS` are set correctly in production.
- Use PostgreSQL in production; update `DATABASES` and set environment vars accordingly.
