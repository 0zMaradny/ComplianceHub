# Immich Setup — Photo Backup

Immich requires Docker (6+ containers). On Android proot, Docker doesn't work, so we need either cloud or a separate server.

## Option 1: Immich Cloud (easiest)

1. Go to https://my.immich.app
2. Create account with osmaradny@gmail.com
3. Note your server URL from the settings page
4. Install the Android app from Google Play Store
5. Login with your cloud credentials
6. Enable auto-backup for your camera album

**Free tier** includes generous storage. Upgrade if needed.

## Option 2: VPS (cheapest)

| Provider | Plan | Cost | RAM | Storage |
|----------|------|------|-----|---------|
| Hetzner | CAX11 | €3.79/mo | 4GB | 40GB |
| Hetzner | CAX21 | €7.79/mo | 8GB | 80GB |
| DigitalOcean | Basic | $6/mo | 1GB | 25GB |

### Steps
```bash
# SSH into VPS
ssh root@your-vps-ip

# Install Docker
curl -fsSL https://get.docker.com | sh

# Install Immich
mkdir -p ~/immich-app && cd ~/immich-app
wget -O docker-compose.yml https://github.com/immich-app/immich/releases/latest/download/docker-compose.yml
wget -O .env https://github.com/immich-app/immich/releases/latest/download/example.env
# Edit .env — set UPLOAD_LOCATION, DB_PASSWORD
docker compose up -d
```

The Android app connects to `http://your-vps-ip:2283`.

## Option 3: Windows WSL2

If you have a Windows machine, run Docker in WSL2:
```powershell
wsl --install -d ubuntu
# Then follow VPS steps above inside WSL2
```
