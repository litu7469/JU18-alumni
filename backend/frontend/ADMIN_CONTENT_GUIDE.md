# Admin Content Management Guide
## Editable Content Sections for Phase 4

---

## 📝 Overview

This document lists all content sections that will be **editable by administrators** in Phase 4 when the Admin Panel is implemented. Currently, these sections are hardcoded in HTML files.

---

## 🏠 **HOME PAGE** (index.html)

### 1. Image Slider (5 Slides)
**Location**: Top of homepage  
**Current**: Lines 84-130 in index.html

**Editable Fields**:
- Image file (upload new image)
- Slide heading (main text)
- Slide caption (subtext)
- Display order
- Active/Inactive status

**Example**:
```
Slide 1:
- Image: slide1.jpg
- Heading: "Welcome to JU 18th Batch Alumni Association"
- Caption: "জাহাঙ্গীরনগর বিশ্ববিদ্যালয় ১৮তম ব্যাচে স্বাগতম"
```

---

### 2. Statistics Section
**Location**: Below slider  
**Current**: Lines 134-157 in index.html

**Editable Fields**:
- Members count (e.g., "400+")
- Batch years (e.g., "1996-2000")
- Countries (e.g., "25+")
- Events organized (e.g., "50+")

---

### 3. Welcome Text
**Location**: Welcome Section  
**Current**: Lines 161-176 in index.html

**Editable Fields**:
- English welcome text (paragraph)
- Bangla welcome text (paragraph)

---

### 4. Vision & Mission
**Location**: VM Cards Section  
**Current**: Lines 181-201 in index.html

**Editable Fields**:
- Vision statement (paragraph)
- Mission statement (paragraph)
- Values statement (paragraph)

---

### 5. Latest Announcements
**Location**: News Grid Section  
**Current**: Lines 205-227 in index.html

**Editable Fields per announcement**:
- Date (e.g., "February 20, 2026")
- Headline (e.g., "Website Launch Announcement")
- Summary text (paragraph)
- Link URL
- Display order
- Active/Inactive status

**Admin Actions**:
- Add new announcement
- Edit existing announcement
- Delete announcement
- Reorder announcements

---

### 6. Upcoming Events
**Location**: Events Grid Section  
**Current**: Lines 231-269 in index.html

**Editable Fields per event**:
- Event date (day + month)
- Event title
- Event description
- Location
- Time
- Display order
- Active/Inactive status

**Admin Actions**:
- Add new event
- Edit existing event
- Delete event
- Mark as past event (moves to archive)

---

### 7. President's Message
**Location**: Messages Section  
**Current**: Lines 291-300 in index.html

**Editable Fields**:
- Message content (multiple paragraphs)
- Author name/title
- Display/Hide status

---

## 📘 **ABOUT PAGE** (about.html - To Be Created)

### 1. History Timeline
**Editable Fields per timeline item**:
- Year
- Event description
- Icon/image (optional)
- Display order

---

### 2. Mission & Vision Statements
**Editable Fields**:
- Mission statement (full text)
- Vision statement (full text)
- Last updated date

---

### 3. Objectives List
**Editable Fields per objective**:
- Objective text
- Display order
- Active/Inactive status

**Admin Actions**:
- Add new objective
- Edit existing objective
- Delete objective
- Reorder objectives

---

### 4. Executive Committee
**Editable Fields per committee member**:
- Profile photo (upload image)
- Full name
- Position/Title (e.g., "President", "Vice President")
- Department
- Batch year
- Email (optional)
- Phone (optional)
- Display order
- Active/Inactive status

**Admin Actions**:
- Add new member
- Edit existing member
- Remove member
- Change display order
- Bulk import from Excel/CSV

---

## 📞 **CONTACT PAGE** (contact.html - To Be Created)

### 1. Contact Information
**Editable Fields**:
- Email address
- Phone number
- Office address
- Google Maps embed link/coordinates

---

### 2. Social Media Links
**Editable Fields per social link**:
- Platform name (Facebook, LinkedIn, etc.)
- Profile URL
- Display order
- Active/Inactive status

---

### 3. Office Hours
**Editable Fields**:
- Working days
- Opening time
- Closing time
- Special notes (holidays, etc.)

---

## 🔧 **GLOBAL SETTINGS** (All Pages)

### 1. Header/Logo
**Editable Fields**:
- University logo (upload image)
- Site title (English)
- Site title (Bangla)

---

### 2. Navigation Menu
**Editable Fields per menu item**:
- Menu text
- Link URL
- Display order
- Active/Inactive status
- Dropdown items (for submenus)

---

### 3. Footer Content
**Editable Fields**:
- Copyright text
- Contact email
- Contact phone
- Address
- Social media links
- Quick links

