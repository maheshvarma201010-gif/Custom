# ============================================
# REQUIRED CONFIGURATIONS
# ============================================

# Telegram Bot Token from @BotFather
BOT_TOKEN = ""

# Your Telegram User ID (get from @userinfobot)
OWNER_ID = 0

# Telegram API ID and Hash from https://my.telegram.org
TELEGRAM_API = 0
TELEGRAM_HASH = ""


# ============================================
# OPTIONAL CONFIGURATIONS
# ============================================

# Proxy settings (if needed)
# Format: {"scheme": "socks5", "hostname": "127.0.0.1", "port": 1080}
TG_PROXY = {}

# User session string for premium features
USER_SESSION_STRING = ""

# Command suffix to avoid conflicts with other bots
CMD_SUFFIX = ""

# Authorized chats (comma-separated IDs, -100 for group)
AUTHORIZED_CHATS = ""

# Sudo users (comma-separated IDs, can use bot commands)
SUDO_USERS = ""

# MongoDB Database URL
DATABASE_URL = ""

# Database name
DATABASE_NAME = "mltb"

# Status message update interval (seconds)
STATUS_LIMIT = 4
STATUS_UPDATE_INTERVAL = 15

# Default upload mode: "gd" for GDrive, "rc" for Rclone
DEFAULT_UPLOAD = "rc"

# File hosting APIs (optional)
FILELION_API = ""
STREAMWISH_API = ""

# AllDebrid API Key
ALLDEBRID_API_KEY = ""

# BuzzHeavier Account ID
BUZZHEAVIER_ACCOUNT_ID = ""

# Gofile API Key
GOFILE_API_KEY = ""

# Excluded extensions (space-separated, e.g., "txt jpg nfo")
EXCLUDED_EXTENSIONS = ""

# Included extensions (space-separated, empty = all)
INCLUDED_EXTENSIONS = ""

# Notify when incomplete tasks exist
INCOMPLETE_TASK_NOTIFIER = False

# YT-DLP custom options (JSON format)
YT_DLP_OPTIONS = ""

# Gallery-DL custom options (JSON format)
GALLERY_DL_OPTIONS = ""

# Use Google Service Accounts for GDrive
USE_SERVICE_ACCOUNTS = False

# Name substitute regex pattern
NAME_SUBSTITUTE = r""

# FFmpeg custom commands (JSON format)
FFMPEG_CMDS = {"merge": ["-f concat -safe 0 -i mltb.txt -c copy mltb.mp4 -del"]}

# Upload paths configuration (JSON format)
UPLOAD_PATHS = {}

# Enable file links instead of file uploads
FILES_LINKS = False


# ============================================
# AUTO MERGE FEATURE
# ============================================
# Automatically merge multiple video files into one MKV file
# When enabled: Downloads all files, extracts archives, merges videos in order
# Then uploads as single file (auto-splits if exceeds Telegram 2GB limit)
AUTO_MERGE = False


# ============================================
# GOOGLE DRIVE CONFIGURATIONS
# ============================================

# Default GDrive folder ID
GDRIVE_ID = ""

# Set to True if using Team Drive
IS_TEAM_DRIVE = False

# Stop upload if file already exists
STOP_DUPLICATE = False

# Index URL for direct GDrive links
INDEX_URL = ""


# ============================================
# RCLONE CONFIGURATIONS
# ============================================

# Default Rclone remote:path
RCLONE_PATH = ""

# Rclone flags (e.g., "--drive-chunk-size 64M")
RCLONE_FLAGS = ""

# Rclone serve URL (for streaming)
RCLONE_SERVE_URL = ""
RCLONE_SERVE_PORT = 0
RCLONE_SERVE_USER = ""
RCLONE_SERVE_PASS = ""


# ============================================
# JDOWNLOADER CONFIGURATIONS
# ============================================

# JDownloader MyJdownloader credentials
JD_EMAIL = ""
JD_PASS = ""


# ============================================
# SABNZBD (USENET) CONFIGURATIONS
# ============================================

USENET_SERVERS = [
    {
        "name": "main",
        "host": "",
        "port": 563,
        "timeout": 60,
        "username": "",
        "password": "",
        "connections": 8,
        "ssl": 1,
        "ssl_verify": 2,
        "ssl_ciphers": "",
        "enable": 1,
        "required": 0,
        "optional": 0,
        "retention": 0,
        "send_group": 0,
        "priority": 0,
    }
]


