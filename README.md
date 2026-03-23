# 🚀 Parqly – Smart Parking Automation Platform

![Parqly Logo](./static/images/readme/logo.png "Parqly")

**Parqly** is a full-stack smart parking solution that automates vehicle access, tracking, and payments using **Computer Vision (ANPR)** and a seamless **QR-based mobile payment system**.

It eliminates tickets, reduces operational costs, and delivers a fully frictionless **“Park & Pay”** experience.

---

# Vision

Our mission is to digitize and automate parking infrastructure by transforming traditional parking lots into **intelligent, self-operating systems**.

Parqly enables:
- Instant vehicle recognition  
- Ticketless payments  
- Zero human intervention  
- Increased revenue efficiency  

---

# System Architecture

Camera → ANPR Engine → Flask API → Database → Web App → Barrier Control


### Components:

- Camera Feed (IP/Webcam)
- ANPR Engine (Python)
- Backend API (Flask)
- Database (PostgreSQL / Supabase)
- Mobile Web App

---

# Core Components

## 1. Computer Vision Module (ANPR Engine)

The system’s core recognition engine responsible for real-time license plate detection.

### Features:

- Custom-Trained Detection Model: YOLOv8 trained on license plate datasets  
- OCR Recognition: EasyOCR for text extraction  
- Validation Layer: Regex-based plate verification  
- High recognition accuracy under standard conditions  
- Low-latency processing suitable for real-time applications   

---

## 2. Smart Payment Web App

A mobile-first web application with zero installation required.

### Key Features:
- QR Code Access (no app needed)  
- Auto-detected or manually entered plate  
- Real-time fee calculation  
- Instant payment confirmation  

---

# 🖥️ Interface Overview

The system consists of two primary interfaces: the parking terminal and the mobile web application.

## Parking Terminal Interface

Displays real-time feedback at entry/exit points.

- License plate recognition  
- Access granted / payment required  

<p align="center">
  <img src="./static/images/readme/screen2.png" width="315" alt="Access Granted UI">
  &nbsp;&nbsp;&nbsp;&nbsp;
  <img src="./static/images/readme/screen.png" width="315" alt="Terminal Feedback">
</p>

---

## Mobile Payment Application

Allows users to manage and pay for their parking session.

- Search by license plate  
- View duration and cost  
- Complete payment instantly  

<p align="center">
  <img src="./static/images/readme/app.png" width="300" alt="Payment Interface Main">
  &nbsp;&nbsp;&nbsp;&nbsp;
  <img src="./static/images/readme/app2.png" width="300" alt="Payment Processing">
</p>

---

## 3. Backend Services

Central system logic and communication layer.

### Tech Stack:

- Flask API  
- Supabase (PostgreSQL)  

### Responsibilities:

- Manage parking sessions (IN / OUT)  
- Handle payment validation  
- Sync data between ANPR and frontend  
- Maintain logs  

---

# Security

- HTTPS-secured API communication  
- Real-time session validation  
- Audit logs for vehicle activity  

---

# Key Features

| Feature | Description |
|--------|------------|
| Fast Recognition | Instant plate detection |
| Ticketless Access | Fully digital parking |
| Cost Reduction | No staff or machines |
| Eco-Friendly | No paper tickets |
| Real-Time Sync | Instant payment validation |
| Scalable | Multi-location support |

---

# Workflow

1. Vehicle approaches entrance  
2. ANPR detects and reads plate  
3. Session is created (IN)  
4. User pays via web app  
5. Exit camera verifies payment  
6. Barrier opens automatically  

---

# Edge Case Handling

- Failed recognition retry  
- Manual override  
- Invalid plate filtering  

---

# Scalability

- Multi-camera support  
- Cloud backend  
- Horizontal scaling ready  

---

# Getting Started

## Prerequisites

- Python 3.9+  
- Webcam or IP Camera  

---

## Installation

```bash
# Clone the repository
git clone https://github.com/PetarIliev22/Parqly.git

# Install required libraries
pip install -r requirements.txt

# Launch the system
python local_anpr.py