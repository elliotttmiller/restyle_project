# 📱 Restyle.ai iOS App Icon Setup

This directory contains all the app icons and assets for the Restyle.ai mobile application.

## 🎨 Icon Files

### Main Icons
- `icon.png` - Main app icon (1024x1024) for general use
- `splash.png` - Splash screen image
- `original-icon.png` - Original source icon file

### iOS-Specific Icons
All iOS app icon sizes have been generated to meet Apple's requirements:

#### iPhone App Icons
- `icon-60@3x.png` (180x180) - iPhone App Icon 60pt @3x
- `icon-60@2x.png` (120x120) - iPhone App Icon 60pt @2x

#### iPad App Icons  
- `icon-76@2x.png` (152x152) - iPad App Icon 76pt @2x
- `icon-76.png` (76x76) - iPad App Icon 76pt @1x
- `icon-83.5@2x.png` (167x167) - iPad Pro App Icon 83.5pt @2x

#### Settings Icons
- `icon-29@3x.png` (87x87) - Settings 29pt @3x
- `icon-29@2x.png` (58x58) - Settings 29pt @2x
- `icon-29.png` (29x29) - Settings 29pt @1x

#### Spotlight Icons
- `icon-40@3x.png` (120x120) - Spotlight 40pt @3x
- `icon-40@2x.png` (80x80) - Spotlight 40pt @2x
- `icon-40.png` (40x40) - Spotlight 40pt @1x

#### Notification Icons
- `icon-20@3x.png` (60x60) - Notification 20pt @3x
- `icon-20@2x.png` (40x40) - Notification 20pt @2x
- `icon-20.png` (20x20) - Notification 20pt @1x

#### App Store Icon
- `icon-1024.png` (1024x1024) - App Store submission icon

## 🔧 Configuration

The app icons are configured in `app.json`:

```json
{
  "expo": {
    "icon": "./assets/icon.png",
    "splash": {
      "image": "./assets/splash.png",
      "resizeMode": "contain",
      "backgroundColor": "#ffffff"
    },
    "ios": {
      "icon": "./assets/icon-1024.png"
    },
    "android": {
      "adaptiveIcon": {
        "foregroundImage": "./assets/icon.png",
        "backgroundColor": "#ffffff"
      }
    }
  }
}
```

## 🚀 Building with Icons

### Local Development
```bash
cd restyle-mobile
npx expo start
```

### Production Build for TestFlight
```bash
npx eas build --platform ios --profile production
```

### Submit to App Store
```bash
npx eas submit --platform ios
```

## ✅ Icon Checklist

- [x] 1024x1024 App Store icon
- [x] Multiple iOS device sizes (iPhone/iPad)
- [x] Settings and spotlight icons
- [x] Notification icons  
- [x] High-quality PNG format
- [x] Proper alpha channel handling
- [x] Expo configuration updated
- [x] Ready for TestFlight deployment

## 📱 Where Icons Appear

Your Restyle.ai icon will appear in:
- **Home Screen** - Main app icon users tap to launch
- **Settings App** - When users configure app settings
- **Spotlight Search** - When users search for your app
- **App Store** - In store listings and search results
- **Notifications** - When your app sends push notifications
- **Task Switcher** - When users switch between apps

## 🎯 Next Steps

1. Test the app locally with `npx expo start`
2. Build for TestFlight with `npx eas build --platform ios`
3. Submit to App Store Connect
4. Verify icons appear correctly on all devices

Your Restyle.ai app is now ready with professional iOS app icons! 🎉