# ============================================
# NZB SEARCH CONFIGURATIONS (nzbhydra2)
# ============================================

HYDRA_IP = ""
HYDRA_API_KEY = ""


# ============================================
# BOT UPDATE CONFIGURATIONS
# ============================================

# Upstream repo URL for auto-updates
UPSTREAM_REPO = ""

# Branch name (main, master, etc.)
UPSTREAM_BRANCH = "master"


# ============================================
# LEECH CONFIGURATIONS
# ============================================

# Split size for leech (0 = no split, >0 = split into parts)
LEECH_SPLIT_SIZE = 0

# Send as document (True) or as media (False)
AS_DOCUMENT = False

# Split files equally by size
EQUAL_SPLITS = False

# Send files as media group (album)
MEDIA_GROUP = False

# Use user session for leech (requires premium)
USER_TRANSMISSION = False

# Hybrid leech (mix of bot and user session)
HYBRID_LEECH = False

# Prefix for leeched files
LEECH_FILENAME_PREFIX = ""

# Default leech destination chat ID
LEECH_DUMP_CHAT = ""

# Clone dump chats (comma-separated)
CLONE_DUMP_CHATS = ""

# Thumbnail layout style
THUMBNAIL_LAYOUT = ""


# ============================================
# TORRENT CONFIGURATIONS (qBittorrent/Aria2c)
# ============================================

# Torrent download timeout (seconds)
TORRENT_TIMEOUT = 0

# Base URL for direct downloads
BASE_URL = ""
BASE_URL_PORT = 0

# Web authentication pincode
WEB_PINCODE = False


# ============================================
# QUEUE SYSTEM CONFIGURATIONS
# ============================================

# Maximum concurrent tasks (0 = unlimited)
QUEUE_ALL = 0
QUEUE_DOWNLOAD = 0
QUEUE_UPLOAD = 0


# ============================================
# RSS CONFIGURATIONS
# ============================================

# RSS refresh delay (seconds)
RSS_DELAY = 600

# RSS default chat ID
RSS_CHAT = ""

# RSS size limit (bytes)
RSS_SIZE_LIMIT = 0


# ============================================
# TORRENT SEARCH CONFIGURATIONS
# ============================================

# Search API link (e.g., jackett)
SEARCH_API_LINK = ""

# Maximum search results
SEARCH_LIMIT = 0

# Search engine plugins
SEARCH_PLUGINS = [
    "https://raw.githubusercontent.com/qbittorrent/search-plugins/master/nova3/engines/piratebay.py",
    "https://raw.githubusercontent.com/qbittorrent/search-plugins/master/nova3/engines/limetorrents.py",
    "https://raw.githubusercontent.com/qbittorrent/search-plugins/master/nova3/engines/torlock.py",
    "https://raw.githubusercontent.com/qbittorrent/search-plugins/master/nova3/engines/torrentscsv.py",
    "https://raw.githubusercontent.com/qbittorrent/search-plugins/master/nova3/engines/eztv.py",
    "https://raw.githubusercontent.com/qbittorrent/search-plugins/master/nova3/engines/torrentproject.py",
    "https://raw.githubusercontent.com/MaurizioRicci/qBittorrent_search_engines/master/kickass_torrent.py",
    "https://raw.githubusercontent.com/MaurizioRicci/qBittorrent_search_engines/master/yts_am.py",
    "https://raw.githubusercontent.com/MadeOfMagicAndWires/qBit-plugins/master/engines/linuxtracker.py",
    "https://raw.githubusercontent.com/MadeOfMagicAndWires/qBit-plugins/master/engines/nyaasi.py",
    "https://raw.githubusercontent.com/LightDestory/qBittorrent-Search-Plugins/master/src/engines/ettv.py",
    "https://raw.githubusercontent.com/LightDestory/qBittorrent-Search-Plugins/master/src/engines/glotorrents.py",
    "https://raw.githubusercontent.com/LightDestory/qBittorrent-Search-Plugins/master/src/engines/thepiratebay.py",
    "https://raw.githubusercontent.com/v1k45/1337x-qBittorrent-search-plugin/master/leetx.py",
    "https://raw.githubusercontent.com/nindogo/qbtSearchScripts/master/magnetdl.py",
    "https://raw.githubusercontent.com/msagca/qbittorrent_plugins/main/uniondht.py",
    "https://raw.githubusercontent.com/khensolomon/leyts/master/yts.py",
]
