# bot/helper/ext_utils/bot_utils.py

from httpx import AsyncClient
from asyncio.subprocess import PIPE
from functools import partial, wraps
from concurrent.futures import ThreadPoolExecutor
from asyncio import (
    create_subprocess_exec,
    create_subprocess_shell,
    run_coroutine_threadsafe,
    sleep,
)
import re
import os
from pathlib import Path

from ... import user_data, bot_loop
from ...core.config_manager import Config
from ..telegram_helper.button_build import ButtonMaker
from .telegraph_helper import telegraph
from .help_messages import (
    YT_HELP_DICT,
    GDL_HELP_DICT,
    MIRROR_HELP_DICT,
    CLONE_HELP_DICT,
)

COMMAND_USAGE = {}

THREAD_POOL = ThreadPoolExecutor(max_workers=500)


class SetInterval:
    def __init__(self, interval, action, *args, **kwargs):
        self.interval = interval
        self.action = action
        self.task = bot_loop.create_task(self._set_interval(*args, **kwargs))

    async def _set_interval(self, *args, **kwargs):
        while True:
            await sleep(self.interval)
            await self.action(*args, **kwargs)

    def cancel(self):
        self.task.cancel()


def _build_command_usage(help_dict, command_key):
    buttons = ButtonMaker()
    for name in list(help_dict.keys())[1:]:
        buttons.data_button(name, f"help {command_key} {name}")
    buttons.data_button("Close", "help close")
    COMMAND_USAGE[command_key] = [help_dict["main"], buttons.build_menu(3)]
    buttons.reset()


def create_help_buttons():
    _build_command_usage(MIRROR_HELP_DICT, "mirror")
    _build_command_usage(YT_HELP_DICT, "yt")
    _build_command_usage(GDL_HELP_DICT, "gdl")
    _build_command_usage(CLONE_HELP_DICT, "clone")


def bt_selection_buttons(id_):
    gid = id_[:12] if len(id_) > 25 else id_
    pin = "".join([n for n in id_ if n.isdigit()][:4])
    buttons = ButtonMaker()
    if Config.WEB_PINCODE:
        buttons.url_button("Select Files", f"{Config.BASE_URL}/app/files?gid={id_}")
        buttons.data_button("Pincode", f"sel pin {gid} {pin}")
    else:
        buttons.url_button(
            "Select Files", f"{Config.BASE_URL}/app/files?gid={id_}&pin={pin}"
        )
    buttons.data_button("Done Selecting", f"sel done {gid} {id_}")
    buttons.data_button("Cancel", f"sel cancel {gid}")
    return buttons.build_menu(2)


async def get_telegraph_list(telegraph_content):
    path = [
        (
            await telegraph.create_page(
                title="Mirror-Leech-Bot Drive Search", content=content
            )
        )["path"]
        for content in telegraph_content
    ]
    if len(path) > 1:
        await telegraph.edit_telegraph(path, telegraph_content)
    buttons = ButtonMaker()
    buttons.url_button("🔎 VIEW", f"https://telegra.ph/{path[0]}")
    return buttons.build_menu(1)


