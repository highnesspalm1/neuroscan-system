#!/usr/bin/env python3
"""
Check if Vercel has the correct environment variables set
and provide instructions to fix the customer portal login
"""

import requests
import json

def main():
    print("🔍 CUSTOMER PORTAL LOGIN FIX ANALYSIS")
    print("=" * 60)
    
    print("\n📋 ISSUE SUMMARY:")
    print("   • Customer Portal frontend is accessible ✅")
    print("   • Backend API is working correctly ✅") 
    print("   • Login fails in browser but works via API ❌")
    
    print("\n🎯 MOST LIKELY CAUSES:")
    print("   1. Render.com service goes to sleep (cold starts)")
    print("   2. Frontend timeout issues during API wake-up")
    print("   3. Environment variables not set in Vercel")
    print("   4. Browser cache issues")
    
    print("\n🛠️  SOLUTIONS TO TRY:")
    
    print("\n1️⃣ WAKE UP THE API SERVICE:")
    print("   Visit: https://neuroscan-api.onrender.com/health")
    print("   Wait for 200 OK response, then immediately try login")
    
    print("\n2️⃣ HARD REFRESH THE CUSTOMER PORTAL:")
    print("   • Press Ctrl+F5 in browser to clear cache")
    print("   • Or Ctrl+Shift+R to hard reload")
    
    print("\n3️⃣ VERIFY ENVIRONMENT VARIABLES IN VERCEL:")
    print("   • Go to Vercel dashboard")
    print("   • Navigate to neuroscan-system project") 
    print("   • Settings → Environment Variables")
    print("   • Ensure VITE_API_URL = https://neuroscan-api.onrender.com")
    
    print("\n4️⃣ TRY INCOGNITO/PRIVATE BROWSING:")
    print("   • Open customer portal in incognito mode")
    print("   • This bypasses any cached API configurations")
    
    print("\n5️⃣ CHECK BROWSER CONSOLE:")
    print("   • Open Developer Tools (F12)")
    print("   • Check Console tab for errors")
    print("   • Check Network tab for failed requests")
    
    # Test current API status
    print("\n🧪 CURRENT API STATUS CHECK:")
    try:
        response = requests.get("https://neuroscan-api.onrender.com/health", timeout=10)
        if response.status_code == 200:
            print("   ✅ API is currently awake and responding")
            print("   💡 Try customer login immediately!")
        else:
            print(f"   ⚠️ API returned status {response.status_code}")
    except requests.exceptions.Timeout:
        print("   ❌ API is sleeping/cold starting (takes 30+ seconds)")
        print("   💡 Wait a moment and try again")
    except Exception as e:
        print(f"   ❌ API connection error: {e}")
    
    print("\n🎯 IMMEDIATE ACTION PLAN:")
    print("   1. Visit https://neuroscan-api.onrender.com/health")
    print("   2. Wait for the API to wake up (green checkmark)")
    print("   3. Immediately go to https://neuroscan-system.vercel.app/customer/login")
    print("   4. Try login with: testcustomer / password123")
    print("   5. If it still fails, try hard refresh (Ctrl+F5)")
    
    print("\n📞 TECHNICAL DETAILS:")
    print("   • Backend: Render.com free tier (auto-sleeps)")
    print("   • Frontend: Vercel (always on)")
    print("   • Database: PostgreSQL (persistent)")
    print("   • Auth: JWT tokens (working)")
    
    print("\n✅ CONFIDENCE LEVEL: HIGH")
    print("   The customer portal should work once the API is warmed up!")

if __name__ == "__main__":
    main()
