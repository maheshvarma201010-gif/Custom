# bot/helper/ext_utils/bot_utils.py

from html import escape
from psutil import virtual_memory, cpu_percent, disk_usage
from time import time
from asyncio import iscoroutinefunction, gather
from pyrogram.types import InlineKeyboardButton

from ... import task_dict, task_dict_lock, bot_start_time, status_dict, DOWNLOAD_DIR
from ...core.config_manager import Config
from ..telegram_helper.button_build import ButtonMaker

SIZE_UNITS = ["B", "KB", "MB", "GB", "TB", "PB"]


class MirrorStatus:
    STATUS_UPLOAD = "Upload"
    STATUS_DOWNLOAD = "Download"
    STATUS_CLONE = "Clone"
    STATUS_QUEUEDL = "QueueDl"
    STATUS_QUEUEUP = "QueueUp"
    STATUS_PAUSED = "Pause"
    STATUS_ARCHIVE = "Archive"
    STATUS_EXTRACT = "Extract"
    STATUS_SPLIT = "Split"
    STATUS_CHECK = "CheckUp"
    STATUS_SEED = "Seed"
    STATUS_SAMVID = "SamVid"
    STATUS_CONVERT = "Convert"
    STATUS_FFMPEG = "FFmpeg"
    STATUS_MERGE = "Merge"  # Added for Auto Merge feature


STATUSES = {
    "ALL": "All",
    "DL": MirrorStatus.STATUS_DOWNLOAD,
    "UP": MirrorStatus.STATUS_UPLOAD,
    "QD": MirrorStatus.STATUS_QUEUEDL,
    "QU": MirrorStatus.STATUS_QUEUEUP,
    "AR": MirrorStatus.STATUS_ARCHIVE,
    "EX": MirrorStatus.STATUS_EXTRACT,
    "SD": MirrorStatus.STATUS_SEED,
    "CL": MirrorStatus.STATUS_CLONE,
    "CM": MirrorStatus.STATUS_CONVERT,
    "SP": MirrorStatus.STATUS_SPLIT,
    "SV": MirrorStatus.STATUS_SAMVID,
    "FF": MirrorStatus.STATUS_FFMPEG,
    "PA": MirrorStatus.STATUS_PAUSED,
    "CK": MirrorStatus.STATUS_CHECK,
    "MG": MirrorStatus.STATUS_MERGE,  # Added for merge status
}


async def get_task_by_gid(gid: str):
    async with task_dict_lock:
        for tk in task_dict.values():
            if hasattr(tk, "seeding"):
                await tk.update()
            if tk.gid() == gid:
                return tk
        return None


async def get_specific_tasks(status, user_id):
    if status == "All":
        if user_id:
            return [tk for tk in task_dict.values() if tk.listener.user_id == user_id]
        else:
            return list(task_dict.values())
    tasks_to_check = (
        [tk for tk in task_dict.values() if tk.listener.user_id == user_id]
        if user_id
        else list(task_dict.values())
    )
    coro_tasks = []
    coro_tasks.extend(tk for tk in tasks_to_check if iscoroutinefunction(tk.status))
    coro_statuses = await gather(*[tk.status() for tk in coro_tasks])
    result = []
    coro_index = 0
    for tk in tasks_to_check:
        if tk in coro_tasks:
            st = coro_statuses[coro_index]
            coro_index += 1
        else:
            st = tk.status()
        if (st == status) or (
            status == MirrorStatus.STATUS_DOWNLOAD and st not in STATUSES.values()
        ):
            result.append(tk)
    return result


async def get_all_tasks(req_status: str, user_id):
    async with task_dict_lock:
        return await get_specific_tasks(req_status, user_id)


def get_readable_file_size(size_in_bytes):
    if not size_in_bytes or size_in_bytes == 0:
        return "0B"

    index = 0
    while size_in_bytes >= 1024 and index < len(SIZE_UNITS) - 1:
        size_in_bytes /= 1024
        index += 1

    return f"{size_in_bytes:.2f}{SIZE_UNITS[index]}"


def get_readable_time(seconds: int):
    if seconds <= 0:
        return "0s"
    periods = [("d", 86400), ("h", 3600), ("m", 60), ("s", 1)]
    result = ""
    for period_name, period_seconds in periods:
        if seconds >= period_seconds:
            period_value, seconds = divmod(seconds, period_seconds)
            result += f"{int(period_value)}{period_name}"
    return result


def time_to_seconds(time_duration):
    try:
        parts = time_duration.split(":")
        if len(parts) == 3:
            hours, minutes, seconds = map(float, parts)
        elif len(parts) == 2:
            hours = 0
            minutes, seconds = map(float, parts)
        elif len(parts) == 1:
            hours = 0
            minutes = 0
            seconds = float(parts[0])
        else:
            return 0
        return hours * 3600 + minutes * 60 + seconds
    except:
        return 0