def arg_parser(items, arg_base):
    if not items:
        return

    arg_start = -1
    i = 0
    total = len(items)

    # Boolean flags (don't take values)
    bool_arg_set = {
        "-b", "-e", "-z", "-s", "-j", "-d", "-sv", "-ss", "-f", "-fd", "-fu",
        "-sync", "-hl", "-doc", "-med", "-ut", "-bt", "-ad", "-tb", "-m"  # Added -m flag for merge
    }

    # Flags that can take string values
    string_arg_set = {"-n", "-up", "-rcf", "-au", "-ap", "-t", "-ca", "-cv", "-ns", "-tl", "-m"}

    while i < total:
        part = items[i]

        if part in arg_base:
            if arg_start == -1:
                arg_start = i

            # Handle boolean flags
            if part in bool_arg_set:
                arg_base[part] = True
                i += 1
                continue

            # Handle string value flags
            if part in string_arg_set:
                if i + 1 < total and items[i + 1] not in arg_base:
                    value = items[i + 1]
                    # Handle quoted values for -m flag
                    if part == "-m" and (value.startswith('"') or value.startswith("'")):
                        # Find closing quote
                        quote_char = value[0]
                        if value.endswith(quote_char) and len(value) > 1:
                            # Value is fully quoted
                            arg_base[part] = value[1:-1]
                            i += 2
                            continue
                        else:
                            # Multi-part quoted string
                            quoted_parts = [value]
                            for j in range(i + 2, total):
                                quoted_parts.append(items[j])
                                if items[j].endswith(quote_char):
                                    break
                            full_value = " ".join(quoted_parts)
                            arg_base[part] = full_value[1:-1]
                            i += len(quoted_parts) + 1
                            continue
                    else:
                        arg_base[part] = value
                        i += 2
                        continue
                else:
                    arg_base[part] = ""
                    i += 1
                continue

            # Handle numeric flags
            if part == "-i" or part == "-sp":
                if i + 1 < total and items[i + 1].isdigit():
                    arg_base[part] = int(items[i + 1])
                    i += 2
                else:
                    arg_base[part] = 0
                    i += 1
                continue

            # Handle headers flag
            if part == "-h":
                headers = []
                j = i + 1
                while j < total and items[j] not in arg_base:
                    headers.append(items[j])
                    j += 1
                if headers:
                    arg_base[part] = "|".join(headers)
                else:
                    arg_base[part] = []
                i = j
                continue

            # Handle FFmpeg commands flag
            if part == "-ff":
                ff_cmds = set()
                j = i + 1
                while j < total and items[j] not in arg_base:
                    value = items[j]
                    if value.startswith("[") and value.endswith("]"):
                        try:
                            ff_cmds.add(tuple(eval(value)))
                        except:
                            ff_cmds.add(value)
                    else:
                        ff_cmds.add(value)
                    j += 1
                arg_base[part] = ff_cmds
                i = j
                continue

        i += 1

    # Handle link extraction
    if "link" in arg_base:
        # Collect all remaining items as links
        if arg_start != -1:
            link_items = items[:arg_start]
        else:
            # Remove flags from items to get links
            link_items = []
            skip_next = False
            for idx, item in enumerate(items):
                if skip_next:
                    skip_next = False
                    continue
                if item in arg_base:
                    if item in string_arg_set and idx + 1 < len(items) and items[idx + 1] not in arg_base:
                        skip_next = True
                    continue
                link_items.append(item)
        
        if link_items:
            arg_base["link"] = " ".join(link_items)


def get_size_bytes(size):
    """Convert size string to bytes (e.g., '1GB' -> 1073741824)"""
    if not size:
        return 0
    size = str(size).lower()
    try:
        if "k" in size:
            return int(float(size.split("k")[0]) * 1024)
        elif "m" in size:
            return int(float(size.split("m")[0]) * 1048576)
        elif "g" in size:
            return int(float(size.split("g")[0]) * 1073741824)
        elif "t" in size:
            return int(float(size.split("t")[0]) * 1099511627776)
        else:
            return int(float(size))
    except:
        return 0


async def get_content_type(url):
    try:
        async with AsyncClient() as client:
            response = await client.get(url, allow_redirects=True, verify=False, timeout=30)
            return response.headers.get("Content-Type")
    except Exception:
        return None


def update_user_ldata(id_, key, value):
    """Update user data dictionary"""
    user_data.setdefault(id_, {})
    user_data[id_][key] = value


async def cmd_exec(cmd, shell=False):
    """Execute shell command asynchronously"""
    if shell:
        proc = await create_subprocess_shell(cmd, stdout=PIPE, stderr=PIPE)
    else:
        proc = await create_subprocess_exec(*cmd, stdout=PIPE, stderr=PIPE)
    stdout, stderr = await proc.communicate()
    try:
        stdout = stdout.decode().strip()
    except:
        stdout = "Unable to decode the response!"
    try:
        stderr = stderr.decode().strip()
    except:
        stderr = "Unable to decode the error!"
    return stdout, stderr, proc.returncode


