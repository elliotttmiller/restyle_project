# SSL/TLS Debug Checklist for Django/DRF Endpoints

## 1. Certificate Validity
- [ ] Ensure your SSL certificate is valid (not expired) and covers all domains/subdomains.
- [ ] Use an SSL checker (e.g., SSL Labs) to verify the cert chain and hostname.

## 2. Web Server/Proxy Configuration
- [ ] If using Nginx/Apache, confirm all `server` blocks for API endpoints use the same SSL cert and config.
- [ ] Check for endpoint-specific `location` blocks that might override SSL settings.
- [ ] Ensure `proxy_pass` and `proxy_set_header` are consistent for all endpoints.
- [ ] If using Railway or a PaaS, check their SSL/TLS documentation for custom domains and API routing.

## 3. Django Settings
- [ ] `SECURE_SSL_REDIRECT = True` (if all traffic should be HTTPS)
- [ ] `CSRF_COOKIE_SECURE = True` and `SESSION_COOKIE_SECURE = True`
- [ ] No endpoint-specific middleware that could interfere with SSL.

## 4. Certificate Chain and Intermediate Certs
- [ ] Ensure the full certificate chain is provided to the web server (not just the leaf cert).
- [ ] For Nginx: use `ssl_certificate` (fullchain) and `ssl_certificate_key` (private key).

## 5. Debugging Tools
- [ ] Use `curl -v https://yourdomain/api/core/ai/crop-preview/` to check for SSL handshake errors.
- [ ] Use browser dev tools to inspect cert details and errors.
- [ ] Check server logs for SSL handshake or protocol errors.

## 6. Platform/Deployment
- [ ] If using a managed platform (Railway, Heroku, etc.), check for platform-specific SSL proxying or endpoint routing issues.
- [ ] Ensure all endpoints are routed through the same SSL termination point.

## 7. Python/Requests Client
- [ ] If disabling SSL verification in tests, confirm the error persists with `verify=False` (indicates server-side issue).
- [ ] Ensure the server supports modern TLS versions (1.2+).

---

If the error persists after these checks, try reissuing your SSL certificate, restarting your web server, or contacting your hosting provider for endpoint-specific SSL issues.
