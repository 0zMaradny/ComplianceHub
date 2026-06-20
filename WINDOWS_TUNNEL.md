# Windows Tunnel Setup — Cherry Studio + ComplianceHub

## Why Cloudflared (not Serveo)

Your mobile carrier blocks SSH port 22, so Serveo doesn't work. Cloudflared uses HTTP/2 on port 443 — always allowed.

## 1. Install Cloudflared on Windows

### Option A: winget (recommended)
```powershell
winget install cloudflare.cloudflared
```

### Option B: Manual download
1. Download `cloudflared-windows-amd64.exe` from https://github.com/cloudflare/cloudflared/releases
2. Rename to `cloudflared.exe` and place in `C:\Windows\System32\` or add folder to PATH

### Verify
```powershell
cloudflared --version
```

## 2. Get Current Tunnel URL

The tunnel URL changes every restart. Get it from:
- **Android**: `cat /root/Documents/ComplianceHub/.tunnel-url`
- Or from the tunnel watchdog output when `go.sh` runs

Current URL: `https://shirts-enclosure-fell-paste.trycloudflare.com`

## 3. Test the Tunnel from Windows

```powershell
curl -s https://shirts-enclosure-fell-paste.trycloudflare.com/v1/models
```

Should return a JSON list with 12 models (auto, Claude Sonnet 4.6, Claude Opus 4.6, Nemotron, Qwen3, etc.)

## 4. Cherry Studio Configuration

### Add Provider
1. Open Cherry Studio → Settings → AI Providers → Add Provider
2. Fill in:
   - **Name**: `ComplianceHub Tunnel`
   - **API Endpoint**: `https://shirts-enclosure-fell-paste.trycloudflare.com/v1`
   - **API Key**: (leave empty)
   - **Type**: OpenAI Compatible

### Add Models
Add each model you want to use:
| Model ID | Type | Notes |
|----------|------|-------|
| `claude-sonnet-4-6` | Chat | Antigravity Claude — free, 200k context |
| `claude-opus-4-6-thinking` | Chat | Antigravity Claude — free, thinking mode |
| `nemotron-ultra` | Chat | OpenRouter — 550B, 1M context |
| `qwen3-coder` | Chat | OpenRouter — 480B, best for structured output |
| `kimi-k26` | Chat | OpenRouter — ties GPT-5.5, 262k ctx |
| `owl-alpha` | Chat | OpenRouter — 1M ctx, agentic |
| `nemotron-super` | Chat | OpenRouter — 120B, fast |
| `llama-70b` | Chat | OpenRouter — 70B proven workhorse |
| `qwen3-next` | Chat | OpenRouter — 80B, 262k ctx |
| `hermes-405b` | Chat | OpenRouter — 405B reasoning |
| `groq-llama` | Chat | Groq — fastest, ~800 t/s |

### Test
Send a message like "Hello, which model are you?" — the backend will respond through the 5-tier fallback starting with the selected model.

## 5. Auto-Update Tunnel URL (Script)

The tunnel URL changes on every Android restart. Use this PowerShell script to keep Cherry Studio in sync:

```powershell
# fetch-tunnel-url.ps1
$urlFile = "\\YOUR_ANDROID_SHARE\ComplianceHub\.tunnel-url"
if (Test-Path $urlFile) {
    $url = Get-Content $urlFile -Raw
    Write-Host "Tunnel URL: $url"
    # Update Cherry Studio config here if needed
} else {
    Write-Host "Tunnel URL file not found. Run go.sh on Android first."
}
```

## 6. Troubleshooting

| Symptom | Fix |
|---------|-----|
| `curl` hangs or times out | Android device may be offline or tunnel crashed. Run `bash go.sh` on Android. |
| 502 Bad Gateway | Backend not running. Run `bash go.sh` on Android. |
| Model not in Cherry Studio list | Manually add model ID in Cherry Studio provider settings. |
| Slow responses (~5-6s) | Normal. Mobile carrier adds latency through the tunnel. Local access is 8-12ms. |