def new_task(func):
    """Decorator to run async function as a new task"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        task = bot_loop.create_task(func(*args, **kwargs))
        return task
    return wrapper


async def sync_to_async(func, *args, wait=True, **kwargs):
    """Run synchronous function in thread pool"""
    pfunc = partial(func, *args, **kwargs)
    future = bot_loop.run_in_executor(THREAD_POOL, pfunc)
    return await future if wait else future


def async_to_sync(func, *args, wait=True, **kwargs):
    """Run async function synchronously"""
    future = run_coroutine_threadsafe(func(*args, **kwargs), bot_loop)
    return future.result() if wait else future


def loop_thread(func):
    """Decorator to run async function in event loop from sync context"""
    @wraps(func)
    def wrapper(*args, wait=False, **kwargs):
        future = run_coroutine_threadsafe(func(*args, **kwargs), bot_loop)
        return future.result() if wait else future
    return wrapper


# ============ AUTO MERGE UTILITIES ============

def natural_sort_key(filename: str):
    """Natural sorting for filenames (Episode 1, Episode 2, Episode 10)"""
    parts = re.split(r'(\d+)', filename)
    return [int(part) if part.isdigit() else part.lower() for part in parts]


def extract_links_and_merge_flag(text: str) -> tuple:
    """
    Extract all links and check for merge flag from command text
    Returns: (links_list, should_merge, custom_name, cleaned_text)
    
    Examples:
        "/l -m link1.mp4 link2.mp4" -> (["link1.mp4", "link2.mp4"], True, "", "/l link1.mp4 link2.mp4")
        "/l -m 'My Movie' link1.mp4 link2.mp4" -> (["link1.mp4", "link2.mp4"], True, "My Movie", "/l link1.mp4 link2.mp4")
        "/l -m \"My Movie\" link1.mp4 link2.mp4" -> (["link1.mp4", "link2.mp4"], True, "My Movie", "/l link1.mp4 link2.mp4")
    """
    if not text:
        return [], False, "", text
    
    parts = text.split()
    
    links = []
    should_merge = False
    custom_name = ""
    cleaned_parts = []
    skip_next = False
    in_quotes = False
    quote_char = None
    quoted_buffer = []
    
    i = 0
    while i < len(parts):
        part = parts[i]
        
        if skip_next:
            skip_next = False
            cleaned_parts.append(part)
            i += 1
            continue
        
        # Handle merge flag
        if part == '-m':
            should_merge = True
            i += 1
            
            # Check if there's a custom name
            if i < len(parts):
                next_part = parts[i]
                
                # Check for quoted name
                if next_part.startswith('"') or next_part.startswith("'"):
                    quote_char = next_part[0]
                    if next_part.endswith(quote_char) and len(next_part) > 1:
                        # Single part quoted
                        custom_name = next_part[1:-1]
                        skip_next = True
                        cleaned_parts.append(next_part)
                        i += 1
                    else:
                        # Multi-part quoted
                        quoted_parts = [next_part]
                        i += 1
                        while i < len(parts):
                            quoted_parts.append(parts[i])
                            if parts[i].endswith(quote_char):
                                break
                            i += 1
                        full_quoted = " ".join(quoted_parts)
                        custom_name = full_quoted[1:-1]
                        skip_next = True
                        for qp in quoted_parts:
                            cleaned_parts.append(qp)
                        i += 1
                elif not next_part.startswith('-'):
                    # Unquoted name (single word)
                    custom_name = next_part
                    skip_next = True
                    cleaned_parts.append(next_part)
                    i += 1
            continue
        
        # Detect URLs
        if (part.startswith(('http://', 'https://', 'magnet:', 'torrent:', 'rc:', 'gd:')) or
            ('.' in part and any(part.endswith(ext) for ext in ['.mp4', '.mkv', '.rar', '.zip', '.7z']))):
            links.append(part)
        
        cleaned_parts.append(part)
        i += 1
    
    cleaned_text = " ".join(cleaned_parts)
    return links, should_merge, custom_name, cleaned_text


def get_video_extensions() -> list:
    """Get list of supported video extensions"""
    return ['.mkv', '.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.ts', '.mpg', '.mpeg', '.3gp']


def is_video_file(filename: str) -> bool:
    """Check if a file is a video based on extension"""
    ext = os.path.splitext(filename)[1].lower()
    return ext in get_video_extensions()


def get_readable_file_size(size_in_bytes: int) -> str:
    """Convert bytes to human readable format"""
    if not size_in_bytes or size_in_bytes == 0:
        return "0 B"
    
    units = ["B", "KB", "MB", "GB", "TB", "PB"]
    index = 0
    size = float(size_in_bytes)
    
    while size >= 1024 and index < len(units) - 1:
        size /= 1024
        index += 1
    
    return f"{size:.2f} {units[index]}"


def get_readable_time(seconds: int) -> str:
    """Convert seconds to human readable format"""
    if seconds <= 0:
        return "0s"
    
    periods = [("d", 86400), ("h", 3600), ("m", 60), ("s", 1)]
    result = ""
    
    for period_name, period_seconds in periods:
        if seconds >= period_seconds:
            period_value, seconds = divmod(seconds, period_seconds)
            result += f"{int(period_value)}{period_name}"
    
    return result if result else "0s"


def get_progress_bar_string(percentage: float, length: int = 12) -> str:
    """Create a progress bar string"""
    percentage = min(max(percentage, 0), 100)
    filled = int(percentage / 100 * length)
    bar = "■" * filled + "□" * (length - filled)
    return f"[{bar}]"


def get_eta_string(start_time: float, current: int, total: int) -> str:
    """Calculate and format ETA string"""
    if current == 0 or total == 0:
        return "N/A"
    
    elapsed = time.time() - start_time
    if elapsed < 1:
        return "Calculating..."
    
    speed = current / elapsed
    if speed == 0:
        return "N/A"
    
    remaining = (total - current) / speed
    return get_readable_time(int(remaining))


def get_speed_string(speed: float) -> str:
    """Format speed string"""
    if speed <= 0:
        return "0 B/s"
    
    units = ["B/s", "KB/s", "MB/s", "GB/s", "TB/s"]
    index = 0
    while speed >= 1024 and index < len(units) - 1:
        speed /= 1024
        index += 1
    
    return f"{speed:.2f} {units[index]}"
