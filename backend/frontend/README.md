# JU 18th Batch Alumni Association Website
## Complete Project Structure

**Project**: Jahangirnagar University 18th Batch Alumni Website  
**Version**: 1.0  
**Status**: Phase 1 - Static Frontend  

---

## 📁 Folder Structure

```
ju18-alumni-website/
├── index.html              # Homepage (COMPLETE)
├── pages/
│   ├── about.html          # About us page
│   ├── contact.html        # Contact page
│   ├── register.html       # Registration form
│   └── login.html          # Login form
├── assets/
│   └── images/
│       ├── ju-logo.png     # University logo (ADD YOUR IMAGE)
│       └── slider/
│           ├── slide1.jpg  # Slider image 1 (ADD YOUR IMAGE)
│           ├── slide2.jpg  # Slider image 2 (ADD YOUR IMAGE)
│           ├── slide3.jpg  # Slider image 3 (ADD YOUR IMAGE)
│           └── slide4.jpg  # Slider image 4 (ADD YOUR IMAGE)
├── css/
│   └── style.css           # External stylesheet (optional)
├── js/
│   └── main.js             # External JavaScript (optional)
└── README.md               # This file
```

---

## 🚀 Quick Start

1. **Test the website:**
   ```bash
   # Simply open index.html in your browser
   # It works with placeholder images!
   ```

2. **Add your images:**
   - Copy JU logo to `assets/images/ju-logo.png`
   - Copy slider images to `assets/images/slider/`
   - Edit `index.html` line 508 and lines 544-580 to use your images

3. **Customize content:**
   - Edit text directly in HTML files
   - Modify events, messages, contact info

---

## 📝 Content to Customize

### Homepage (index.html)
- Line 509: University logo path
- Lines 510-511: Site titles (English & Bangla)
- Lines 544-580: Slider images and captions
- Lines 601-617: Vision & Mission text
- Lines 623-660: Event details (dates, titles, descriptions)
- Lines 666-669: President's message
- Lines 676-677: Footer contact info

### About Page (pages/about.html)
- History timeline
- Executive committee members
- Mission & vision details

### Contact Page (pages/contact.html)
- Contact form
- Email, phone, address
- Google Maps location

---

## 🖼️ Image Specifications

### Logo (assets/images/ju-logo.png)
- Size: 200x200px minimum
- Format: PNG with transparent background
- Official JU logo

### Slider Images (assets/images/slider/)
- Size: 1920x1080px (Full HD)
- Format: JPG
- File size: < 500KB each
- Images needed:
  - slide1.jpg - JU campus view
  - slide2.jpg - Alumni reunion
  - slide3.jpg - University buildings
  - slide4.jpg - Graduation ceremony

---

## 📱 Features

- ✅ Responsive design (mobile, tablet, desktop)
- ✅ Auto-playing image slider
- ✅ Dropdown navigation menus
- ✅ Hover effects and animations
- ✅ Clean, professional design
- ✅ No external dependencies

---

## 🔧 Customization

### Change Colors
Edit the CSS in `<style>` section of index.html:
- Primary: `#1e3c72` (line 22)
- Secondary: `#2a5298` (line 22)
- Accent: `#ff6b6b` (line 76)

### Change Slider Speed
Edit JavaScript in `<script>` section:
- Line 716: Change 5000 (5 seconds)

---

## 📞 Support

**Developer**: Md. Latiful Islam  
**Project**: JU 18th Batch Alumni Association  
**Phase**: 1 of 5 (Static Frontend)  

---

## ✅ Next Steps

After completing frontend:
- Phase 2: Backend (FastAPI + PostgreSQL)
- Phase 3: Member Portal (Authentication)
- Phase 4: Admin Panel (Content Management)
- Phase 5: Deployment (Live Website)

---

**Status**: ✅ Ready to Use!
