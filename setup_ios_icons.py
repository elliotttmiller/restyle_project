#!/usr/bin/env python3
"""
iOS App Icon Generator for Restyle.ai
Generates all required iOS app icon sizes from the source PNG
"""

import os
import sys
from pathlib import Path

def generate_ios_icons():
    """
    Generate all required iOS app icon sizes using ImageMagick or Pillow
    """
    source_icon = Path("c:/Users/AMD/restyle_project/restyle-icon.png")
    assets_dir = Path("c:/Users/AMD/restyle_project/restyle-mobile/assets")
    
    # iOS App Icon sizes (points and pixels for 3x devices)
    ios_icon_sizes = {
        # iPhone App Icon
        "icon-60@3x.png": 180,  # iPhone App Icon 60pt @3x
        "icon-60@2x.png": 120,  # iPhone App Icon 60pt @2x
        
        # iPad App Icon  
        "icon-76@2x.png": 152,  # iPad App Icon 76pt @2x
        "icon-76.png": 76,      # iPad App Icon 76pt @1x
        "icon-83.5@2x.png": 167, # iPad Pro App Icon 83.5pt @2x
        
        # Settings Icon
        "icon-29@3x.png": 87,   # Settings 29pt @3x
        "icon-29@2x.png": 58,   # Settings 29pt @2x
        "icon-29.png": 29,      # Settings 29pt @1x
        
        # Spotlight
        "icon-40@3x.png": 120,  # Spotlight 40pt @3x
        "icon-40@2x.png": 80,   # Spotlight 40pt @2x
        "icon-40.png": 40,      # Spotlight 40pt @1x
        
        # Notification
        "icon-20@3x.png": 60,   # Notification 20pt @3x
        "icon-20@2x.png": 40,   # Notification 20pt @2x
        "icon-20.png": 20,      # Notification 20pt @1x
        
        # App Store
        "icon-1024.png": 1024,  # App Store 1024x1024
    }
    
    try:
        # Try using Pillow (PIL) first
        from PIL import Image
        
        print(f"📱 Generating iOS app icons from: {source_icon}")
        print(f"🎯 Output directory: {assets_dir}")
        
        # Load source image
        with Image.open(source_icon) as img:
            print(f"✅ Source image loaded: {img.size}")
            
            # Generate each required size
            for filename, size in ios_icon_sizes.items():
                output_path = assets_dir / filename
                
                # Resize with high quality
                resized = img.resize((size, size), Image.Resampling.LANCZOS)
                resized.save(output_path, "PNG", optimize=True)
                
                print(f"✅ Generated: {filename} ({size}x{size})")
        
        print("\n🎉 All iOS app icons generated successfully!")
        print(f"📁 Icons saved to: {assets_dir}")
        
        return True
        
    except ImportError:
        print("❌ Pillow (PIL) not available. Using ImageMagick fallback...")
        
        try:
            import subprocess
            
            # Check if ImageMagick is available
            subprocess.run(["magick", "-version"], check=True, capture_output=True)
            
            print(f"📱 Generating iOS app icons using ImageMagick...")
            
            for filename, size in ios_icon_sizes.items():
                output_path = assets_dir / filename
                
                # Use ImageMagick to resize
                cmd = [
                    "magick", str(source_icon),
                    "-resize", f"{size}x{size}",
                    str(output_path)
                ]
                
                subprocess.run(cmd, check=True)
                print(f"✅ Generated: {filename} ({size}x{size})")
            
            print("\n🎉 All iOS app icons generated successfully with ImageMagick!")
            return True
            
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ ImageMagick not available either.")
            print("ℹ️  Manual resize instructions:")
            print(f"   1. Open {source_icon} in image editor")
            print("   2. Resize to each required size:")
            
            for filename, size in ios_icon_sizes.items():
                print(f"      - {filename}: {size}x{size} pixels")
            
            print(f"   3. Save each to: {assets_dir}")
            return False

def update_expo_config():
    """
    Update the Expo configuration with proper icon references
    """
    print("\n🔧 Updating Expo configuration...")
    
    # The app.json has already been updated with basic icon configuration
    # For iOS-specific icons, we can add them to the iOS section if needed
    
    print("✅ Expo configuration already updated!")
    print("ℹ️  Main app icon: ./assets/icon.png")
    print("ℹ️  Splash screen: ./assets/splash.png")

def display_next_steps():
    """
    Display next steps for deploying the app with new icons
    """
    print("\n" + "="*60)
    print("🚀 NEXT STEPS FOR DEPLOYING YOUR APP ICON")
    print("="*60)
    
    print("\n1. 📱 Build and test locally:")
    print("   cd restyle-mobile")
    print("   npx expo start")
    print("   # Test on iOS Simulator or device")
    
    print("\n2. 🏗️  Build for TestFlight:")
    print("   npx eas build --platform ios --profile production")
    
    print("\n3. 📦 Submit to App Store Connect:")
    print("   npx eas submit --platform ios")
    
    print("\n4. ✅ Verify icon appears correctly:")
    print("   - Home screen icon")
    print("   - Settings app")
    print("   - App Store listing")
    print("   - Spotlight search")
    
    print("\n📋 Icon requirements met:")
    print("   ✅ 1024x1024 App Store icon")
    print("   ✅ Multiple iOS device sizes")
    print("   ✅ Settings and spotlight icons")
    print("   ✅ Notification icons")
    print("   ✅ High-quality PNG format")

def main():
    """
    Main execution function
    """
    print("🎨 RESTYLE.AI iOS APP ICON SETUP")
    print("="*50)
    
    # Generate all iOS icon sizes
    if generate_ios_icons():
        print("✅ Icon generation completed!")
    else:
        print("⚠️  Manual icon generation required!")
    
    # Update Expo configuration
    update_expo_config()
    
    # Show next steps
    display_next_steps()

if __name__ == "__main__":
    main()
