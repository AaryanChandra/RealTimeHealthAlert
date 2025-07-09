#!/usr/bin/env python3
"""
Railway Deployment Helper for Critical Care Monitor
"""

import os
import subprocess
import sys

def check_railway_cli():
    """Check if Railway CLI is installed"""
    try:
        result = subprocess.run(['railway', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Railway CLI is installed")
            return True
        else:
            print("❌ Railway CLI not found")
            return False
    except FileNotFoundError:
        print("❌ Railway CLI not installed")
        return False

def install_railway_cli():
    """Install Railway CLI"""
    print("📦 Installing Railway CLI...")
    try:
        subprocess.run(['npm', 'install', '-g', '@railway/cli'], check=True)
        print("✅ Railway CLI installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install Railway CLI")
        return False

def deploy_to_railway():
    """Deploy the application to Railway"""
    print("🚀 Deploying to Railway...")
    
    # Check if already logged in
    try:
        result = subprocess.run(['railway', 'whoami'], capture_output=True, text=True)
        if result.returncode != 0:
            print("🔐 Please login to Railway first:")
            print("   railway login")
            return False
    except:
        print("❌ Railway CLI not available")
        return False
    
    # Initialize Railway project
    try:
        subprocess.run(['railway', 'init'], check=True)
        print("✅ Railway project initialized")
    except subprocess.CalledProcessError:
        print("⚠️ Railway project already exists")
    
    # Deploy
    try:
        subprocess.run(['railway', 'up'], check=True)
        print("✅ Deployment successful!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Deployment failed")
        return False

def set_environment_variables():
    """Set environment variables"""
    print("🔧 Setting environment variables...")
    
    # Get MongoDB URI from user
    mongodb_uri = input("Enter your MongoDB Atlas connection string: ").strip()
    
    if not mongodb_uri:
        print("❌ MongoDB URI is required")
        return False
    
    try:
        subprocess.run(['railway', 'variables', 'set', f'MONGODB_URI={mongodb_uri}'], check=True)
        subprocess.run(['railway', 'variables', 'set', 'FLASK_ENV=production'], check=True)
        print("✅ Environment variables set successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to set environment variables")
        return False

def main():
    """Main deployment process"""
    print("🏥 Critical Care Monitor - Railway Deployment")
    print("=" * 50)
    
    # Check Railway CLI
    if not check_railway_cli():
        install = input("Install Railway CLI? (y/n): ").lower()
        if install == 'y':
            if not install_railway_cli():
                return
        else:
            print("❌ Railway CLI required for deployment")
            return
    
    # Set environment variables
    if not set_environment_variables():
        return
    
    # Deploy
    if deploy_to_railway():
        print("\n🎉 Deployment completed successfully!")
        print("📱 Your app is now live on Railway!")
        print("🔗 Check your Railway dashboard for the URL")
    else:
        print("\n❌ Deployment failed")
        print("💡 Check the error messages above")

if __name__ == "__main__":
    main() 