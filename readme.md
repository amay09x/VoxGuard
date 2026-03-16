# VoxGuard: AI Threat Analysis System

**VoxGuard** is a real-time cybersecurity tool designed to detect AI-generated deepfakes and social engineering scams in voice notes. By analyzing both the biometric "voiceprint" and the linguistic intent of a message, VoxGuard provides a comprehensive security report to protect users from high-tech fraud.

Built as a hackathon project, this system bridges the gap between complex AI threat detection and an intuitive, user-friendly interface.

## Features
* **Biometric Audio Processing:** Converts raw audio into highly accurate text using Azure's enterprise-grade Speech Services.
* **Intent Analysis Engine:** Utilizes Google's Gemini 2.5 Flash model to perform behavioral analysis on the transcript, identifying psychological manipulation, urgency triggers, and scam playbooks.
* **Threat Scoring:** Generates a quantifiable "Risk Score" (0-100%) alongside clear, actionable bullet points explaining the red flags.
* **Modern UI:** A sleek, Cyberpunk-themed web dashboard built with Python Streamlit for frictionless drag-and-drop analysis.

## Tech Stack
* **Frontend:** Streamlit (Python)
* **Audio Processing (The "Ears"):** Azure Cognitive Services (Speech-to-Text SDK)
* **Threat Intelligence (The "Brain"):** Google GenAI (`gemini-2.5-flash`)
* **Environment Management:** `python-dotenv`

## Getting Started

Follow these steps to run VoxGuard locally on your machine.

### Prerequisites
1. Python 3.9+ installed.
2. An **Azure** account with a Speech Services resource (Key & Region).
3. A **Google AI Studio** account with a Gemini API Key.

### Installation

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/amay09x/VoxGuard.git](https://github.com/amay09x/VoxGuard.git)
   cd VoxGuard