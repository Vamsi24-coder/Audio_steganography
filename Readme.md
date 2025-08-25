# 🎵 Audio Steganography using LSB with Enterprise Security Framework

A professional, enterprise-grade audio steganography application that securely hides messages, images, and documents inside WAV and FLAC audio files using advanced LSB (Least Significant Bit) techniques combined with multi-layer security architecture.

## 🌟 Key Features

**-  Multi-Layer Security Architecture:** Advanced steganography system combining **AES-256 encryption, LSB algorithm, and 7-Zip password protection** for triple-layer data security, ensuring enterprise-grade protection with recipient email verification that prevents unauthorized decoding attempts.

**-  Professional User Management System:** Comprehensive **user authentication and database management** system with SQLite integration, operation history tracking, and secure folder organization, transforming basic LSB steganography into a professional-grade application with complete audit trails.

**-  Advanced Audio Processing Pipeline:** Robust **multi-format audio handler** supporting WAV and FLAC with real-time audio preview, capacity estimation, and intelligent payload embedding, packaged as a standalone executable for easy deployment without technical dependencies.



### Run from Source
```bash
# Clone the repository
git clone https://github.com/your-username/audio-steganography-lsb.git
cd audio-steganography-lsb

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

## 📋 System Requirements

### For Executable Version
- **OS:** Windows 8/10/11 (64-bit recommended)
- **RAM:** 4GB minimum, 8GB recommended
- **Storage:** 100MB free space
- **Additional:** 7-Zip for secure archives

### For Source Code
- **Python:** 3.8 or higher
- **OS:** Windows, Linux, macOS
- **Dependencies:** Listed in `requirements.txt`

## 🔧 Dependencies

```txt
numpy>=1.21.0          # Audio processing
soundfile>=0.12.1      # Audio file handling
cryptography>=41.0.0   # AES-256 encryption
bcrypt>=4.0.0          # Password security
pillow>=10.0.0         # Image processing
PyPDF2>=3.0.0          # PDF handling
py7zr>=0.20.0          # Secure archive creation
pygame>=2.5.0          # Audio preview
scipy>=1.7.0           # Advanced audio processing
```

## 💻 Usage Guide

### 🔐 Encoding (Hiding Data)
1. **Create Account** → Register with email and secure password
2. **Select "Encode"** → Choose data type (Message/Image/PDF)
3. **Choose Audio File** → Select WAV or FLAC format
4. **Enter Recipient Email** → For secure delivery verification
5. **Hide Data** → Embed your secret with encryption
6. **Save Result** → Secure archive or regular file

### 🔓 Decoding (Extracting Data)
1. **Login** → Use recipient email account
2. **Select "Decode"** → Choose encoded audio file
3. **Enter Key** → Decryption key from sender
4. **Extract Data** → Retrieve hidden content securely
5. **Organize Files** → Auto-sorted in secure folders

## 🏗️ Architecture Overview

```
┌─ GUI Layer (Tkinter)
├─ Application Logic
│  ├─ User Authentication
│  ├─ Audio Format Handler
│  └─ Steganography Engine
├─ Security Layer
│  ├─ AES-256 Encryption
│  ├─ Email Verification
│  └─ 7-Zip Protection
├─ Data Layer
│  ├─ SQLite Database
│  └─ File System
└─ Integration
   ├─ Audio Preview
   └─ Secure Archives
```

## 🔒 Security Features

- **🛡️ Triple-Layer Protection:** LSB + AES-256 + 7-Zip archives
- **📧 Email Verification:** Recipient authentication system
- **👤 User Isolation:** Personal databases and secure folders
- **📊 Audit Trails:** Complete operation logging and history
- **🔑 Key Management:** Secure key generation and storage

## 🎯 Supported Formats

### Audio Input/Output
- **WAV:** Uncompressed PCM audio
- **FLAC:** Lossless compressed audio

### Hidden Data Types
- **📝 Text Messages:** Up to 255 characters
- **🖼️ Images:** JPG format support
- **📄 Documents:** PDF file embedding

## 📁 Project Structure

```
audio-steganography-lsb/
├── main.py                    # Application entry point
├── steganography_utils.py     # Core LSB algorithms
├── database.py               # SQLite database management
├── secure_folder_manager.py  # 7z archive handling
├── audio_format_handler.py   # WAV/FLAC processing
├── gui/                      # User interface modules
│   ├── main_window.py
│   ├── encode_gui.py
│   ├── decode_gui.py
│   └── secure_folder_gui.py
├── requirements.txt          # Python dependencies
├── logo1.png                # Application logo
└── README.md                # This file
```



## ❓ Troubleshooting

### Common Issues

**🔴 "Invalid decryption key" error:**
- ✅ Verify key format (44 characters, base64)
- ✅ Check recipient email matches logged-in user
- ✅ Ensure no extra spaces in key

**🔴 "7z files won't open" error:**
- ✅ Install 7-Zip from [official website](https://www.7-zip.org/)
- ✅ Fix file associations in Windows settings
- ✅ Run installation as Administrator

**🔴 "Memory error" when processing:**
- ✅ Use smaller audio files for testing
- ✅ Close other applications to free RAM
- ✅ Try Google Colab for cloud processing


**Developed by Supraja Technologies Team:**
-vamsi vamsimanne2004@gmail.com
## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -am 'Add feature'`
4. Push to branch: `git push origin feature-name`
5. Submit pull request

## 📄 Li


## 🙏 Acknowledgments

- **Cryptography Library:** Advanced encryption standards
- **Audio Processing:** NumPy, SciPy, and SoundFile libraries
- **Secure Archives:** 7-Zip for password protection
- **GUI Framework:** Tkinter for cross-platform interface

***

**⚠️ Legal Notice:** This software is for educational and legitimate privacy purposes only. Users are responsible for compliance with applicable laws and regulations.

**🔒 Your secrets are safe with enterprise-grade security!** Built for real-world privacy protection and professional steganographic applications.

[1](https://www.youtube.com/watch?v=eVGEea7adDM)
[2](https://www.thegooddocsproject.dev/template/readme)
[3](https://www.drupal.org/docs/develop/managing-a-drupalorg-theme-module-or-distribution-project/documenting-your-project/readmemd-template)
[4](https://csc-knu.github.io/sys-prog/books/Andrew%20S.%20Tanenbaum%20-%20Computer%20Networks.pdf)
[5](https://www.slideshare.net/slideshow/audio-steganography-project-presentai/47135492)
[6](https://projectgurukul.org/python-image-steganography/)
[7](https://stackoverflow.com/questions/44185716/add-audio-in-github-readme-md)
[8](https://dev.to/yuridevat/how-to-create-a-good-readmemd-file-4pa2)
