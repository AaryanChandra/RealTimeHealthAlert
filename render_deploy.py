#!/usr/bin/env python3
"""
Render Deployment Guide for Critical Care Monitor
"""

import os
import json

def create_render_config():
    """Create render.yaml for Render deployment"""
    
    render_config = {
        "services": [
            {
                "type": "web",
                "name": "critical-care-monitor",
                "env": "python",
                "buildCommand": "pip install -r requirements.txt",
                "startCommand": "gunicorn dashboard.mongo_app:app",
                "envVars": [
                    {
                        "key": "FLASK_ENV",
                        "value": "production"
                    },
                    {
                        "key": "MONGODB_URI",
                        "value": "YOUR_MONGODB_ATLAS_URI_HERE"
                    }
                ]
            }
        ]
    }
    
    with open('render.yaml', 'w') as f:
        import yaml
        yaml.dump(render_config, f, default_flow_style=False)
    
    print("✅ Created render.yaml configuration file")

def create_dockerfile():
    """Create Dockerfile for containerized deployment"""
    
    dockerfile_content = """FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "dashboard.mongo_app:app"]
"""
    
    with open('Dockerfile', 'w') as f:
        f.write(dockerfile_content)
    
    print("✅ Created Dockerfile")

def main():
    """Main setup process"""
    print("🏥 Critical Care Monitor - Render Deployment Setup")
    print("=" * 50)
    
    print("\n📋 Render Deployment Steps:")
    print("1. Go to https://render.com")
    print("2. Sign up for free account")
    print("3. Click 'New +' → 'Web Service'")
    print("4. Connect your GitHub repository")
    print("5. Set environment variables:")
    print("   - FLASK_ENV=production")
    print("   - MONGODB_URI=your_mongodb_atlas_uri")
    print("6. Click 'Create Web Service'")
    
    print("\n🔧 Creating configuration files...")
    create_render_config()
    create_dockerfile()
    
    print("\n✅ Setup complete!")
    print("📱 Your app will be deployed to: https://your-app-name.onrender.com")
    print("💡 Remember to set your MongoDB URI in Render dashboard")

if __name__ == "__main__":
    main() 