# 🌍 NGROK SETUP GUIDE - GLOBAL ACCESS

## 🎯 Why ngrok for SIH Demo?

**Problem**: Your demo only works on local WiFi  
**Solution**: ngrok creates a secure tunnel to make your app accessible from anywhere on the internet!

---

## 📥 Step 1: Download ngrok

### Quick Download:
1. **Visit**: https://ngrok.com/download
2. **Select**: Windows (64-bit)
3. **Download**: ngrok-v3-stable-windows-amd64.zip
4. **Extract**: ngrok.exe to your project folder

### Expected Location:
```
AI-based rockfall risk prediction and alert system/
├── ngrok.exe              ← Place here
├── REACT_DEMO.bat
├── GLOBAL_DEMO.bat
└── ...
```

---

## 🔑 Step 2: Get Free Account

### Sign Up (Free):
1. **Go to**: https://dashboard.ngrok.com/signup
2. **Sign up**: Free account (no credit card needed)
3. **Get authtoken**: https://dashboard.ngrok.com/get-started/your-authtoken

### Authenticate:
```bash
ngrok config add-authtoken YOUR_TOKEN_HERE
```

---

## 🚀 Step 3: Run Global Demo

### Command:
```bash
.\GLOBAL_DEMO.bat
```

### What Happens:
1. ✅ **Backend starts** (Flask API)
2. ✅ **Frontend starts** (React dashboard)  
3. ✅ **ngrok tunnel** creates global URL
4. ✅ **Public URL** generated (like `https://abc123.ngrok.io`)

---

## 🌍 Global Access Benefits

### For SIH Jury:
- 🌐 **Access from anywhere** - No WiFi restrictions
- 📱 **Any device** - Phones, tablets, laptops
- 🔒 **Secure HTTPS** - Professional SSL certificate
- ⚡ **Fast performance** - Global CDN network

### Demo Scenarios:
```
Judge in Mumbai:     https://abc123.ngrok.io
Judge in Delhi:      https://abc123.ngrok.io  
Judge in Bangalore:  https://abc123.ngrok.io
Your presentation:   https://abc123.ngrok.io
```

**Everyone sees the SAME live demo simultaneously!**

---

## 🎯 Usage Examples

### Local Demo:
```bash
.\REACT_DEMO.bat
# URL: http://localhost:3000 (your computer only)
```

### Network Demo:
```bash
.\NETWORK_DEMO.bat  
# URL: http://10.129.21.66:3000 (same WiFi only)
```

### Global Demo:
```bash
.\GLOBAL_DEMO.bat
# URL: https://abc123.ngrok.io (anywhere in the world!)
```

---

## 🔧 Troubleshooting

### Common Issues:

1. **"ngrok.exe not found"**
   - Download from https://ngrok.com/download
   - Place in your project folder

2. **"Authentication required"**  
   - Sign up at https://ngrok.com
   - Run: `ngrok config add-authtoken YOUR_TOKEN`

3. **"Tunnel not working"**
   - Check if React is running on port 3000
   - Restart `.\GLOBAL_DEMO.bat`

---

## 🏆 Perfect for SIH Jury!

### Professional Advantages:
- ✅ **Enterprise-level** deployment demonstration
- ✅ **Global accessibility** shows real-world readiness  
- ✅ **HTTPS security** impresses technical judges
- ✅ **Zero setup** for jury members
- ✅ **Real-time sync** across all devices worldwide

### Jury Instructions:
```
"Please open https://abc123.ngrok.io on any device
Login: admin / admin123
Experience our AI Rockfall System live!"
```

---

## 📊 Comparison Table

| Method | Access Scope | Setup | Professional Level |
|--------|-------------|-------|-------------------|
| REACT_DEMO.bat | Your computer only | Easy | Basic |
| NETWORK_DEMO.bat | Same WiFi network | Medium | Good |
| GLOBAL_DEMO.bat | **Anywhere worldwide** | **Easy** | **Enterprise** |

---

## ✅ Ready for Global Demo

Your AI Rockfall System will be accessible:
- 🌍 **Globally** via secure HTTPS
- 📱 **Any device** with internet connection
- 🎯 **Perfect for remote SIH jury**
- 🚀 **Professional deployment showcase**

**Download ngrok and run `.\GLOBAL_DEMO.bat` for worldwide access!** 🌟