# eBay OAuth Setup with Ngrok

## 🚀 **Your New Ngrok Tunnel**
- **URL**: `https://ead6946c7030.ngrok-free.app`
- **Status**: Online
- **Dashboard**: http://127.0.0.1:4040

## 📋 **eBay Developer Console Configuration**

When setting up your eBay application, use these URLs:

### **1. Privacy Policy URL**
```
https://ead6946c7030.ngrok-free.app/api/core/privacy-policy/
```

### **2. Auth Accepted URL (OAuth Callback)**
```
https://ead6946c7030.ngrok-free.app/api/core/ebay-oauth-callback/
```

### **3. Auth Declined URL**
```
https://ead6946c7030.ngrok-free.app/api/core/ebay-oauth-declined/
```

## 🔧 **Step-by-Step eBay Setup**

### **Step 1: eBay Developer Console**
1. Go to [eBay Developer Console](https://developer.ebay.com/my/keys)
2. Sign in with your eBay account
3. Create a new application or edit existing one

### **Step 2: Configure URLs**
In your eBay application settings, enter:

| Field | URL |
|-------|-----|
| **Privacy Policy URL** | `https://ead6946c7030.ngrok-free.app/api/core/privacy-policy/` |
| **Auth Accepted URL** | `https://ead6946c7030.ngrok-free.app/api/core/ebay-oauth-callback/` |
| **Auth Declined URL** | `https://ead6946c7030.ngrok-free.app/api/core/ebay-oauth-declined/` |

### **Step 3: Get Your Credentials**
After saving, you'll get:
- **App ID** (Client ID)
- **Cert ID** (Client Secret)
- **Client Secret**

### **Step 4: Update Local Settings**
Edit `backend/backend/local_settings.py`:
```python
EBAY_PRODUCTION_APP_ID = 'your-app-id'
EBAY_PRODUCTION_CERT_ID = 'your-cert-id'
EBAY_PRODUCTION_CLIENT_SECRET = 'your-client-secret'
```

### **Step 5: Get Refresh Token**
1. Visit: `https://ead6946c7030.ngrok-free.app/api/core/ebay-oauth/`
2. Complete the OAuth flow
3. Copy the refresh token
4. Add to settings: `EBAY_PRODUCTION_REFRESH_TOKEN = 'your-refresh-token'`

## 🔄 **Restart and Test**
```bash
docker compose restart backend
python test_files/test_ebay_setup_simple.py
```

## 📱 **Mobile App Configuration**

The mobile app can now connect using either:
- **Local**: `http://192.168.0.25:8000/api`
- **Ngrok**: `https://ead6946c7030.ngrok-free.app/api`

## 🛠 **Backend Endpoints Available**

Your backend now has these endpoints accessible via ngrok:

- **API Base**: `https://ead6946c7030.ngrok-free.app/api/`
- **eBay OAuth**: `https://ead6946c7030.ngrok-free.app/api/core/ebay-oauth/`
- **AI Search**: `https://ead6946c7030.ngrok-free.app/api/core/ai/advanced-search/`
- **Privacy Policy**: `https://ead6946c7030.ngrok-free.app/api/core/privacy-policy/`

## 🔍 **Testing Your Setup**

1. **Test Privacy Policy**: Visit `https://ead6946c7030.ngrok-free.app/api/core/privacy-policy/`
2. **Test OAuth Flow**: Visit `https://ead6946c7030.ngrok-free.app/api/core/ebay-oauth/`
3. **Monitor Traffic**: Check http://127.0.0.1:4040

## ⚠️ **Important Notes**

- **Ngrok URLs change** when you restart ngrok
- **Keep ngrok running** while testing eBay integration
- **Update URLs** in eBay console if ngrok URL changes
- **Free ngrok plan** has limitations but works for testing

## 🎯 **Expected Results**

Once configured, you should see:
- ✅ Real eBay listings in mobile app
- ✅ OAuth flow working
- ✅ AI system with eBay search results 