def speed_string_to_bytes(size_text: str):
    size = 0
    size_text = size_text.lower()
    if "k" in size_text:
        size += float(size_text.split("k")[0]) * 1024
    elif "m" in size_text:
        size += float(size_text.split("m")[0]) * 1048576
    elif "g" in size_text:
        size += float(size_text.split("g")[0]) * 1073741824
    elif "t" in size_text:
        size += float(size_text.split("t")[0]) * 1099511627776
    elif "b" in size_text:
        size += float(size_text.split("b")[0])
    return size


def get_size_bytes(size_text: str):
    """Convert size string to bytes (e.g., '1GB' -> 1073741824)"""
    if not size_text:
        return 0
    size_text = size_text.strip().upper()
    if size_text.endswith("KB"):
        return float(size_text[:-2]) * 1024
    elif size_text.endswith("MB"):
        return float(size_text[:-2]) * 1048576
    elif size_text.endswith("GB"):
        return float(size_text[:-2]) * 1073741824
    elif size_text.endswith("TB"):
        return float(size_text[:-2]) * 1099511627776
    elif size_text.endswith("B"):
        return float(size_text[:-1])
    else:
        return float(size_text)


def get_progress_bar_string(pct):
    if not pct:
        pct = "0%"
    pct = float(pct.strip("%"))
    p = min(max(pct, 0), 100)
    cFull = int(p // 8)
    p_str = "■" * cFull
    p_str += "□" * (12 - cFull)
    return f"[{p_str}]"


def natural_sort_key(filename: str):
    """Natural sorting for filenames (Episode 1, Episode 2, Episode 10)"""
    import re
    parts = re.split(r'(\d+)', filename)
    return [int(part) if part.isdigit() else part.lower() for part in parts]


def extract_links_and_merge_flag(text: str) -> tuple:
    """
    Extract all links and check for merge flag
    Returns: (links_list, should_merge, custom_name, cleaned_text)
    """
    import re
    
    # Split by spaces but respect quotes for merge name
    parts = text.split()
    
    links = []
    should_merge = False
    custom_name = ""
    skip_next = False
    cleaned_parts = []
    
    for i, part in enumerate(parts):
        if skip_next:
            skip_next = False
            cleaned_parts.append(part)
            continue
            
        if part == '-m':
            should_merge = True
            # Check if next part is a quoted name
            if i + 1 < len(parts):
                next_part = parts[i + 1]
                if next_part.startswith('"') and next_part.endswith('"'):
                    custom_name = next_part[1:-1]
                    skip_next = True
                elif next_part.startswith("'") and next_part.endswith("'"):
                    custom_name = next_part[1:-1]
                    skip_next = True
                elif not next_part.startswith('-'):
                    custom_name = next_part
                    skip_next = True
        else:
            cleaned_parts.append(part)
            # Check if it's a URL
            if part.startswith(('http://', 'https://', 'magnet:', 'torrent:', 'rc:', 'gd:')):
                links.append(part)
    
    cleaned_text = " ".join(cleaned_parts)
    return links, should_merge, custom_name, cleaned_text


async def get_readable_message(sid, is_user, page_no=1, status="All", page_step=1):
    msg = ""
    button = None

    tasks = await get_specific_tasks(status, sid if is_user else None)

    STATUS_LIMIT = Config.STATUS_LIMIT
    tasks_no = len(tasks)
    pages = (max(tasks_no, 1) + STATUS_LIMIT - 1) // STATUS_LIMIT
    if page_no > pages:
        page_no = (page_no - 1) % pages + 1
        status_dict[sid]["page_no"] = page_no
    elif page_no < 1:
        page_no = pages - (abs(page_no) % pages)
        status_dict[sid]["page_no"] = page_no
    start_position = (page_no - 1) * STATUS_LIMIT

    task_gids = []
    for index, task in enumerate(
        tasks[start_position : STATUS_LIMIT + start_position], start=1
    ):
        if status != "All":
            tstatus = status
        elif iscoroutinefunction(task.status):
            tstatus = await task.status()
        else:
            tstatus = task.status()
        
        # Get task name safely
        try:
            task_name = task.name()
        except:
            task_name = "Unknown Task"
        
        if task.listener.is_super_chat:
            msg += f"<b>{index + start_position}.<a href='{task.listener.message.link}'>{tstatus}</a>: </b>"
        else:
            msg += f"<b>{index + start_position}.{tstatus}: </b>"
        msg += f"<code>{escape(task_name)}</code>"
        
        if task.listener.subname:
            msg += f"\n<i>{task.listener.subname}</i>"
        
        # Show merge specific info
        if tstatus == MirrorStatus.STATUS_MERGE:
            msg += f"\n<b>Status:</b> Merging videos in order..."
            if hasattr(task, 'merge_progress'):
                msg += f"\n<b>Progress:</b> {task.merge_progress}"
            if hasattr(task, 'videos_merged'):
                msg += f"\n<b>Videos Merged:</b> {task.videos_merged}"
        
        elif tstatus not in [MirrorStatus.STATUS_SEED, MirrorStatus.STATUS_QUEUEUP] and task.listener.progress:
            progress = task.progress()
            msg += f"\n{get_progress_bar_string(progress)} {progress}"
            if task.listener.subname:
                subsize = f"/{get_readable_file_size(task.listener.subsize)}"
                ac = len(task.listener.files_to_proceed)
                count = f"{task.listener.proceed_count}/{ac or '?'}"
            else:
                subsize = ""
                count = ""
            msg += f"\n<b>Processed:</b> {task.processed_bytes()}{subsize}"
            if count:
                msg += f"\n<b>Count:</b> {count}"
            msg += f"\n<b>Size:</b> {task.size()}"
            msg += f"\n<b>Speed:</b> {task.speed()}"
            msg += f"\n<b>ETA:</b> {task.eta()}"
            if (
                tstatus == MirrorStatus.STATUS_DOWNLOAD
                and task.listener.is_torrent
                or task.listener.is_qbit
            ):
                try:
                    msg += f"\n<b>Seeders:</b> {task.seeders_num()} | <b>Leechers:</b> {task.leechers_num()}"
                except:
                    pass
        elif tstatus == MirrorStatus.STATUS_SEED:
            msg += f"\n<b>Size: </b>{task.size()}"
            msg += f"\n<b>Speed: </b>{task.seed_speed()}"
            msg += f"\n<b>Uploaded: </b>{task.uploaded_bytes()}"
            msg += f"\n<b>Ratio: </b>{task.ratio()}"
            msg += f" | <b>Time: </b>{task.seeding_time()}"
        else:
            msg += f"\n<b>Size: </b>{task.size()}"
        
        msg += f"\n<b>Gid: </b><code>{task.gid()}</code>\n\n"
        task_gids.append((index + start_position, task.gid()))

    if len(msg) == 0:
        if status == "All":
            return None, None
        else:
            msg = f"No Active {status} Tasks!\n\n"
    
    buttons = ButtonMaker()
    if not is_user:
        buttons.data_button("📜", f"status {sid} ov", position="header")
    
    if len(tasks) > STATUS_LIMIT:
        msg += f"<b>Page:</b> {page_no}/{pages} | <b>Tasks:</b> {tasks_no} | <b>Step:</b> {page_step}\n"
        buttons.data_button("<<", f"status {sid} pre", position="header")
        buttons.data_button(">>", f"status {sid} nex", position="header")
        if tasks_no > 30:
            for i in [1, 2, 4, 6, 8, 10, 15]:
                buttons.data_button(i, f"status {sid} ps {i}", position="footer")
    
    if status != "All" or tasks_no > 20:
        for label, status_value in list(STATUSES.items()):
            if status_value != status:
                buttons.data_button(label, f"status {sid} st {status_value}")
    
    buttons.data_button("♻️", f"status {sid} ref", position="header")
    button = buttons.build_menu(8)
    
    if task_gids:
        cancel_buttons = [
            InlineKeyboardButton(
                text=f"❌ {num}",
                callback_data=f"status {sid} cancel {gid}",
            )
            for num, gid in task_gids
        ]
        for i in range(0, len(cancel_buttons), 4):
            button.inline_keyboard.append(cancel_buttons[i : i + 4])
    
    # Get system stats
    try:
        cpu_usage = cpu_percent()
        ram_usage = virtual_memory().percent
        disk_free = disk_usage(DOWNLOAD_DIR).free
        uptime = get_readable_time(time() - bot_start_time)
        
        msg += f"<b>CPU:</b> {cpu_usage}% | <b>FREE:</b> {get_readable_file_size(disk_free)}"
        msg += f"\n<b>RAM:</b> {ram_usage}% | <b>UPTIME:</b> {uptime}"
    except:
        msg += f"\n<b>UPTIME:</b> {get_readable_time(time() - bot_start_time)}"
    
    return msg, button


def update_user_ldata(user_id, key, value):
    """Update user data dictionary"""
    from ... import user_data
    if user_id not in user_data:
        user_data[user_id] = {}
    user_data[user_id][key] = value


def new_task(func):
    """Decorator to run async functions as new tasks"""
    from ... import bot_loop
    def wrapper(*args, **kwargs):
        return bot_loop.create_task(func(*args, **kwargs))
    return wrapper
