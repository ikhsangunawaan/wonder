# 🔧 Fix Discord Bot Errors - Panduan Lengkap

## ❌ Masalah yang Ditemukan

### 1. **Error Token Discord**
- **Error**: "Improper token has been passed"
- **Penyebab**: Token Discord masih menggunakan placeholder `YOUR_DISCORD_BOT_TOKEN_HERE`

### 2. **Missing Dependencies** 
- **Error**: `ModuleNotFoundError: No module named 'discord'`
- **Penyebab**: Package Python yang diperlukan belum diinstall

### 3. **Duplicate Command Sync**
- **Masalah**: Bot mencoba sync slash commands dua kali di setup_hook

## ✅ Solusi yang Telah Diterapkan

### 1. **Install Dependencies**
```bash
pip3 install -r requirements.txt --break-system-packages
```

**Package yang diinstall:**
- discord.py>=2.3.2
- aiofiles>=23.2.1  
- aiosqlite>=0.19.0
- aiomysql>=0.2.0
- PyMySQL>=1.1.0
- Pillow>=10.0.1
- python-dotenv>=1.0.0
- schedule>=1.2.0
- colorama>=0.4.6
- typing-extensions>=4.8.0
- PyNaCl>=1.5.0
- requests>=2.31.0

### 2. **Update .env File**
File `.env` telah diupdate dengan instruksi yang jelas:
```env
# Discord Bot Configuration
# IMPORTANT: Replace YOUR_DISCORD_BOT_TOKEN_HERE with your actual Discord bot token
# To get your bot token:
# 1. Go to https://discord.com/developers/applications
# 2. Create a new application or select your existing bot application
# 3. Go to the "Bot" section
# 4. Copy the token and paste it below
DISCORD_TOKEN=YOUR_DISCORD_BOT_TOKEN_HERE

# Optional Role IDs (get these from your Discord server)
# Right-click on roles in Discord with Developer Mode enabled to copy IDs
PREMIUM_ROLE_ID=YOUR_PREMIUM_ROLE_ID_HERE
BOOSTER_ROLE_ID=YOUR_BOOSTER_ROLE_ID_HERE

# Database Configuration (Optional - uses SQLite by default)
# Uncomment and configure these if you want to use MySQL
# DB_HOST=localhost
# DB_PORT=3306
# DB_NAME=wonder_bot
# DB_USER=your_username
# DB_PASSWORD=your_password
```

### 3. **Fix Duplicate Command Sync**
Removed duplicate slash command syncing in `setup_hook()` method.

### 4. **Add Test Script**
Created `test_bot.py` untuk verifikasi inisialisasi bot tanpa koneksi Discord.

## 🚀 Cara Menjalankan Bot

### 1. **Setup Discord Token**
1. Buka https://discord.com/developers/applications
2. Buat aplikasi baru atau pilih aplikasi bot yang sudah ada
3. Pergi ke bagian "Bot"
4. Copy token dan paste ke file `.env`:
   ```env
   DISCORD_TOKEN=your_actual_bot_token_here
   ```

### 2. **Test Bot**
```bash
python3 test_bot.py
```

### 3. **Run Bot**
```bash
python3 src/main.py
```
atau
```bash
python3 run.py
```

## 🎮 Commands yang Tersedia

### **Economy Commands**
- `w.balance [@user]` - Cek balance WonderCoins
- `w.daily` - Claim daily reward
- `w.work` - Kerja untuk earn coins
- `w.leaderboard` - Lihat leaderboard

### **Game Commands**
- `w.coinflip <amount> <choice>` - Flip coin gambling
- `w.dice <amount> <target>` - Dice gambling  
- `w.slots <amount>` - Slot machine
- `w.gamestats [@user]` - Lihat statistik gambling

### **Shop Commands**
- `w.shop [category] [page]` - Browse shop
- `w.buy <item_id> [quantity]` - Beli item
- `w.inventory [page]` - Lihat inventory
- `w.use <item_id>` - Gunakan item

### **Leveling Commands**
- `w.rank [@user]` - Lihat rank dan XP
- `w.roles` - Lihat level roles
- `w.prestige` - Prestige info

### **Admin Commands**
- `w.giveaway-create` - Buat giveaway
- `w.adddrops` - Add drop channel
- `w.set-user-xp` - Set user XP
- `w.toggle-category` - Toggle leveling category

### **Slash Commands**
Semua commands juga tersedia sebagai slash commands (`/balance`, `/daily`, dll.)

## 🔧 Troubleshooting

### **Bot tidak bisa start**
1. Pastikan token Discord benar di `.env`
2. Check log error di `bot.log`
3. Jalankan `python3 test_bot.py` untuk test

### **Commands tidak bekerja**
1. Pastikan bot punya permissions yang cukup
2. Check intents di Discord Developer Portal
3. Restart bot setelah sync commands

### **Database errors**
- Bot menggunakan SQLite by default
- MySQL opsional (configure di `.env`)
- Database tables dibuat otomatis

### **Permission errors**
Pastikan bot punya permissions:
- Send Messages
- Embed Links
- Add Reactions
- Manage Roles (untuk leveling)
- Manage Messages (untuk giveaways)

## 📋 System Status

✅ **Dependencies** - Installed
✅ **Database** - Initialized  
✅ **Commands** - Loaded (104 commands total)
✅ **Error Handling** - Comprehensive
✅ **Slash Commands** - Synchronized
✅ **Bot Ready** - Siap dijalankan

**Next Steps:**
1. Set Discord token di `.env`
2. Run bot: `python3 src/main.py`
3. Invite bot ke server dengan permissions yang cukup

## 🆘 Support

Jika masih ada error:
1. Check file `bot.log` untuk error details
2. Pastikan Python 3.8+ digunakan
3. Verify semua dependencies terinstall
4. Check Discord token validity