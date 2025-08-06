# Manual Menjalankan Wonder Discord Bot (Python Application)

## Persyaratan Sistem

1. **Python 3.8+** terinstall di sistem Anda
2. **Discord Bot Token** dari Discord Developer Portal
3. **Git** (opsional, untuk clone repository)
4. **Internet connection** untuk install dependencies

## Langkah-langkah Instalasi dan Menjalankan Aplikasi

### 1. Persiapan Environment

#### Opsi A: Menggunakan Virtual Environment (Direkomendasikan)
```bash
# Buat virtual environment
python3 -m venv wonder-bot-env

# Aktifkan virtual environment
# Linux/Mac:
source wonder-bot-env/bin/activate
# Windows:
wonder-bot-env\Scripts\activate
```

#### Opsi B: Instalasi Global (Tidak direkomendasikan untuk production)
```bash
# Langsung install tanpa virtual environment
# Gunakan flag --break-system-packages jika diperlukan
pip install --break-system-packages -r requirements.txt
```

### 2. Install Python Packages/Dependencies

**Daftar Python Packages yang Diperlukan:**

| Package | Versi Minimum | Fungsi |
|---------|---------------|--------|
| `discord.py` | ≥2.3.2 | Library utama untuk Discord bot |
| `aiofiles` | ≥23.2.1 | Async file operations |
| `aiosqlite` | ≥0.19.0 | Async SQLite database operations |
| `Pillow` | ≥10.0.1 | Image processing untuk fitur bot |
| `python-dotenv` | ≥1.0.0 | Load environment variables dari .env file |
| `schedule` | ≥1.2.0 | Scheduling tasks |
| `colorama` | ≥0.4.6 | Colored terminal output |
| `typing-extensions` | ≥4.8.0 | Extended typing support |
| `PyNaCl` | ≥1.5.0 | Voice support untuk Discord |

**Cara Install Dependencies:**
```bash
# Install semua dependencies sekaligus
pip install -r requirements.txt

# Atau install satu per satu jika ada masalah
pip install discord.py>=2.3.2
pip install aiofiles>=23.2.1
pip install aiosqlite>=0.19.0
pip install Pillow>=10.0.1
pip install python-dotenv>=1.0.0
pip install schedule>=1.2.0
pip install colorama>=0.4.6
pip install typing-extensions>=4.8.0
pip install PyNaCl>=1.5.0
```

### 3. Konfigurasi Environment Variables

1. **Buat file .env** (jika belum ada):
   ```bash
   cp .env.example .env  # atau buat file .env baru
   ```

2. **Edit file .env** dan tambahkan konfigurasi berikut:
   ```env
   # WAJIB: Token Discord Bot
   DISCORD_TOKEN=your_actual_discord_bot_token_here

   # OPSIONAL: Role IDs untuk fitur premium
   PREMIUM_ROLE_ID=your_premium_role_id_here
   BOOSTER_ROLE_ID=your_booster_role_id_here

   # OPSIONAL: Database settings
   DATABASE_PATH=wonder.db

   # OPSIONAL: Logging level
   LOG_LEVEL=INFO
   ```

### 4. Mendapatkan Discord Bot Token

