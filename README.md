# 🤖 Wonder Bot - Discord Bot yang Gampang Banget!

## ⚡ Quick Start (5 Menit Jadi!)

### 1. Setup Bot
```bash
# Install dependencies
pip install -r requirements.txt

# Jalanin bot
python run.py
```

### 2. Setting Discord Token
1. Buka `config.json`
2. Masukin Discord bot token lu di bagian `"token": "TOKEN_LU_DISINI"`
3. Save, terus jalanin bot!

## 🎮 Fitur Utama

- **💰 Ekonomi**: Coins, daily rewards, work, gambling
- **📈 Leveling**: XP system dengan roles otomatis  
- **🎁 Giveaway**: Bikin giveaway otomatis
- **🎯 Games**: Coinflip, dice, slots
- **🛒 Shop**: Beli items dengan coins
- **💧 Drops**: Random drops di channel

## 📁 File Penting (Yang Perlu Lu Tau)

```
wonder-bot/
├── src/main.py          # File utama bot (JANGAN DIUBAH kecuali tau banget)
├── config.json          # Setting bot (INI YANG SERING DIUBAH)
├── requirements.txt     # List library yang dibutuhin
├── run.py              # File buat jalanin bot (PAKAI INI UNTUK START)
└── archive/            # File-file lama yang gak penting (ABAIKAN AJA)
```

## 🔧 Kalo Ada Error

1. **Bot gak nyala**: Cek token di `config.json`
2. **Command gak jalan**: Restart bot (`Ctrl+C` terus `python run.py` lagi)
3. **Error aneh**: Hapus folder `src/__pycache__` terus restart

## 💡 Tips Buat Pemula

- **Gak usah buka file di folder `src/`** kecuali lu tau banget apa yang lu lakuin
- **Cuma ubah `config.json`** untuk setting bot
- **Pake `python run.py`** untuk start bot, jangan pake file lain
- **Kalo bingung, restart aja** bot-nya 90% masalah kelar

## 🆘 Butuh Bantuan?

Kalo stuck atau ada error yang aneh:
1. Screenshot error-nya
2. Kasih tau apa yang lu coba lakuin
3. Tanya di chat/forum yang biasa lu pake

---
*Made simple for beginners! Semua file ribet udah dipindahin ke folder `archive/` biar gak bikin pusing.*
