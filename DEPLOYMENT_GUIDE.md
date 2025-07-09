# 🚀 Critical Care Monitor - Deployment Guide

## **🗄️ MongoDB Atlas Setup**

### **Step 1: Create MongoDB Atlas Account**
1. Go to [mongodb.com/atlas](https://mongodb.com/atlas)
2. Click "Try Free" 
3. Create account (free forever)

### **Step 2: Create Database Cluster**
1. Click "Build a Database"
2. Choose **FREE** tier (M0)
3. Select region (closest to you)
4. Click "Create"

### **Step 3: Set Up Database Access**
1. Go to "Database Access" (left sidebar)
2. Click "Add New Database User"
3. Create username/password (save these!)
4. Select "Read and write to any database"
5. Click "Add User"

### **Step 4: Set Up Network Access**
1. Go to "Network Access" (left sidebar)
2. Click "Add IP Address"
3. Click "Allow Access from Anywhere" (for deployment)
4. Click "Confirm"

### **Step 5: Get Connection String**
1. Go back to "Database" tab
2. Click "Connect"
3. Choose "Connect your application"
4. Copy the connection string (looks like):
   ```
   mongodb+srv://username:password@cluster.mongodb.net/healthcare_monitor
   ```

## **🚀 Railway Deployment**

### **Option 1: Automated Deployment**
```bash
# Run the deployment script
python deploy_railway.py
```

### **Option 2: Manual Deployment**
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Initialize project
railway init

# Set environment variables
railway variables set MONGODB_URI="your_mongodb_atlas_uri"
railway variables set FLASK_ENV=production

# Deploy
railway up
```

## **🔧 Environment Variables**

Set these in your Railway dashboard:

| Variable | Value | Description |
|----------|-------|-------------|
| `MONGODB_URI` | `mongodb+srv://...` | Your MongoDB Atlas connection string |
| `FLASK_ENV` | `production` | Production environment |

## **📱 Alternative Platforms**

### **Heroku Deployment**
```bash
# Install Heroku CLI
# Download from: https://devcenter.heroku.com/articles/heroku-cli

# Login and deploy
heroku login
heroku create your-app-name
git add .
git commit -m "Add MongoDB support"
git push heroku main

# Set MongoDB URI
heroku config:set MONGODB_URI="your_mongodb_atlas_uri"
```

### **Vercel Deployment**
```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
vercel

# Set MongoDB URI in Vercel dashboard
```

## **✅ Verification**

After deployment, your app should:
- ✅ Connect to MongoDB Atlas
- ✅ Display patient data
- ✅ Show real-time vitals
- ✅ Allow ML predictions
- ✅ Enable forecasting

## **🔗 Useful Links**

- **MongoDB Atlas**: [mongodb.com/atlas](https://mongodb.com/atlas)
- **Railway**: [railway.app](https://railway.app)
- **Heroku**: [heroku.com](https://heroku.com)
- **Vercel**: [vercel.com](https://vercel.com)

## **🆘 Troubleshooting**

### **Common Issues:**

1. **MongoDB Connection Failed**
   - Check your connection string
   - Verify network access is set to "Allow from anywhere"
   - Ensure username/password are correct

2. **Deployment Failed**
   - Check Railway logs: `railway logs`
   - Verify all dependencies are in `requirements.txt`
   - Ensure environment variables are set

3. **App Not Loading**
   - Check if MongoDB is connected
   - Verify the app is running: `railway status`
   - Check the deployment URL

### **Get Help:**
- Check Railway logs: `railway logs`
- View app status: `railway status`
- Open app: `railway open` 