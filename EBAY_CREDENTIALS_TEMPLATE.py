# eBay Credentials Template
# Copy this to backend/backend/local_settings.py and replace with your real credentials

# eBay OAuth Credentials - REPLACE THESE WITH YOUR REAL CREDENTIALS
EBAY_PRODUCTION_APP_ID = 'your-actual-app-id-here'
EBAY_PRODUCTION_CERT_ID = 'your-actual-cert-id-here'
EBAY_PRODUCTION_CLIENT_SECRET = 'your-actual-client-secret-here'
EBAY_PRODUCTION_REFRESH_TOKEN = 'your-actual-refresh-token-here'  # Will be obtained from OAuth flow

# Instructions:
# 1. Get these credentials from https://developer.ebay.com/my/keys
# 2. Replace the placeholder values above with your real credentials
# 3. Save the file
# 4. Run: docker compose restart backend
# 5. Test with: python test_files/test_ebay_setup_simple.py 