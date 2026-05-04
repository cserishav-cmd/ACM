# 🌾 Rice AI System

A professional, production-grade AI platform for rice crop analysis. It combines **segmentation**, **disease detection**, and **variety classification** into a high-performance intelligent pipeline.

## 📁 Project Structure

```
rice-ai-system/
├── api/            # FastAPI routes, schemas, and main entry
├── src/            # Core ML services (Lazy Loading) and chatbot logic
├── ui/             # React + Vite frontend (STITCH Design)
├── models/         # Centralized ML model weights (.keras)
├── data/           # Essential datasets and processed files
├── utils/          # Standardized helper functions and config
├── app.py          # Unified One-Click Launcher
└── .env            # Centralized environment configuration
```

## 🚀 Quick Start

### 1. Requirements
- Python 3.10+
- Node.js 18+

### 2. Launching the System
We have provided a unified launcher that starts both the backend and frontend simultaneously.

**On Windows:**
```powershell
python app.py
```
*Or use the provided batch file:* `start_backend.bat`

### 3. Features
- **Intelligent Routing**: Automatically detects if an image is a paddy field, a rice plant, or harvested grains.
- **Lazy Model Loading**: Reduces memory footprint by loading weights only when needed.
- **Farming Calculator**: Localized financial planning for Indian farmers with AI-driven yield penalty insights.
- **Weather Insights**: Real-time spraying recommendations based on humidity, wind, and rain probability.

## 🧠 Models

| Model | Task | Path |
|-------|------|------|
| `seg_model.keras` | Rice field segmentation | `models/seg_model.keras` |
| `disease_model.keras` | Disease classification | `models/disease_model.keras` |
| `variety_model.keras` | Variety identification | `models/variety_model.keras` |

## 🛠️ Tech Stack

- **Backend**: Python, FastAPI, TensorFlow/Keras
- **Frontend**: React, Vite, TailwindCSS (Plus Jakarta Sans)
- **AI**: Custom CNN architectures + NVIDIA NIM for Chatbot Advisory

## ⚖️ License
MIT
