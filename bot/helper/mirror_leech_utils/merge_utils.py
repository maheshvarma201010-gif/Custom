import asyncio
from os import path as ospath
from shutil import rmtree
from aiofiles.os import remove as aioremove
from ..telegram_helper.message_utils import send_message, edit_message
from ..ext_utils.bot_utils import new_task
from ..ext_utils.db_handler import database
from ... import LOGGER, DOWNLOAD_DIR, user_data

class MergedTask:
    def __init__(self, client, message, links, is_leech, is_qbit, is_jd, is_nzb, options, user_dict, args):
        self.client = client
        self.message = message
        self.links = links
        self.is_leech = is_leech
        self.is_qbit = is_qbit
        self.is_jd = is_jd
        self.is_nzb = is_nzb
        self.options = options
        self.user_dict = user_dict
        self.args = args
        self.sub_tasks = []
        self.merge_id = f"merge_{message.id}_{message.from_user.id if message.from_user else message.sender_chat.id}"
        self.status_message = None
        self.merge_path = None
        
    async def start_merge(self):
        """Start the merged task process"""
        # Create status message
        self.status_message = await send_message(
            self.message, 
            f"🔄 **Merge Task Started**\n"
            f"📥 Total links: {len(self.links)}\n"
            f"⚙️ Status: Initializing downloads..."
        )
        
        # Create directory for merged downloads
        from ... import DOWNLOAD_DIR
        self.merge_path = f"{DOWNLOAD_DIR}{self.merge_id}/"
        
        # Create sub-tasks for each link
        for idx, link in enumerate(self.links, 1):
            from .mirror_leech_utils import Mirror  # Import here to avoid circular import
            
            # Create modified args for sub-task
            sub_args = self.args.copy()
            sub_args["link"] = link
            sub_args["-i"] = 0  # Reset multi counter
            
            # Create sub-task message
            sub_message = await send_message(
                self.message,
                f"🔗 Downloading {idx}/{len(self.links)}: {link[:50]}..."
            )
            if self.message.from_user:
                sub_message.from_user = self.message.from_user
            else:
                sub_message.sender_chat = self.message.sender_chat
            
            # Create sub-task
            sub_task = Mirror(
                client=self.client,
                message=sub_message,
                is_qbit=self.is_qbit,
                is_leech=self.is_leech,
                is_jd=self.is_jd,
                is_nzb=self.is_nzb,
                parent_merge_task=self.merge_id
            )
            
            self.sub_tasks.append({
                'task': sub_task,
                'link': link,
                'status': 'pending',
                'path': None
            })
        
        # Start all sub-tasks
        for sub_task in self.sub_tasks:
            await sub_task['task'].new_event()
            sub_task['status'] = 'downloading'
        
        # Monitor completion
        await self.monitor_merge()
    
    async def monitor_merge(self):
        """Monitor all sub-tasks and merge when complete"""
        while True:
            await asyncio.sleep(3)
            
            # Update status message
            completed = sum(1 for t in self.sub_tasks if t['status'] == 'completed')
            failed = sum(1 for t in self.sub_tasks if t['status'] == 'failed')
            downloading = sum(1 for t in self.sub_tasks if t['status'] == 'downloading')
            
            status_text = (
                f"🔄 **Merge Task Progress**\n"
                f"✅ Completed: {completed}/{len(self.sub_tasks)}\n"
                f"⬇️ Downloading: {downloading}\n"
                f"❌ Failed: {failed}\n"
                f"⚙️ Overall Status: {'Merging...' if completed == len(self.sub_tasks) else 'Downloading...'}"
            )
            
            await edit_message(self.status_message, status_text)
            
            # Check if all tasks are complete
            if completed == len(self.sub_tasks):
                await self.perform_merge()
                break
            elif failed > 0:
                await self.handle_failure()
                break
    
    async def perform_merge(self):
        """Merge all downloaded files"""
        await edit_message(self.status_message, "🔄 **Merging files...** Please wait.")
        
        # Collect all download paths
        download_paths = []
        for sub_task in self.sub_tasks:
            if sub_task['task'].download_path:
                download_paths.append(sub_task['task'].download_path)
        
        if not download_paths:
            await send_message(self.message, "❌ No files found to merge!")
            return
        
        # Try to use existing merge function from split.py if available
        try:
            from ..modules.split import merge_multiple_files
            merged_file_path = await merge_multiple_files(download_paths, self.merge_id)
        except ImportError:
            # Fallback: Simple merge by copying files to merge directory
            from aiofiles.os import listdir, rename
            import shutil
            
            merged_file_path = f"{self.merge_path}/merged_output"
            os.makedirs(merged_file_path, exist_ok=True)
            
            for path in download_paths:
                if ospath.isdir(path):
                    for item in await listdir(path):
                        src = ospath.join(path, item)
                        dst = ospath.join(merged_file_path, item)
                        shutil.move(src, dst)
                else:
                    shutil.move(path, merged_file_path)
        
        # Upload the merged files
        await edit_message(self.status_message, "📤 **Uploading merged files...**")
        
        if self.is_leech:
            from ..telegram_helper.telegram_upload import upload_to_telegram
            await upload_to_telegram(merged_file_path, self.message, self.user_dict)
        else:
            from ..mirror_leech_utils.upload_utils.gdrive_upload import upload_to_gdrive
            await upload_to_gdrive(merged_file_path, self.message, self.user_dict)
        
        # Cleanup
        await self.cleanup()
        
        await edit_message(
            self.status_message,
            f"✅ **Merge Completed Successfully!**\n"
            f"📦 Total files merged: {len(download_paths)}\n"
            f"💾 Merged path: {merged_file_path}"
        )
    
    async def handle_failure(self):
        """Handle failed downloads"""
        failed_tasks = [t for t in self.sub_tasks if t['status'] == 'failed']
        error_msg = f"❌ **Merge Failed**\n\nFailed downloads:\n"
        for task in failed_tasks:
            error_msg += f"• {task['link'][:100]}...\n"
        error_msg += f"\nPlease check individual downloads and try again."
        await send_message(self.message, error_msg)
        await self.cleanup()
    
    async def cleanup(self):
        """Clean up temporary files"""
        try:
            if self.merge_path and ospath.exists(self.merge_path):
                rmtree(self.merge_path, ignore_errors=True)
        except Exception as e:
            LOGGER.error(f"Error cleaning up merge directory: {e}")
