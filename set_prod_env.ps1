$env:ERP_API_STRICT_DYNAMIC_TOKENS = "true"
$env:ERP_API_RATE_LIMIT_MAX_REQUESTS = "120"
$env:ERP_API_RATE_LIMIT_WINDOW_SEC = "60"
$env:ERP_API_TOKEN_TTL_HOURS = "12"
$env:ERP_API_ALLOWED_SUBNETS = "192.168.1.0/24,10.0.0.0/8"
$env:ERP_API_EXPOSE_NETWORK = "true"

Write-Host "ERP production environment variables loaded for this session." -ForegroundColor Green
Write-Host "You can now run: python main.py" -ForegroundColor Cyan
