#!/usr/bin/env python
# Simple test to check if our app can be imported

try:
    print("Starting app import test...")
    
    print("1. Importing Flask...")
    from flask import Flask
    print("   ✓ Flask imported successfully")
    
    print("2. Importing app module...")
    from app import create_app
    print("   ✓ App module imported successfully")
    
    print("3. Creating app instance...")
    app = create_app('development')
    print("   ✓ App created successfully")
    
    print("4. Testing app context...")
    with app.app_context():
        print("   ✓ App context working")
    
    print("\n🎉 All tests passed! The app should work.")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