1. Kunjungi [Discord Developer Portal](https://discord.com/developers/applications)
2. Klik "New Application" dan beri nama bot Anda
3. Navigasi ke tab "Bot" di sidebar
4. Klik "Add Bot" untuk membuat bot
5. Copy token dari bagian "Token" (jangan share token ini!)
6. **PENTING**: Aktifkan intents berikut di bagian "Privileged Gateway Intents":
   - ✅ Message Content Intent
   - ✅ Server Members Intent
   - ✅ Presence Intent (opsional)

### 5. Menjalankan Aplikasi Python

#### Metode 1: Menggunakan Script Python Langsung (Direkomendasikan)
```bash
# Pastikan Anda berada di directory project
cd /path/to/wonder-discord-bot

# Jalankan aplikasi
python3 run.py
```

#### Metode 2: Menggunakan Start Script
```bash
# Berikan permission execute pada script
chmod +x start.sh

# Jalankan script
./start.sh
```

#### Metode 3: Untuk Development dengan Auto-reload
```bash
# Install nodemon atau equivalent untuk Python
pip install watchdog

# Jalankan dengan auto-reload (buat script terpisah jika perlu)
python3 -m watchdog --patterns="*.py" --ignore-patterns="*/__pycache__/*" run.py
```

### 6. Verifikasi Bot Berjalan

Jika berhasil, Anda akan melihat output seperti:
```
[INFO] Bot is starting...
[INFO] Database initialized successfully
[INFO] Bot logged in as: YourBotName#1234
[INFO] Bot is ready and online!
```

## Deployment ke Platform Hosting

### Heroku
1. **Buat Procfile** (sudah tersedia):
   ```
   worker: python3 run.py
   ```

2. **Set environment variables** di dashboard Heroku:
   - `DISCORD_TOKEN`
   - `PREMIUM_ROLE_ID` (opsional)
   - `BOOSTER_ROLE_ID` (opsional)

3. **Deploy**:
   ```bash
   git add .
   git commit -m "Deploy Wonder Discord Bot"
   git push heroku main
   ```

### Railway/Render/Digital Ocean
1. Upload project ke platform
2. Set environment variables di dashboard
3. Gunakan command: `python3 run.py`

### VPS/Dedicated Server
1. **Install dependencies**:
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip python3-venv
   ```

2. **Setup project**:
   ```bash
   git clone <repository-url>
   cd wonder-discord-bot
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Setup service** (systemd):
   ```bash
   sudo nano /etc/systemd/system/wonder-bot.service
   ```
   
   Isi file service:
   ```ini
   [Unit]
   Description=Wonder Discord Bot
   After=network.target

   [Service]
   Type=simple
   User=your-username
   WorkingDirectory=/path/to/wonder-discord-bot
   Environment=PATH=/path/to/wonder-discord-bot/venv/bin
   ExecStart=/path/to/wonder-discord-bot/venv/bin/python run.py
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

4. **Enable dan start service**:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable wonder-bot
   sudo systemctl start wonder-bot
   ```

## Fitur Bot

- **Sistem Ekonomi**: WonderCoins, daily rewards, work commands
- **Games**: Coinflip, dice, slots
- **Sistem Shop**: Buy items dan manage inventory
- **Leveling System**: XP dan level tracking
- **Giveaway System**: Create dan manage giveaways
- **Auto WonderCoins Drops**: Random coin drops di channels

## Commands Utama

Bot menggunakan prefix `w.`. Contoh commands:

| Command | Fungsi |
|---------|--------|
| `w.balance` | Cek balance WonderCoins |
| `w.daily` | Claim daily coins |
| `w.work` | Work untuk dapat coins |
| `w.coinflip <amount>` | Main coinflip |
| `w.shop` | Lihat shop |
| `w.rank` | Cek level dan XP |
| `w.help` | Get help commands |
| `w.giveaway create` | Buat giveaway |

## Troubleshooting

### Error "Improper token"
- ✅ Pastikan DISCORD_TOKEN di .env file benar
- ✅ Token tidak boleh ada spasi atau quotes tambahan
- ✅ Token harus dari bot yang sudah dibuat di Discord Developer Portal

### Import Errors
- ✅ Pastikan semua dependencies terinstall: `pip list`
- ✅ Cek virtual environment aktif: `which python`
- ✅ Reinstall dependencies: `pip install -r requirements.txt --force-reinstall`

### Permission Errors di Discord
- ✅ Bot harus di-invite ke server dengan permissions yang cukup
- ✅ Role bot harus di atas role yang ingin dikelola
- ✅ Channel permissions harus allow bot untuk read/send messages

### Database Errors
- ✅ Pastikan file `wonder.db` dapat ditulis
- ✅ Cek permissions directory: `ls -la wonder.db`
- ✅ Hapus database lama jika corrupt: `rm wonder.db` (data akan hilang)

### Python Path Errors
- ✅ Gunakan `start.sh` script yang auto-detect Python path
- ✅ Cek Python installation: `which python3`
- ✅ Update system Python jika versi terlalu lama

## Monitoring dan Logs

### Melihat Logs Real-time
```bash
# Jika run manual
python3 run.py

# Jika pakai systemd service
sudo journalctl -u wonder-bot -f

# Jika pakai screen/tmux
screen -r wonder-bot
```

### Log Files
- Bot logs tersimpan di: `bot.log`
- Database: `wonder.db`
- Config: `config.json`

## Update dan Maintenance

### Update Bot
```bash
# Backup database
cp wonder.db wonder.db.backup

# Pull updates
git pull origin main

# Update dependencies
pip install -r requirements.txt --upgrade

# Restart bot
# Manual: Ctrl+C dan jalankan lagi python3 run.py
# Service: sudo systemctl restart wonder-bot
```

### Backup Data
```bash
# Backup database
cp wonder.db backups/wonder.db.$(date +%Y%m%d_%H%M%S)

# Backup config
cp config.json backups/config.json.$(date +%Y%m%d_%H%M%S)
```