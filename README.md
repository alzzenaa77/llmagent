# Schedbot Discord -- LLM Agent untuk Manajemen Jadwal
SchedBot merupakan chatbot Discord berbasis Large Language Model (LLM) yang memanfaatkan API Google Gemini AI dan dirancang untuk membantu pengguna dalam mengatur dan menyusun jadwal harian secara otomatis melalui integrasi langsung dengan Google Calendar. <br>

Anggota Kelompok: <br>
Della Febi Alfian (22/505892/TK/55393) <br>
Raffa Alzena Zhafirah (22/505656/TK/55353) <br>

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

## ⚙️ Setup & Run untuk CLI dan integrasi
1. Lakukan git clone proyek <br> 
   ```git clone https://github.com/alzzenaa77/llmagent.git```
2. Masuk ke direktori proyek <br> 
   ```cd llmagent```
4. Install *dependencies* utama <br>
   ```pip install -r requirements.txt```
6. Masukkan token yang diperlukan di file .env, referensi ada di .env.<br>
7. Jalankan bot discord dengan menggunakan<br>
   ```python main.py <br> ```
9. Testing bisa dilakukan menggunakan<br>
   

## 📂 Struktur Proyek
LLMAGENT/<br>
├─ agent/<br>
│  ├─ tools/<br>
│  │  ├─ __init__.py                # Mendaftarkan tool untuk agent<br>
│  │  ├─ calendar_tools.py          # Tool utilitas kalender (create, read, update)<br>
│  │<br>
│  ├─ calendar_agent.py             # Agent untuk manajemen kalender<br>
│  ├─ llm_agent.py                  # Core logic & reasoning LLM<br>
│<br>
│  ├─ bot/<br>
│  │  ├─ discord_bot.py             # Integrasi dengan Discord bot<br>
│<br>
│  ├─ credentials/<br>
│  │  ├─ credentials.json           # Data client API<br>
│  │  └─ token.json                 # Token autentikasi<br>
│<br>
├─ node_modules/                    # Dependensi npm<br>
│<br>
├─ tests/<br>
│  ├─ test_calendar.py              # Unit test untuk fungsi kalender<br>
│<br>
├─ .env                             # Variabel lingkungan<br>
├─ .gitignore                       # File untuk mengecualikan dari git tracking<br>
├─ main.py                          # Entry point utama<br>
├─ package.json                     # Konfigurasi npm dependencies<br>
├─ package-lock.json                # Lock versi npm dependencies<br>
├─ README.md                        # Dokumentasi proyek<br>
├─ requirements.txt                 # Dependensi Python<br>
├─ test_agent.py                    # Unit test untuk agent<br>
└─ test_tools_wrapper.py            # Test untuk wrapper tools<br>


## 📦 *Tech Stack Flow*
<img width="993" height="474" alt="Screenshot 2025-10-30 192044" src="https://github.com/user-attachments/assets/5762f0ab-3a2e-42f2-8208-459c120e8858" />

## 💡 *Essential Links*
Link Demo: https://drive.google.com/drive/folders/1FPcu1RkJKglmezaZvpMcMOtkm3f9YWk3
Link Notion: https://www.notion.so/Pengembangan-LLM-Agent-Chatbot-Schedbot-sebagai-Asisten-Manajemen-Jadwal-terintegrasi-dengan-Googl-29a0fb4506398002b24ad07c4257d4eb?source=copy_link



