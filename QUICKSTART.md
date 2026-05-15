# ⚡ Quick Start Guide

## 🚀 Get Running in 3 Steps

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Start Both Servers
Open 2 terminals:

**Terminal 1 - Backend:**
```bash
python main.py
```

**Terminal 2 - Frontend:**
```bash
python app.py
```

### Step 3: Open in Browser
```
http://127.0.0.1:5000
```

---

## 🎯 What Each File Does

### Main Application
- **app.py** - Web interface (Flask)
- **main.py** - API backend (FastAPI)

### Analysis
- **skin_analyzer.py** - Image processing & analysis
- **skin_model.py** - Machine learning model

### Infrastructure
- **config.py** - Settings & configuration
- **logger.py** - Logging system
- **utils.py** - Helper functions
- **constants.py** - Constants & messages

### Tools
- **health_check.py** - Check if servers are running
- **startup.py** - Setup verification

---

## 🔍 Key Features

### 1. Image Analysis
Upload a face photo to get detailed skin analysis

### 2. Skin MBTI
Answer questions about your skin type

### 3. Comprehensive Metrics
- Wrinkles, pores, redness
- Acne, pigmentation, sagging
- Oil balance, skin tone
- Age & gender estimation

### 4. Personalized Advice
Get skincare recommendations

---

## 🛠️ Configuration

### Default Settings
Located in `config.py`:
- Flask port: 5000
- FastAPI port: 8000
- Max file size: 50 MB

### Customize
Edit `config.py` or create `.env` file:
```bash
cp .env.example .env
# Edit .env with your settings
```

---

## 📊 Endpoints

### Web Interface
- `GET /` - Main page
- `POST /analyze` - Upload and analyze

### API
- `GET http://localhost:8000/` - API info
- `GET http://localhost:8000/docs` - API documentation
- `POST http://localhost:8000/analyze-skin` - Analyze (API)

---

## ✅ Health Check

Verify both servers are running:
```bash
python health_check.py
```

Expected output:
```
✓ Flask Frontend: HEALTHY
✓ FastAPI Backend: HEALTHY
```

---

## 🐛 Troubleshooting

### "Port 5000 already in use"
```bash
# Change port in config.py or .env
FLASK_PORT=5001
```

### "Port 8000 already in use"
```bash
# Change port in config.py or .env
FASTAPI_PORT=8001
```

### "Face not detected"
- Use clear frontal face photos
- Try high-quality images
- Ensure good lighting

### "Backend not responding"
- Check if `main.py` is running
- Verify port 8000 is available
- Run `python health_check.py`

### "Dependencies not installed"
```bash
pip install -r requirements.txt
```

---

## 📚 Documentation

- **README.md** - Full documentation
- **UPGRADE_SUMMARY.md** - Detailed changes
- **FINAL_REPORT.md** - Complete report
- **UPGRADE_COMPLETE.md** - Overview
- **.env.example** - Configuration options

---

## 💡 Tips

1. **First Run?** Read README.md
2. **Want Details?** See UPGRADE_SUMMARY.md
3. **Issues?** Check health_check.py
4. **Configure?** Copy and edit .env.example

---

## 🎉 You're Ready!

Your Skin Analysis AI app is ready to use!

Open: **http://127.0.0.1:5000**
