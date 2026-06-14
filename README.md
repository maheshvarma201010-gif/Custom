
# Mirror-Leech-Telegram-Bot with Auto Merge

This Telegram Bot, based on [python-aria-mirror-bot](https://github.com/lzzy12/python-aria-mirror-bot), has undergone substantial modifications and is designed for efficiently mirroring or leeching files from the Internet to various destinations, including Google Drive, Telegram, or any rclone-supported cloud. It is built using asynchronous programming in Python.

## 🎉 NEW: Auto Merge Feature
- **Auto Merge Toggle**: Enable/disable from `/settings` menu
- **Manual Merge**: Use `-m` flag with any mirror/leech command
- **Custom Naming**: `-m "Custom Name"` for merged output
- **Smart Sorting**: Natural order (Episode 1, Episode 2, Episode 10)
- **FFmpeg Integration**: Fast stream copy or re-encoding fallback
- **Telegram Limit Handling**: Auto-split to `filename_part1.mkv` if >2GB
- **Multi-Format Support**: MKV, MP4, AVI, MOV, WMV, FLV, WEBM, M4V, TS
- **Archive Extraction**: Extract then merge in one command

- **TELEGRAM CHANNEL:** https://t.me/mltb_official_channel
- **TELEGRAM GROUP:** https://t.me/mltb_official_support

---

## 📋 Table of Contents
1. [Features](#features)
2. [Auto Merge Usage](#auto-merge-usage)
3. [Deployment Guide](#deployment-guide)
4. [Configuration](#configuration)
5. [Commands](#commands)
6. [Troubleshooting](#troubleshooting)

---

## ✨ Features

### Auto Merge (NEW!)
- Toggle Auto Merge on/off from user settings
- Manual merge with `-m` flag
- Custom output naming with quotes: `-m "My Movie"`
- Natural sorting for episode numbers
- FFmpeg-based merging with smart fallback
- Auto-split for Telegram 2GB limit

### QBittorrent
- External access to webui, so you can remove files or edit settings. Then you can sync settings in database with sync button in bsetting
- Select files from a Torrent before and during download using mltb file selector (Requires Base URL) (task option)
- Seed torrents to a specific ratio and time (task option)
- Edit Global Options while the bot is running from bot settings (global option)

### Aria2c
- Select files from a Torrent before and during download (Requires Base URL) (task option)
- Seed torrents to a specific ratio and time (task option)
- Netrc support (global option)
- Direct link authentication for a specific link while using the bot (it will work even if only the username or password is provided) (task option)
- Edit Global Options while the bot is running from bot settings (global option)

### Sabnzbd
- External access to web interface, so you can remove files or edit settings. Then you can sync settings in database with sync button in bsetting
- Remove files from job before and during download using mltb file selector (Requires Base URL) (task option)
- Edit Global Options while the bot is running from bot settings (global option)
- Servers menu to edit/add/remove usenet servers

### TG Upload/Download
- Split size (global, user, and task option)
- Thumbnail (user and task option)
- Leech filename prefix (user option)
- Set upload as a document or as media (global, user and task option)
- Upload all files to a specific chat (superGroup/channel/private/topic) (global, user, and task option)
- Equal split size settings (global and user option)
- Ability to leech split file parts in a media group (global and user option)
- Download restricted messages (document or link) by tg private/public/super links (task option)
- Choose transfer by bot or user session in case you have a premium plan (global, user option and task option)
- Mix upload between user and bot session with respect to file size (global, user option and task option)
- Upload with custom layout multiple thumbnail (global, user option and task option)
- Topics support

### Google Drive
- Download/Upload/Clone/Delete/Count from/to Google Drive
- Count Google Drive files/folders
- Search in multiple Drive folder/TeamDrive
- Use Token.pickle if the file is not found with a Service Account, for all Gdrive functions
- Random Service Account for each task
- Recursive Search (only with `root` or TeamDrive ID, folder ids will be listed with a non-recursive method)
- Stop Duplicates (global and user option)
- Custom upload destination (global, user, and task option)
- Ability to choose token.pickle or service account and upload destinations from list with or without buttons (global, user and task option)
- Index link support

### Rclone
- Transfer (download/upload/clone-server-side) without or with random service accounts (global and user option)
- Ability to choose config, remote and path from list with or without buttons (global, user and task option)
- Ability to set flags for each task or globally from config (global, user and task option)
- Ability to select specific files or folders to download/copy using buttons (task option)
- Rclone.conf (global and user option)
- Rclone serve for combine remote to use it as index from all remotes (global option)
- Upload destination (global, user and task option)

### Status
- Download/Upload/Extract/Archive/Seed/Clone/Merge Status
- Status Pages for an unlimited number of tasks, view a specific number of tasks in a message (global option)
- Interval message update (global option)
- Next/Previous buttons to get different pages (global and user option)
- Status buttons to get specific tasks for the chosen status regarding transfer type if the number of tasks is more than 30 (global and user option)
- Steps buttons for how much next/previous buttons should step backward/forward (global and user option)
- Status for each user (no auto refresh)

### Yt-dlp
- Yt-dlp quality buttons (task option)
- Ability to use a specific yt-dlp option (global, user, and task option)
- Netrc support (global option)
- Cookies support (global option)
- Embed the original thumbnail and add it for leech
- All supported audio formats

### Gallery-dl
- Mirror and leech from gallery-dl supported sites
- Supports custom gallery-dl options globally, per user, and per task
- Supports cookies and config files for authenticated or advanced downloads

### JDownloader
- Synchronize Settings (global option)
- Waiting to select (enable/disable files or change variants) before download start
- DLC file support
- All settings can be edited from the remote access to your JDownloader with Web Interface, Android App, iPhone App or Browser Extensions

### Mongo Database
- Store bot settings
- Store user settings including thumbnails and all private files
- Store RSS data
- Store incomplete task messages
- Store JDownloader settings
- Store config.py file on first build and in case any change occurred to it, then next build it will define variables from config.py instead of database

### Torrents Search
- Search on torrents with Torrent Search API
- Search on torrents with variable plugins using qBittorrent search engine

### Archives
- Extract splits with or without password
- Zip file/folder with or without password and splits in case of leech
- Using 7z package to extract with or without password all supported types

### RSS
- Based on this repository [rss-chan](https://github.com/hyPnOtICDo0g/rss-chan)
- Rss feed (user option)
- Title Filters (feed option)
- Edit any feed while running: pause, resume, edit command and edit filters (feed option)
- Sudo settings to control users feeds
- All functions have been improved using buttons from one command.

### Overall
- Docker image support for linux `amd64, arm64/v8, arm/v7`
- Edit variables and overwrite the private files while bot running (bot, user settings)
- Update bot at startup and with restart command using `UPSTREAM_REPO`
- Telegraph
- Mirror/Leech/Watch/Clone/Count/Del by reply
- Mirror/Leech/Clone multi links/files with one command
- Custom name for all links except torrents. For files you should add extension except yt-dlp links (global and user option)
- Exclude files with specific extensions from being uploaded/cloned (global and user option)
- View Link button. Extra button to open index link in browser instead of direct download for file
- Queueing System for all tasks (global option)
- Ability to zip/unzip multi links in same directory. Mostly helpful in unzipping tg file parts (task option)
- Bulk download from telegram txt file or text message contains links separated by new line (task option)
- Join split files that were split before by split(linux pkg) (task option)
- Sample video Generator (task option)
- Screenshots Generator (task option)
- Ability to cancel upload/clone/archive/extract/split/queue (task option)
- Cancel all buttons for choosing specific tasks status to cancel (global option)
- Convert videos and audios to specific format with filter (task option)
- Force start to upload or download or both from queue using cmds or args once you add the download (task option)
- Shell and Executor
- Add sudo users
- Ability to save upload paths
- Name Substitution to rename the files before upload
- User can select whether he want to use his rclone.conf/token.pickle without adding mpt: or mrcc: before path/gd-id
- FFmpeg commands to execute it after download (task option)

---

## 🚀 Auto Merge Usage Examples

### Enable Auto Merge
1. Open `/settings` in Telegram
2. Click **"Enable Auto Merge"** button
3. Status will show "Auto Merge is Enabled"

### Manual Merge Commands
```bash
# Basic merge with default name
/l -m https://example.com/video1.mp4 https://example.com/video2.mp4

# Merge with custom name
/l -m "My Movie Collection" https://example.com/video1.mp4 https://example.com/video2.mp4

# Merge with extraction
/l -m -e https://example.com/archive1.rar https://example.com/archive2.rar

# Merge with multiple links
/l -m link1.mkv link2.mkv link3.mkv link4.mkv

# Mirror and merge
/m -m https://example.com/video1.mp4 https://example.com/video2.mp4
```

How Auto Merge Works

1. Bot downloads all linked files in order
2. Extracts archives if -e flag used
3. Scans for video files (MKV, MP4, AVI, MOV, etc.)
4. Sorts videos naturally (Episode 1, Episode 2, Episode 10)
5. Merges using FFmpeg (fast stream copy, no quality loss)
6. Uploads merged file to Telegram
7. Auto-splits if >2GB (filename_part1.mkv, filename_part2.mkv)

---

📦 Deployment Guide (100% Working)

Prerequisites

VPS Requirements

· OS: Ubuntu 20.04/22.04/24.04 LTS (Recommended)
· RAM: Minimum 2GB (4GB+ recommended for merging)
· Storage: 20GB+ free space
· CPU: 2+ cores

Step 1: Update System

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y curl wget git nano htop
```

Step 2: Install FFmpeg (REQUIRED for Auto Merge)

```bash
sudo apt install -y ffmpeg
ffmpeg -version
```

Step 3: Install Python and Dependencies

```bash
sudo apt install -y python3 python3-pip python3-venv
```

Step 4: Install MongoDB

```bash
sudo apt install -y mongodb
sudo systemctl start mongodb
sudo systemctl enable mongodb
sudo systemctl status mongodb
```

Step 5: Install Archive Tools

```bash
sudo apt install -y p7zip-full unrar-free unzip aria2
```

Step 6: Clone Repository

```bash
git clone https://github.com/anasty17/mirror-leech-telegram-bot.git mirrorbot
cd mirrorbot
```

Step 7: Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

Step 8: Install Python Packages

```bash
pip install --upgrade pip
pip install -r requirements.txt
pip install aiofiles natsort psutil pyrogram tgcrypto pymongo tenacity aiohttp
```

Step 9: Create Auto Merge Files

Create merge_utils.py:

```bash
mkdir -p bot/helper/mirror_leech_utils
cat > bot/helper/mirror_leech_utils/merge_utils.py << 'EOF'
# PASTE THE COMPLETE merge_utils.py CODE HERE
# (The one with VideoMerger and MergedTask classes)
EOF
```

Step 10: Configure Bot

```bash
cp config_sample.py config.py
nano config.py
```

Minimum required configuration:

```python
BOT_TOKEN = "YOUR_BOT_TOKEN_FROM_BOTFATHER"
OWNER_ID = 123456789
TELEGRAM_API = 12345
TELEGRAM_HASH = "your_api_hash"
DATABASE_URL = "mongodb://localhost:27017"
DATABASE_NAME = "mltb"
AUTO_MERGE = False
LEECH_SPLIT_SIZE = 2097152000
AS_DOCUMENT = False
STATUS_LIMIT = 4
```

Step 11: Create Directories

```bash
mkdir -p downloads tokens thumbnails rclone logs
chmod 755 downloads tokens thumbnails rclone logs
```

Step 12: Test Run

```bash
python3 -m bot
```

Step 13: Create Systemd Service (For Production)

```bash
sudo nano /etc/systemd/system/leechbot.service
```

Paste this:

```ini
[Unit]
Description=Mirror Leech Bot with Auto Merge
After=network.target mongodb.service

[Service]
Type=simple
User=$USER
WorkingDirectory=$PWD
Environment="PATH=$PWD/venv/bin"
ExecStart=$PWD/venv/bin/python3 -m bot
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable leechbot
sudo systemctl start leechbot
sudo systemctl status leechbot
```

Step 14: Check Logs

```bash
sudo journalctl -u leechbot -f
```

---

⚙️ Configuration

Required Fields

Variable Type Description
BOT_TOKEN Str Telegram Bot Token from @BotFather
OWNER_ID Int Your Telegram User ID
TELEGRAM_API Int From my.telegram.org
TELEGRAM_HASH Str From my.telegram.org

Auto Merge Specific

Variable Type Default Description
AUTO_MERGE Bool False Enable Auto Merge globally

Optional Fields

Variable Type Default Description
DATABASE_URL Str None MongoDB connection string
DATABASE_NAME Str mltb Database name
LEECH_SPLIT_SIZE Int 2097152000 Split size in bytes (2GB)
AS_DOCUMENT Bool False Upload as document
STATUS_LIMIT Int 4 Tasks shown in status

---

📱 Bot Commands

Mirror Commands

```
mirror - or /m Mirror
qbmirror - or /qm Mirror torrent using qBittorrent
jdmirror - or /jm Mirror using jdownloader
nzbmirror - or /nm Mirror using sabnzbd
ytdl - or /y Mirror yt-dlp supported links
gallerydl - or /gdl Mirror using gallery-dl
```

Leech Commands

```
leech - or /l Upload to telegram (supports -m for merge)
qbleech - or /ql Leech torrent using qBittorrent
jdleech - or /jl Leech using jdownloader
nzbleech - or /nl Leech using sabnzbd
ytdlleech - or /yl Leech yt-dlp supported links
gallerydlleech - or /gdlleech Leech using gallery-dl
```

Other Commands

```
clone - Copy file/folder to Drive
count - Count file/folder from GDrive
usetting - or /us User settings (includes Auto Merge toggle)
bsetting - or /bs Bot settings
status - Get Mirror Status Message (shows merge progress)
sel - Select files from torrent
rss - Rss menu
list - Search files in Drive
search - Search for torrents with API
nzbsearch - Search for NZBs
cancel - or /c Cancel a task
cancelall - Cancel all tasks
forcestart - or /fs to start task from queue
del - Delete file/folder from GDrive
log - Get the Bot Log
auth - Authorize user or chat
unauth - Unauthorize user or chat
shell - Run commands in Shell
aexec - Execute async function
exec - Execute sync function
clearlocals - Clear exec locals
restart - Restart the Bot
stats - Bot Usage Stats
ping - Ping the Bot
help - All cmds with description
```

---

🐛 Troubleshooting

FFmpeg Not Found

```bash
which ffmpeg
sudo apt install --reinstall ffmpeg -y
```

MongoDB Connection Failed

```bash
sudo systemctl status mongodb
sudo systemctl restart mongodb
mongosh --eval "db.runCommand({ping:1})"
```

Auto Merge Not Working

```bash
# Check FFmpeg
ffmpeg -version

# Check merge_utils.py exists
ls -la bot/helper/mirror_leech_utils/merge_utils.py

# Check logs
sudo journalctl -u leechbot -f | grep -i merge
```

Module Not Found

```bash
source venv/bin/activate
pip install -r requirements.txt --upgrade
```

Permission Denied

```bash
sudo chown -R $USER:$USER ~/mirrorbot
chmod -R 755 ~/mirrorbot
```

Bot Not Responding

```bash
# Check service status
sudo systemctl status leechbot

# Check token
grep BOT_TOKEN config.py

# Restart bot
sudo systemctl restart leechbot
```

---

🔧 Maintenance Commands

Update Bot

```bash
cd ~/mirrorbot
git pull
source venv/bin/activate
pip install -r requirements.txt --upgrade
sudo systemctl restart leechbot
```

View Logs

```bash
sudo journalctl -u leechbot -f --lines=100
```

Restart Bot

```bash
sudo systemctl restart leechbot
```

Stop Bot

```bash
sudo systemctl stop leechbot
```

Check Resources

```bash
htop
df -h
free -h
```

---

✅ Deployment Checklist

· Ubuntu 20.04/22.04/24.04 installed
· FFmpeg installed (ffmpeg -version)
· MongoDB installed and running
· Python 3.9+ installed
· Repository cloned
· Virtual environment created
· All dependencies installed
· config.py configured
· merge_utils.py created
· Bot runs without errors
· /settings shows Auto Merge toggle
· /l -m test1.mp4 test2.mp4 works
· Systemd service configured (optional)
· Firewall configured (optional)

---

🎉 Success!

Your bot is now running with the Auto Merge feature!

Quick Test:

```bash
# Send to your bot
/l -m "Test Merge" https://sample-videos.com/video123/mp4/720/big_buck_bunny_720p_1mb.mp4 https://sample-videos.com/video123/mp4/720/big_buck_bunny_720p_2mb.mp4
```

---

🤝 Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

📄 License

This project is licensed under the GNU General Public License v3.0

🙏 All Thanks To Our Contributors

<a href="https://github.com/anasty17/mirror-leech-telegram-bot/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=anasty17/mirror-leech-telegram-bot" />
</a>

💝 Donations

<p>If you feel like showing your appreciation for this project, then how about buying me a coffee.</p>

https://storage.ko-fi.com/cdn/kofi2.png

Binance ID:

```
52187862
```

USDT Address (TRC20):

```
TEzjjfkxLKQqndpsdpkA7jgiX7QQCL5p4f
```

BTC Address:

```
17dkvxjqdc3yiaTs6dpjUB1TjV3tD7ScWe
```

ETH Address:

```
0xf798a8a1c72d593e16d8f3bb619ebd1a093c7309
```

---

⭐ Star this repo if you find it useful!
