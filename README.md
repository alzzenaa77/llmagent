# 🗓️ Schedbot Discord - LLM Agent untuk Manajemen Jadwal
SchedBot merupakan chatbot Discord berbasis Large Language Model (LLM) yang memanfaatkan API Google Gemini AI dan dirancang untuk membantu pengguna dalam mengatur dan menyusun jadwal harian secara otomatis melalui integrasi langsung dengan Google Calendar. <br>

Anggota Kelompok: <br>
| Nama Lengkap | NIM |
|---------------|-------------------|
| Della Febi Alfian | 22/505892/TK/55393 |
| Raffa Alzena Zhafirah | 22/505656/TK/55353 |

## 🚀 Fitur Utama Schedbot
1. **Create Jadwal**<br> 
Mengembangkan chatbot berbasis Large Language Model sebagai asisten manajemen jadwal sederhana untuk membantu pengguna mencatat dan menyusun aktivitas harian yang terintegrasi dengan Google Calendar. <br>
<img width="1493" height="535" alt="image" src="https://github.com/user-attachments/assets/95fcd383-1d6d-4b59-9d90-664a91ba47c0" />

2. **Read Jadwal**<br> 
Menampilkan daftar jadwal yang sudah tersimpan agar pengguna mudah mengecek aktivitas.<br>
<img width="1508" height="752" alt="image" src="https://github.com/user-attachments/assets/1ddaa227-4701-4aea-8502-d2117bd92925" />

3. **Update Jadwal**<br> 
Mengubah detail jadwal yang sudah tersimpan tanpa perlu menghapusnya.<br>
<img width="1505" height="759" alt="image" src="https://github.com/user-attachments/assets/4b6b0b38-63e4-4c65-a58d-2f9444193f5b" />

4. **Delete Jadwal**<br> 
Menghapus jadwal tertentu bila sudah tidak diperlukan.<br>
<img width="1492" height="452" alt="image" src="https://github.com/user-attachments/assets/79947222-a8ce-434e-9b77-d93a188046ca" />

5. **Conversational AI** </br>
Berinteraksi dengan user melalui Discord bot <br>
<img width="979" height="643" alt="image" src="https://github.com/user-attachments/assets/c06bfa99-f418-495a-9bcd-74bda37db3fd" />

🔧 Installation
1. Clone Repository
bashgit clone https://github.com/yourusername/schedbot.git
cd schedbot
2. Create Virtual Environment
bash# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python -m venv venv
source venv/bin/activate
3. Install Dependencies
bashpip install -r requirements.txt

# Install package in editable mode for development
pip install -e .

⚙️ Configuration
Step 1: Get Google Calendar API Credentials

Go to Google Cloud Console
Create New Project (or select existing)

Click "Select a project" → "New Project"
Name it (e.g., "SchedBot")
Click "Create"


Enable Google Calendar API

Go to "APIs & Services" → "Library"
Search "Google Calendar API"
Click "Enable"


Create OAuth 2.0 Credentials

Go to "APIs & Services" → "Credentials"
Click "Create Credentials" → "OAuth client ID"
If prompted, configure OAuth consent screen:

User Type: External
App name: SchedBot
User support email: your-email@gmail.com
Add test users (your email)


Application type: Desktop app
Name: SchedBot Desktop
Click "Create"


Download Credentials

Click "Download JSON" button
Save as credentials.json


Place Credentials File

bash   mkdir credentials
   mv ~/Downloads/client_secret_*.json credentials/credentials.json
Step 2: Get Google Gemini API Key

Go to Google AI Studio
Create API Key

Click "Create API Key"
Select your Google Cloud project
Copy the API key



Step 3: Setup Environment Variables
Create a .env file in the project root:
bash# .env file
GEMINI_API_KEY=your_gemini_api_key_here
DISCORD_TOKEN=your_discord_bot_token_here  # Optional, for Discord bot
⚠️ Security Note: Never commit .env file to git! It's already in .gitignore.
Step 4: Verify Directory Structure
Ensure your directory looks like this:
schedbot/
├── credentials/
│   ├── credentials.json    # Google OAuth credentials
│   └── token.json          # Auto-generated after first auth
├── .env                    # Environment variables
├── agent/
├── bot/
└── tests/

