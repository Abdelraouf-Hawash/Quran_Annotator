# Quran_Annotator
This repository is for Annotating the Holy Quran

# Quran Ayah Annotation Tool

## Overview

`Aya_end_PauseMark_Annotator.py` is a Streamlit-based interactive annotation tool for labeling the **end** of Quranic verses with a suitable pause mark.

The application loads the Quran text (Uthmani XML format), displays one ayah at a time, and allows users to annotate each ayah using predefined labels. Annotation progress is tracked and stored in a CSV file.

This tool is designed for research purposes, including:

- Quranic pause mark studies  
- Tajweed / waqf analysis  
- NLP dataset construction  
- Semantic or structural Quran research  

---

## Features

- Displays Quran text in large Arabic font  
- Shows next ayah preview  
- Multiple annotation labels  
- Indicates whether current ayah is already annotated  
- Live annotation progress bar  
- Mobile-friendly layout option  
- Automatic CSV saving of annotations  
- Sidebar navigation (Surah + Ayah jump)  
- Session state tracking  

---

## Installation

### 1. Install dependencies

    pip install -r requirements.txt

### 2. Run the application

    streamlit run Annotator.py



