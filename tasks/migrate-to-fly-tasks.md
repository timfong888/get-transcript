# Migrate YouTube Transcript Function to Fly.io - FAST TRACK

## 🎯 **Project Overview**

**Objective**: Migrate YouTube Transcript API function from Firebase Functions to Fly.io to resolve proxy authentication issues with Webshare residential proxies.

**Problem**: Google Cloud Functions blocks proxy authentication (407 Proxy Authentication Required) despite correct credentials and configuration.

**Solution**: Deploy to Fly.io which provides full container control and minimal network restrictions.

**Timeline**: 10 minutes - Focus on core proxy authentication fix first!

---

## 🚀 **PRIORITY 1: Core Migration (10 minutes)**

### **Step 1: Quick Fly.io Setup** [2 minutes]
- [ ] Install Fly.io CLI: `brew install flyctl`
- [ ] Login to Fly.io: `flyctl auth login`
- [ ] Create account if needed (use existing if available)

### **Step 2: Convert to FastAPI Web Server** [3 minutes]
- [ ] Create simple FastAPI app from Firebase Function
- [ ] Convert `@https_fn.on_request` to FastAPI route
- [ ] Keep existing proxy configuration code
- [ ] Add basic health check endpoint

### **Step 3: Create Deployment Files** [2 minutes]
- [ ] Create minimal Dockerfile (Python 3.12 + FastAPI)
- [ ] Generate fly.toml with US region, smallest machine size
- [ ] Update requirements.txt (remove Firebase, add FastAPI)

### **Step 4: Deploy and Test Proxy** [3 minutes]
- [ ] Set Webshare secrets: `flyctl secrets set WEBSHARE_USERNAME=... WEBSHARE_PASSWORD=...`
- [ ] Deploy: `flyctl deploy`
- [ ] **CRITICAL TEST**: Verify proxy authentication works (no 407 errors)
- [ ] Test YouTube transcript retrieval

---

## 📋 **PRIORITY 2: Optimization Phases (After Core Works)**

### **Phase A: Basic Improvements**
#### A.1 Add Simple Retry Logic
- [ ] Basic exponential backoff for proxy failures
- [ ] Simple error handling for 407 errors
- [ ] Basic logging to Google Cloud Logging

#### A.2 Cost Optimization
- [ ] Verify smallest machine size works
- [ ] Configure auto-scaling (min 0, max 1 initially)
- [ ] Monitor costs vs Firebase Functions

### **Phase B: Enhanced Features**
#### B.1 Simple Caching (if ≤5 lines of code)
- [ ] In-memory cache for frequent requests
- [ ] Skip if implementation is complex

#### B.2 Monitoring Setup
- [ ] Configure Google Cloud Logging integration
- [ ] Basic health monitoring
- [ ] Simple error alerts

### **Phase C: Documentation and Backup**
#### C.1 Documentation
- [ ] Update README with Fly.io deployment
- [ ] Document migration process
- [ ] Create troubleshooting guide

#### C.2 Backup Strategy
- [ ] Keep Firebase Functions deployment active
- [ ] Document rollback procedure
- [ ] Test both deployments work

---

## 🎯 **Success Criteria**

### **Primary Goals (10 minutes)**
- ✅ **Proxy Authentication Works**: No more 407 errors in Fly.io environment
- ✅ **YouTube Transcript Retrieval**: Full functionality maintained
- ✅ **Cost Lower than Firebase Functions**: Verify costs are reduced

### **Secondary Goals (After core works)**
- ✅ **Basic Monitoring**: Google Cloud Logging integration
- ✅ **Simple Documentation**: Basic deployment and rollback procedures
- ✅ **Backup Strategy**: Keep Firebase Functions as fallback

---

## 📊 **Risk Mitigation**

### **Primary Risk**
1. **Proxy still doesn't work**: Keep Firebase Functions as immediate fallback

### **Mitigation Strategy**
- Deploy quickly to test core functionality
- Keep existing Firebase deployment active during testing
- Focus on proxy authentication first, optimize later

---

## 🚀 **Getting Started - IMMEDIATE ACTION**

**Current Status**: Ready to start 10-minute migration

**Next Steps (in order)**:
1. `brew install flyctl && flyctl auth login`
2. Convert Firebase Function to FastAPI
3. Create Dockerfile and fly.toml
4. Deploy and test proxy authentication

**Timeline**: 10 minutes for core migration, then optimize as needed