🚀 Usage
Option 1: CLI Mode (Command Line Interface)
Use the interactive command-line interface:
bashpython main.py
Example Commands:
You: tambahkan meeting besok jam 2 siang
Bot: ✅ Event "Meeting" berhasil ditambahkan untuk 2025-10-31 14:00

You: apa jadwalku hari ini?
Bot: 📅 Jadwal kamu hari ini:
     1. Morning Standup - 09:00
     2. Team Meeting - 14:00

You: hapus event morning standup
Bot: ✅ Event "Morning Standup" berhasil dihapus

You: exit
Bot: Bye! 👋
Option 2: Discord Bot
Run the Discord bot:
bashpython -m bot.discord_bot
Discord Commands:
!schedbot tambahkan rapat besok jam 3
!schedbot jadwalku minggu ini
!schedbot help
!schedbot clear
First Run: Google Calendar Authentication
On the first run, you'll need to authenticate:

Browser will open automatically
Select your Google account
Click "Allow" to grant calendar access
Close browser after seeing "Authentication successful"

A token.json file will be created in credentials/ folder for future use.

🧪 Testing
Run All Tests
bash# Run all tests with verbose output
pytest -v

# Run specific test file
pytest tests/test_calendar_agent.py -v
pytest tests/test_calendar_tools.py -v
pytest tests/test_llm_integration.py -v

# Run with coverage report
pytest --cov=agent --cov-report=html

   
LLMAGENT/
├─ agent/
│  ├─ tools/
│  │  ├─ __init__.py                # Inisialisasi modul tools
│  │  ├─ calendar_tools.py          # Fungsi utilitas kalender (membuat, membaca, mengedit event)
│  │  ├─ calendar_agent.py          # Agent pengelola event kalender
│  │  └─ llm_agent.py               # Logika inti dan reasoning untuk LLM Agent
│  │
│  ├─ bot/
│  │  └─ discord_bot.py             # Integrasi bot dengan platform Discord
│
│  ├─ credentials/
│  │  ├─ credentials.json           # Data client API untuk autentikasi
│  │  └─ token.json                 # Token hasil autentikasi OAuth
│
├─ tests/
│  ├─ conftest.py                   # Setup dan konfigurasi awal pytest
│  ├─ test_calendar_agent.py        # Unit test untuk modul calendar_agent
│  ├─ test_calendar_tools.py        # Unit test untuk modul calendar_tools
│  ├─ test_llm_integration.py       # Pengujian integrasi agent LLM dengan modul lain
│  ├─ test_agent.py                 # Pengujian agent secara keseluruhan
│  ├─ test_simple.py                # Pengujian fungsi dasar/sederhana
│  └─ test_tools_wrapper.py         # Test wrapper untuk tool tambahan
│
├─ credentials/                     # Direktori penyimpanan file autentikasi API
│
├─ htmlcov/                         # Hasil laporan coverage testing
├─ logs/                            # Log aktivitas sistem
├─ node_modules/                    # Dependensi npm untuk integrasi linting atau bot
│
├─ .env                             # Variabel lingkungan (API keys, tokens, dsb)
├─ .coverage                        # File hasil coverage testing pytest
├─ .gitignore                       # File yang dikecualikan dari pelacakan Git
├─ list_model.py                    # Daftar model atau konfigurasi LLM yang digunakan
├─ main.py                          # Entry point utama untuk menjalankan agent
├─ package.json                     # Konfigurasi dan dependensi npm
├─ package-lock.json                # Lock file versi npm dependencies
├─ pytest.ini                       # Konfigurasi pytest
├─ README.md                        # Dokumentasi proyek
├─ requirements.txt                 # Dependensi Python
└─ setup.py                         # File instalasi dan distribusi package


```
## 📦 *Tech Stack Flow*
<img width="993" height="474" alt="Screenshot 2025-10-30 192044" src="https://github.com/user-attachments/assets/5762f0ab-3a2e-42f2-8208-459c120e8858" />

## 💡 *Essential Links*
Link Demo: https://drive.google.com/drive/folders/1FPcu1RkJKglmezaZvpMcMOtkm3f9YWk3
Link Notion: https://www.notion.so/Pengembangan-LLM-Agent-Chatbot-Schedbot-sebagai-Asisten-Manajemen-Jadwal-terintegrasi-dengan-Googl-29a0fb4506398002b24ad07c4257d4eb?source=copy_link



