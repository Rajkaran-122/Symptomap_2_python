# 📘 Doctor Station - User Manual

**For Healthcare Professionals**

A complete step-by-step guide to using the SymptoMap Doctor Station.

---

## Table of Contents
1. [Getting Started](#getting-started)
2. [Logging In](#logging-in)
3. [Dashboard Overview](#dashboard-overview)
4. [Submitting an Outbreak](#submitting-an-outbreak)
5. [Creating Health Alerts](#creating-health-alerts)
6. [Viewing Your Submissions](#viewing-your-submissions)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)

---

## Getting Started

### What You Need
- ✅ Web browser (Chrome, Firefox, Safari, or Edge)
- ✅ Internet connection
- ✅ Access password: `Doctor@SymptoMap2025`
- ✅ Device: Desktop, tablet, or smartphone

### Accessing the Portal
Open your web browser and go to:
```
http://your-deployment-url.com/doctor
```

Or for local testing:
```
http://localhost:3000/doctor
```

---

## Logging In

### Step 1: Open the Login Page
Navigate to the doctor portal URL. You'll see a clean login interface.

### Step 2: Enter Password
The password is displayed on the login page for convenience:
```
Doctor@SymptoMap2025
```

> **Note**: Password is case-sensitive. Copy it exactly as shown.

### Step 3: Click "Sign In"
After entering the password, click the blue "Sign In" button.

### Step 4: Redirected to Dashboard
Upon successful login, you'll be automatically redirected to the Doctor Station dashboard.

### Security Notes
- Your session lasts 24 hours
- You'll be automatically logged out after this time
- Close your browser when done on shared computers

---

## Dashboard Overview

After logging in, you'll see three main tabs:

### 1. Submit Outbreak Tab
- Report disease outbreaks
- Enter patient counts
- Mark locations on map

### 2. Create Alert Tab
- Broadcast health warnings
- Set severity levels
- Define affected areas

### 3. My Submissions Tab
- View all your past submissions
- See submission timestamps
- Track outbreak reports

### Statistics Cards (Top)
- **Total Submissions**: How many you've submitted
- **Outbreaks**: Number of outbreak reports
- **Alerts**: Number of alerts created

---

## Submitting an Outbreak

### Step-by-Step Guide

#### 1. Click "Submit Outbreak" Tab
This is usually the default active tab.

#### 2. Select Disease Type
Click the dropdown and choose from:
- Dengue
- Malaria
- COVID-19
- Influenza
- Typhoid
- Chikungunya
- Tuberculosis
- Hepatitis A/B/C
- Cholera
- Measles
- Other (specify in description)

#### 3. Enter Patient Count
- Type the number of confirmed or suspected cases
- Must be a positive number
- Example: `45`

#### 4. Select Severity Level
Choose one:
- **Mild** (Green) - Minor outbreak, under control
- **Moderate** (Orange) - Requires attention
- **Severe** (Red) - Critical situation, urgent response needed

#### 5. Enter Location Details

**City:**
- Type the city name
- Example: `Jaipur`

**State:**
- Type the state name
- Example: `Rajasthan`

**Hospital/Location Name:**
- Type the specific facility or area
- Example: `SMS Hospital` or `Civil Lines Area`

#### 6. Mark Location on Map

**Option A: Search for Location**
1. Click the search box above the map
2. Type your city name
3. Select from predefined locations
4. Map will center on that city

**Option B: Click on Map**
1. Find your location on the map visually
2. Click directly on the map
3. A red marker will appear
4. Latitude and longitude auto-fill

**Option C: Manual Coordinates**
1. If you know exact coordinates
2. Enter Latitude (e.g., `26.9124`)
3. Enter Longitude (e.g., `75.7873`)
4. Marker will appear on map

#### 7. Add Description (Optional but Recommended)
Provide context:
- "Reported cases in surrounding neighborhoods"
- "Post-monsoon outbreak"
- "Clustered in specific ward"
- "Contact tracing in progress"

#### 8. Click "Submit Outbreak Report"
- Green success message appears
- Form resets
- Your data is saved immediately

#### 9. Verify on Dashboard
- Open main dashboard: `http://your-url/dashboard`
- Scroll to "Recent Doctor Submissions"
- Your outbreak should appear within 30 seconds

---

## Creating Health Alerts

### When to Create Alerts
- Sudden increase in cases
- New disease detected  
- Public health emergency
- Preventive measures needed
- Water/food contamination
- Vaccination drives

### Step-by-Step Guide

#### 1. Click "Create Alert" Tab

#### 2. Select Alert Type
**Critical** (Red)
- Immediate danger
- Emergency response needed
- Example: "Cholera outbreak in water supply"

**Warning** (Orange)
- Caution required
- Preventive action advised
- Example: "Dengue cases increasing"

**Info** (Blue)
- General information
- Awareness notice
- Example: "Vaccination camp scheduled"

#### 3. Write Alert Title
- Keep it concise (max 100 characters)
- Clear and descriptive
- Examples:
  - "Dengue Alert - Jaipur Region"
  - "Water Contamination Warning"
  - "Flu Season Advisory"

#### 4. Write Alert Message
- Detailed information (max 500 characters)
- What's happening
- What people should do
- Examples:
  - "Increase in dengue cases reported. Use mosquito repellent and remove standing water."
  - "Water contamination detected in Area X. Boil water before drinking."

#### 5. Enter Affected Area
- City or region name
- Example: "Jaipur, Rajasthan" or "Pink City Area"

#### 6. Set Expiry Duration
- How many hours the alert stays active
- Examples:
  - `24` = 1 day
  - `72` = 3 days
  - `168` = 1 week

#### 7. Mark Location on Map
Same as outbreak submission - search, click, or enter coordinates.

#### 8. Click "Create Alert"
- Success message appears
- Alert goes live immediately
- Visible on public dashboard

---

## Viewing Your Submissions

### Access History

#### 1. Click "My Submissions" Tab

#### 2. View List
You'll see all your submissions with:
- Disease type / Alert title
- Submission date and time
- Location
- Status

#### 3. Filter (If Available)
- By date range
- By disease type
- By severity

---

## Best Practices

### Data Accuracy
✅ **Double-check patient counts** - Verify numbers before submitting  
✅ **Precise locations** - Use exact hospital/clinic names  
✅ **Current data** - Report recent cases, not historical  
✅ **Complete information** - Fill all required fields  

### Location Marking
✅ **Use map for accuracy** - Don't guess coordinates  
✅ **Zoom in** - Get as precise as possible  
✅ **Verify marker** - Ensure it's at the right spot  
✅ **Include landmark** - Add hospital or area name  

### Descriptions
✅ **Be specific** - "30 cases in Ward 5" not just "many cases"  
✅ **Add context** - "Post-flood outbreak" or "School cluster"  
✅ **Mention trends** - "Increasing daily" or "Stabilizing"  
✅ **Note interventions** - "Fumigation done" or "Vaccination ongoing"  

### Alerts
✅ **Use appropriate severity** - Don't overuse "Critical"  
✅ **Actionable information** - Tell people what to do  
✅ **Set realistic expiry** - Not too short or too long  
✅ **Update if needed** - Create new alert for updates  

---

## Troubleshooting

### Can't Login

**Problem**: "Invalid password" message

**Solutions**:
1. Copy password exactly: `Doctor@SymptoMap2025`
2. Check for extra spaces
3. Ensure caps are correct
4. Try refreshing the page
5. Clear browser cache

---

### Form Won't Submit

**Problem**: Submit button doesn't work or shows error

**Solutions**:
1. Fill all required fields (red asterisks)
2. Verify patient count is a positive number
3. Ensure location is marked on map
4. Check date is not in future
5. Description should be under 500 characters

---

### Map Not Loading

**Problem**: Black or blank map area

**Solutions**:
1. Check internet connection
2. Refresh the page
3. Try a different browser
4. Disable browser extensions (ad blockers)
5. Clear browser cache

---

### Marker Won't Appear

**Problem**: Click on map but no marker

**Solutions**:
1. Ensure you clicked within India
2. Try zooming in first
3. Use search instead
4. Enter coordinates manually
5. Check JavaScript is enabled

---

### Data Not Showing on Dashboard

**Problem**: Submitted but not visible

**Solutions**:
1. Wait 30-60 seconds (auto-refresh delay)
2. Manually refresh dashboard page
3. Check you submitted successfully (green message)
4. Verify you're on main dashboard, not doctor station

---

### Session Expired

**Problem**: "Please login again" message

**Solution**:
- Sessions last 24 hours
- Login again with the password
- Your previous submissions are saved

---

## Tips for Efficient Use

### Quick Submission
1. Have patient count ready
2. Know exact location beforehand
3. Use search for cities (faster than clicking)
4. Keep description brief but informative

### Multiple Submissions
1. Keep the portal open
2. Submit one at a time
3. Verify each submission
4. Use CSV import for bulk data (see admin)

### Mobile Use
1. Portrait mode works best for forms
2. Landscape for better map view
3. Tap once on map to place marker
4. Pinch to zoom on map

---

## Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| Focus search | `/` |
| Submit form | `Ctrl + Enter` |
| Clear form | `Ctrl + R` |
| Next field | `Tab` |
| Previous field | `Shift + Tab` |

---

## Getting Help

### Documentation
📖 Read other guides:
- [START_HERE.md](./START_HERE.md) - Quick setup
- [PROJECT_SUMMARY.md](./PROJECT_SUMMARY.md) - Technical details
- [QUICK_REFERENCE.md](./QUICK_REFERENCE.md) - Command list

### Support Channels
- Email: support@symptomap.example.com
- Create GitHub issue
- Contact system administrator

### FAQs
**Q: Can I edit a submission?**  
A: Currently no. Submit a new entry with corrected data.

**Q: How often should I submit?**  
A: Submit when you have new data or significant changes.

**Q: Is my data visible immediately?**  
A: Yes, within 30 seconds on the public dashboard.

**Q: Can I delete a submission?**  
A: Contact system administrator for data corrections.

**Q: What if my hospital isn't on the map?**  
A: Click on the map at your location and add the name manually.

---

## Privacy & Data

### What's Collected
- Disease type and count
- Location coordinates
- Hospital/area name
- Your description
- Submission timestamp

### What's NOT Collected
- Patient names
- Personal medical records
- Your identity (beyond "doctor")
- Contact details (unless you add in description)

### Data Usage
- Public health monitoring
- Outbreak tracking
- Statistical analysis
- Dashboard display

### Data Storage
- Secure database
- Automated backups
- No data deletion without admin approval

---

## Conclusion

You're now ready to use the Doctor Station effectively!

### Quick Recap
1. ✅ Login with password
2. ✅ Select "Submit Outbreak" tab
3. ✅ Fill all fields carefully
4. ✅ Mark location on map
5. ✅ Submit and verify
6. ✅ Create alerts when needed

### Remember
- Accuracy is crucial
- Complete all required fields
- Verify location on map
- Check dashboard for confirmation

---

**Thank you for contributing to public health monitoring!** 🏥

Your data helps save lives and control disease spread.

---

*Last Updated: December 2025*  
*Version: 1.0*
