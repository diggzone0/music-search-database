# 🎵 music-database

A Python-based music search tool that queries a **local database** for fast lookups and falls back to **online sources** for deeper search results.

---

## 📌 Overview

`musicdb.py` is a command-line utility designed to provide fast and comprehensive music search capabilities:

- ⚡ **Local Search** — Queries a local database for instant results
- 🌐 **Online Search** — Falls back to online sources when deeper results are needed
- 🐍 **Python-powered** — Lightweight and easy to run on any system with Python 3

---

## 🖥️ Environment

| Component | Details          |
|-----------|-----------------|
| OS        | Fedora 43 (WSL) |
| Host      | Windows 11      |
| Runtime   | Python 3        |
| VCS       | Git             |

---

## 🚀 How to Run
```bash
python3 musicdb.py
```

---

## 🔍 How It Works

1. User enters a search query
2. Script checks the **local database** first for fast results
3. If results are limited, it performs an **online lookup**
4. Results are displayed in the terminal

---

## 📁 Project Structure
```
music-database/
├── musicdb.py          # Main Python script
├── .gitignore       # Git ignore rules
└── README.md        # Project documentation
```

---

## ⚙️ Requirements

- Python 3.x
- Internet connection (for online search feature)

---

## 📝 Notes

- This project was built with AI assistance and runs in a WSL (Windows Subsystem for Linux) environment
- Script is executed directly via `python3 musicdb.py`