---

## 📊 **ADMIN PANEL FEATURES** (Phase 4)

### Content Management System (CMS)
1. **Dashboard**
   - View all content sections
   - Recent changes log
   - Pending approvals

2. **Editor Interface**
   - Rich text editor (WYSIWYG)
   - Image uploader
   - Preview before publish
   - Save as draft
   - Schedule publication

3. **Image Management**
   - Upload images
   - Resize/crop tools
   - Image library browser
   - Delete unused images

4. **Content Versioning**
   - View revision history
   - Revert to previous version
   - Compare versions

---

## 🎨 **STYLING CUSTOMIZATION** (Advanced)

### Theme Settings (Phase 4+)
**Editable via Admin Panel**:
- Primary color
- Accent color
- Font family
- Button styles
- Heading styles

---

## 📝 **DATABASE STRUCTURE** (Phase 2)

When backend is implemented, content will be stored in PostgreSQL tables:

### Tables Needed:
```sql
-- Slider images
slider_images (
    id, image_url, heading, caption, display_order, is_active
)

-- Announcements/News
announcements (
    id, date, title, content, link, display_order, is_active
)

-- Events
events (
    id, date, title, description, location, time, is_past, display_order
)

-- Executive Committee
committee_members (
    id, name, position, department, photo_url, email, phone, display_order
)

-- Settings (key-value pairs)
site_settings (
    key, value, last_updated
)
```

---

## 🔐 **ADMIN ACCESS CONTROL**

### Permission Levels:
1. **Super Admin**
   - Full access to all content
   - Can add/edit/delete
   - User management

2. **Content Editor**
   - Edit existing content
   - Cannot delete
   - Cannot manage users

3. **Moderator**
   - Approve/reject submissions
   - Limited editing

---

## 📸 **IMAGE SPECIFICATIONS**

### Homepage Slider:
- **Size**: 1920x1080px (Full HD)
- **Format**: JPG, optimized
- **File size**: < 500KB per image
- **Aspect ratio**: 16:9

### Committee Member Photos:
- **Size**: 400x400px
- **Format**: JPG or PNG
- **File size**: < 200KB
- **Aspect ratio**: 1:1 (square)

### Logo:
- **Size**: 200x200px minimum
- **Format**: PNG with transparency
- **File size**: < 100KB

---

## 🚀 **CONTENT PUBLISHING WORKFLOW**

### Typical Admin Flow:
1. Login to admin panel
2. Navigate to content section
3. Click "Edit" button
4. Make changes in editor
5. Preview changes
6. Save as draft OR Publish immediately
7. Changes appear on live site

### For Images:
1. Click "Upload Image"
2. Select file from computer
3. Crop/resize if needed
4. Add alt text (for accessibility)
5. Save
6. Image appears in content

---

## 📅 **CONTENT UPDATE SCHEDULE** (Recommended)

### Weekly Updates:
- Latest announcements
- Upcoming events

### Monthly Updates:
- President's message
- Statistics (if changed)

### Quarterly Updates:
- Executive committee changes
- Mission/vision refinements

### Yearly Updates:
- History timeline
- Major site redesigns

---

## ✅ **CONTENT APPROVAL WORKFLOW** (Phase 4)

### Multi-Step Approval:
1. **Content Editor** creates/edits content
2. **Senior Editor** reviews
3. **President/Admin** final approval
4. Content goes live

---

## 🔔 **NOTIFICATIONS** (Phase 4)

### Admin Receives Notifications For:
- New member registrations (pending approval)
- Content submission (memories, messages)
- System updates
- Security alerts

---

## 📖 **ADMIN TRAINING MATERIALS** (To Be Created)

### Documentation Needed:
1. Admin Panel User Guide (PDF)
2. Video tutorials (screen recordings)
3. Quick reference cards
4. Troubleshooting guide
5. FAQ document

---

## 🎯 **BEST PRACTICES FOR ADMINS**

### Content Guidelines:
1. **Keep it concise** - Users scan, not read
2. **Use active voice** - More engaging
3. **Add images** - Visual appeal
4. **Proofread** - Check spelling/grammar
5. **Test links** - Ensure they work
6. **Mobile preview** - Check on phone
7. **Backup** - Download content before major changes

---

## 🆘 **CONTENT BACKUP & RECOVERY**

### Automated Backups (Phase 5):
- Daily database backups
- Image backups
- Version history
- One-click restore

### Manual Backups:
- Download content as JSON
- Export to Excel/CSV
- Save images locally

---

**This guide will be implemented in Phase 4 with full admin panel functionality.**

Current Phase: **Phase 1 - Static Frontend**  
Next Phase: **Phase 2 - Backend Integration**
