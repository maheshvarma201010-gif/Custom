import asyncio
import os
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
        self.download_paths = []

    async def start_merge(self):
        """Start the merged task process"""
        self.status_message = await send_message(
            self.message,
            f"🔄 **Merge Task Started**\n"
            f"📥 Total links: {len(self.links)}\n"
            f"⚙️ Status: Initializing downloads..."
        )

        self.merge_path = f"{DOWNLOAD_DIR}{self.merge_id}/"
        os.makedirs(self.merge_path, exist_ok=True)

        from ...modules.mirror_leech import Mirror

        for idx, link in enumerate(self.links, 1):
            sub_args = self.args.copy()
            sub_args["link"] = link
            sub_args["-i"] = 0

            sub_message = await send_message(
                self.message,
                f"🔗 Downloading {idx}/{len(self.links)}: {link[:50]}..."
            )
            if self.message.from_user:
                sub_message.from_user = self.message.from_user
            else:
                sub_message.sender_chat = self.message.sender_chat

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
                'index': idx
            })

        for sub_task in self.sub_tasks:
            await sub_task['task'].new_event()
            sub_task['status'] = 'downloading'

        await self.monitor_merge()

    async def monitor_merge(self):
        """Monitor all sub-tasks and merge when complete"""
        while True:
            await asyncio.sleep(3)

            completed = 0
            failed = 0
            downloading = 0
            
            for sub_task in self.sub_tasks:
                task = sub_task['task']
                if hasattr(task, 'is_completed') and task.is_completed:
                    sub_task['status'] = 'completed'
                    completed += 1
                    if hasattr(task, 'download_path') and task.download_path:
                        self.download_paths.append(task.download_path)
                    elif hasattr(task, 'path') and task.path:
                        self.download_paths.append(task.path)
                elif hasattr(task, 'is_failed') and task.is_failed:
                    sub_task['status'] = 'failed'
                    failed += 1
                elif sub_task['status'] == 'downloading':
                    downloading += 1

            status_text = (
                f"🔄 **Merge Task Progress**\n"
                f"✅ Completed: {completed}/{len(self.sub_tasks)}\n"
                f"⬇️ Downloading: {downloading}\n"
                f"❌ Failed: {failed}\n"
            )

            await edit_message(self.status_message, status_text)

            if completed == len(self.sub_tasks):
                await self.perform_merge()
                break
            elif failed > 0:
                await self.handle_failure()
                break
            
            await asyncio.sleep(2)

    async def perform_merge(self):
        """Merge all downloaded files"""
        await edit_message(self.status_message, "🔄 **Merging files...** Please wait.")

        if not self.download_paths:
            for sub_task in self.sub_tasks:
                task = sub_task['task']
                if hasattr(task, 'download_path') and task.download_path:
                    self.download_paths.append(task.download_path)
                elif hasattr(task, 'path') and task.path:
                    self.download_paths.append(task.path)

        if not self.download_paths:
            await send_message(self.message, "❌ No files found to merge!")
            return

        merged_file_path = self.merge_path
        
        for path in self.download_paths:
            if ospath.exists(path):
                if ospath.isdir(path):
                    for item in os.listdir(path):
                        src = ospath.join(path, item)
                        dst = ospath.join(merged_file_path, item)
                        if ospath.exists(dst):
                            dst = ospath.join(merged_file_path, f"merged_{item}")
                        os.rename(src, dst)
                else:
                    filename = ospath.basename(path)
                    dst = ospath.join(merged_file_path, filename)
                    if ospath.exists(dst):
                        dst = ospath.join(merged_file_path, f"merged_{filename}")
                    os.rename(path, dst)

        await edit_message(self.status_message, "📤 **Uploading merged files...**")

        try:
            if self.sub_tasks:
                main_task = self.sub_tasks[0]['task']
                if hasattr(main_task, 'upload'):
                    await main_task.upload(merged_file_path)
                else:
                    await send_message(self.message, f"Merged files saved at: {merged_file_path}")
        except Exception as e:
            LOGGER.error(f"Upload error: {e}")
            await send_message(self.message, f"⚠️ Merge completed but upload failed: {e}")

        await self.cleanup()

        await edit_message(
            self.status_message,
            f"✅ **Merge Completed Successfully!**\n"
            f"📦 Total files merged: {len(self.download_paths)}\n"
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
