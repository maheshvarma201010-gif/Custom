# bot/helper/mirror_leech_utils/merge_utils.py

import asyncio
import os
import re
import shutil
from asyncio import create_subprocess_exec, sleep
from asyncio.subprocess import PIPE
from os import path as ospath
from pathlib import Path
from shutil import rmtree, move
from typing import List, Tuple, Optional, Dict, Any

from ... import LOGGER, DOWNLOAD_DIR, user_data, Config
from ..telegram_helper.message_utils import send_message, edit_message
from ..ext_utils.bot_utils import natural_sort_key, new_task


class VideoMerger:
    """Handles merging of multiple video files into one using FFmpeg"""
    
    VIDEO_EXTENSIONS = ['.mkv', '.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.ts', '.mpg', '.mpeg', '.3gp']
    
    @classmethod
    async def get_video_files(cls, directory: str, sort_by_date: bool = False) -> List[str]:
        """Get all video files in directory sorted by order"""
        if not os.path.exists(directory):
            return []
        
        video_files = []
        for ext in cls.VIDEO_EXTENSIONS:
            video_files.extend(Path(directory).glob(f'*{ext}'))
            video_files.extend(Path(directory).glob(f'*{ext.upper()}'))
        
        # Remove duplicates
        unique_files = list(set(video_files))
        
        if sort_by_date:
            # Sort by modification time (order of download completion)
            unique_files.sort(key=lambda x: os.path.getmtime(x))
        else:
            # Natural sort by name (Episode 1, Episode 2, Episode 10)
            unique_files.sort(key=lambda x: natural_sort_key(x.stem))
        
        return [str(f) for f in unique_files]
    
    @classmethod
    async def create_concat_file(cls, video_files: List[str], concat_path: str) -> None:
        """Create FFmpeg concat demuxer file"""
        with open(concat_path, 'w', encoding='utf-8') as f:
            for video in video_files:
                # Escape special characters in filename
                safe_path = video.replace("'", "'\\''")
                f.write(f"file '{safe_path}'\n")
    
    @classmethod
    async def merge_videos(cls, video_files: List[str], output_path: str) -> Tuple[bool, str]:
        """Merge videos using FFmpeg concat demuxer (fast copy, no re-encode)"""
        if len(video_files) < 2:
            return False, "Need at least 2 videos to merge"
        
        LOGGER.info(f"Merging {len(video_files)} videos: {[os.path.basename(f) for f in video_files]}")
        
        concat_file = output_path + ".concat.txt"
        await cls.create_concat_file(video_files, concat_file)
        
        # Try stream copy first (fast, no quality loss)
        cmd = [
            'ffmpeg', '-y',
            '-f', 'concat',
            '-safe', '0',
            '-i', concat_file,
            '-c', 'copy',
            output_path
        ]
        
        try:
            process = await create_subprocess_exec(*cmd, stdout=PIPE, stderr=PIPE)
            stdout, stderr = await process.communicate()
            
            # Clean up concat file
            if os.path.exists(concat_file):
                os.remove(concat_file)
            
            if process.returncode == 0:
                LOGGER.info(f"Merge successful: {output_path}")
                return True, output_path
            
            # If stream copy fails, try re-encoding
            error_msg = stderr.decode() if stderr else "Unknown error"
            LOGGER.warning(f"Stream copy failed: {error_msg[:200]}, trying re-encode...")
            
            if "codec" in error_msg.lower() or "non-monotonous" in error_msg.lower():
                return await cls.merge_videos_reencode(video_files, output_path)
            
            return False, f"Merge failed: {error_msg[:200]}"
            
        except Exception as e:
            if os.path.exists(concat_file):
                os.remove(concat_file)
            return False, str(e)
    
    @classmethod
    async def merge_videos_reencode(cls, video_files: List[str], output_path: str) -> Tuple[bool, str]:
        """Merge with re-encoding (slower but compatible with different codecs)"""
        concat_file = output_path + ".concat.txt"
        await cls.create_concat_file(video_files, concat_file)
        
        cmd = [
            'ffmpeg', '-y',
            '-f', 'concat',
            '-safe', '0',
            '-i', concat_file,
            '-c:v', 'libx264',
            '-c:a', 'aac',
            '-preset', 'fast',
            output_path
        ]
        
        try:
            process = await create_subprocess_exec(*cmd, stdout=PIPE, stderr=PIPE)
            stdout, stderr = await process.communicate()
            
            if os.path.exists(concat_file):
                os.remove(concat_file)
            
            if process.returncode == 0:
                LOGGER.info(f"Re-encode merge successful: {output_path}")
                return True, output_path
            
            error_msg = stderr.decode() if stderr else "Unknown error"
            return False, f"Re-encoding merge failed: {error_msg[:200]}"
            
        except Exception as e:
            if os.path.exists(concat_file):
                os.remove(concat_file)
            return False, str(e)
    
    @classmethod
    async def should_merge(cls, user_id: int, directory: str, force_merge: bool = False) -> Tuple[bool, List[str]]:
        """Check if files should be merged"""
        if force_merge:
            video_files = await cls.get_video_files(directory)
            # Also check extracted directory if exists
            extracted_dir = directory + "_extracted"
            if os.path.exists(extracted_dir):
                video_files.extend(await cls.get_video_files(extracted_dir))
            return len(video_files) >= 2, video_files
        
        user_dict = user_data.get(user_id, {})
        auto_merge = user_dict.get("AUTO_MERGE", False)
        if not auto_merge:
            auto_merge = getattr(Config, 'AUTO_MERGE', False)
        
        if not auto_merge:
            return False, []
        
        video_files = await cls.get_video_files(directory)
        extracted_dir = directory + "_extracted"
        if os.path.exists(extracted_dir):
            video_files.extend(await cls.get_video_files(extracted_dir))
        
        return len(video_files) >= 2, video_files
    
    @classmethod
    async def perform_merge(cls, user_id: int, directory: str, custom_name: str = "", force_merge: bool = False, listener=None) -> Tuple[bool, Optional[str], List[str]]:
        """
        Perform video merge operation
        Args:
            user_id: User ID
            directory: Directory containing videos
            custom_name: Custom name for merged file (without extension)
            force_merge: Force merge even if AUTO_MERGE is disabled
            listener: Listener for status updates
        Returns: (success, merged_file_path, list_of_files_to_delete)
        """
        should_merge, video_files = await cls.should_merge(user_id, directory, force_merge)
        
        if not should_merge:
            if force_merge:
                return False, "No video files found to merge!", []
            return False, None, []
        
        # Determine output path
        if custom_name:
            # Clean custom name for filesystem
            custom_name = "".join(c for c in custom_name if c.isalnum() or c in ' ._-')
            if not custom_name.endswith('.mkv'):
                custom_name += '.mkv'
            output_path = os.path.join(directory, custom_name)
        else:
            # Generate name from folder or first file
            folder_name = os.path.basename(directory.rstrip('/'))
            if folder_name and folder_name not in ["downloads", "leech", "", " "]:
                output_path = os.path.join(directory, f"{folder_name}.mkv")
            else:
                # Use first video file's base name
                base_name = Path(video_files[0]).stem
                output_path = os.path.join(directory, f"{base_name}_merged.mkv")
        
        # Avoid overwriting existing files
        counter = 1
        original_path = output_path
        while os.path.exists(output_path):
            name_part = Path(original_path).stem
            ext = Path(original_path).suffix
            output_path = os.path.join(directory, f"{name_part}_{counter}{ext}")
            counter += 1
        
        if listener and hasattr(listener, 'onDownloadError'):
            await listener.onDownloadError(f"🔄 Merging {len(video_files)} videos in order...")
        
        # Perform merge
        success, result = await cls.merge_videos(video_files, output_path)
        
        if not success:
            return False, result, []
        
        # Files to delete after upload (original videos)
        files_to_delete = video_files.copy()
        
        extracted_dir = directory + "_extracted"
        if os.path.exists(extracted_dir):
            files_to_delete.append(extracted_dir)
        
        return True, output_path, files_to_delete


class MergedTask:
    """Handles merging multiple downloads into one task"""
    
    def __init__(
        self,
        client,
        message,
        links: List[str],
        is_leech: bool,
        is_qbit: bool,
        is_jd: bool,
        is_nzb: bool,
        options: str,
        user_dict: dict,
        args: dict,
        custom_merge_name: str = "",
        force_merge: bool = False
    ):
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
        self.custom_merge_name = custom_merge_name
        self.force_merge = force_merge
        self.sub_tasks = []
        self.user_id = message.from_user.id if message.from_user else message.sender_chat.id
        self.merge_id = f"merge_{self.user_id}_{message.id}_{int(asyncio.get_event_loop().time())}"
        self.status_message = None
        self.merge_path = None
        self.merged_file_path = None
        self.is_cancelled = False
        self.tag = getattr(self, 'tag', '')
        self.extract = args.get("-e", False) or args.get("e", False)
        self.compress = args.get("-z", False)
        
    async def start_merge(self):
        """Start the merged task process"""
        # Send initial status message
        status_text = (
            f"🔄 **Auto Merge Task Started**\n\n"
            f"📥 **Total links:** {len(self.links)}\n"
            f"🎯 **Mode:** {'Leech' if self.is_leech else 'Mirror'}\n"
            f"⚡ **Force Merge:** {self.force_merge}\n"
            f"📦 **Extract archives:** {self.extract}\n"
            f"🔧 **Compress:** {self.compress}\n\n"
            f"📝 **Custom name:** {self.custom_merge_name if self.custom_merge_name else 'Auto-generated'}\n\n"
            f"⏳ Initializing downloads..."
        )
        
        self.status_message = await send_message(self.message, status_text)
        
        # Create merge directory
        self.merge_path = f"{DOWNLOAD_DIR}{self.merge_id}/"
        os.makedirs(self.merge_path, exist_ok=True)
        
        from ...modules.mirror_leech import Mirror
        
        # Create sub-tasks for each link
        for idx, link in enumerate(self.links, 1):
            if self.is_cancelled:
                await self._cancel_merge()
                return
            
            # Create a copy of args for sub-task
            sub_args = self.args.copy() if self.args else {}
            sub_args["link"] = link
            sub_args["-i"] = 0
            
            if self.extract:
                sub_args["-e"] = True
            
            # Create a dummy message for sub-task
            sub_message = await send_message(
                self.message,
                f"🔗 **Downloading {idx}/{len(self.links)}:**\n`{link[:80]}...`"
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
                parent_merge_task=self
            )
            
            sub_task.user = self.message.from_user or self.message.sender_chat
            sub_task.tag = self.tag
            sub_task.mid = f"{self.merge_id}_{idx}"
            sub_task.download_path = f"{self.merge_path}part_{idx}/"
            
            self.sub_tasks.append({
                'task': sub_task,
                'link': link,
                'status': 'pending',
                'index': idx,
                'download_path': sub_task.download_path
            })
        
        # Start all sub-tasks
        for sub_task in self.sub_tasks:
            if self.is_cancelled:
                await self._cancel_merge()
                return
            
            await sub_task['task'].new_event()
            sub_task['status'] = 'downloading'
        
        # Monitor and merge
        await self._monitor_merge()
    
    async def _monitor_merge(self):
        """Monitor all sub-tasks and merge when complete"""
        while not self.is_cancelled:
            await asyncio.sleep(3)
            
            completed = 0
            failed = 0
            downloading = 0
            
            for sub_task in self.sub_tasks:
                task = sub_task['task']
                
                # Check task status
                if hasattr(task, 'is_completed') and task.is_completed:
                    if sub_task['status'] != 'completed':
                        sub_task['status'] = 'completed'
                        completed += 1
                elif hasattr(task, 'is_failed') and task.is_failed:
                    if sub_task['status'] != 'failed':
                        sub_task['status'] = 'failed'
                        failed += 1
                elif sub_task['status'] == 'downloading':
                    downloading += 1
                elif sub_task['status'] == 'pending':
                    downloading += 1
            
            # Update status message
            status_text = (
                f"🔄 **Auto Merge Progress**\n\n"
                f"📥 **Total links:** {len(self.sub_tasks)}\n"
                f"✅ **Completed:** {completed}\n"
                f"⬇️ **Downloading:** {downloading}\n"
                f"❌ **Failed:** {failed}\n\n"
                f"📝 **Custom name:** {self.custom_merge_name if self.custom_merge_name else 'Auto-generated'}"
            )
            
            await edit_message(self.status_message, status_text)
            
            # Check if all completed
            if completed == len(self.sub_tasks):
                await self._perform_merge()
                break
            
            # Check if any failed
            if failed > 0:
                await self._handle_failure()
                break
        
        if self.is_cancelled:
            await self._cancel_merge()
    
    async def _perform_merge(self):
        """Merge all downloaded files in order"""
        await edit_message(
            self.status_message,
            "🔄 **Merging files...**\n\nPlease wait while files are being merged in order."
        )
        
        # Collect all downloaded files in order
        all_files = []
        
        for sub_task in self.sub_tasks:
            task = sub_task['task']
            download_path = sub_task['download_path']
            
            # Find downloaded files
            if os.path.exists(download_path):
                for root, dirs, files in os.walk(download_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        all_files.append(file_path)
            
            # Also check task.dir if exists
            if hasattr(task, 'dir') and task.dir and os.path.exists(task.dir):
                for root, dirs, files in os.walk(task.dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        if file_path not in all_files:
                            all_files.append(file_path)
        
        if not all_files:
            await send_message(self.message, "❌ No files found to merge!")
            return
        
        # Get video files in order (natural sorting or by download order)
        video_files = await VideoMerger.get_video_files(self.merge_path, sort_by_date=True)
        
        # Also check individual download paths for videos
        for sub_task in self.sub_tasks:
            download_path = sub_task['download_path']
            if os.path.exists(download_path):
                sub_videos = await VideoMerger.get_video_files(download_path)
                for video in sub_videos:
                    if video not in video_files:
                        video_files.append(video)
        
        if len(video_files) < 2:
            await send_message(self.message, "❌ Not enough video files found to merge! Need at least 2 videos.")
            return
        
        # Determine output name
        if self.custom_merge_name:
            output_name = self.custom_merge_name
            if not output_name.endswith('.mkv'):
                output_name += '.mkv'
        else:
            # Try to get name from first file or folder
            first_name = Path(video_files[0]).stem
            output_name = f"{first_name}_merged.mkv"
        
        output_path = os.path.join(self.merge_path, output_name)
        
        # Perform merge
        await edit_message(
            self.status_message,
            f"🔄 **Merging {len(video_files)} videos...**\n\n"
            f"📝 Output: {output_name}\n"
            f"⚙️ This may take a few minutes..."
        )
        
        success, result = await VideoMerger.merge_videos(video_files, output_path)
        
        if not success:
            await send_message(self.message, f"❌ Merge failed: {result}")
            return
        
        self.merged_file_path = output_path
        
        # Upload the merged file
        await self._upload_merged_file()
    
    async def _upload_merged_file(self):
        """Upload the merged file to Telegram or Cloud"""
        await edit_message(
            self.status_message,
            f"✅ **Merge Complete!**\n\n"
            f"📁 File: {os.path.basename(self.merged_file_path)}\n"
            f"💾 Size: {os.path.getsize(self.merged_file_path) / (1024*1024):.2f} MB\n\n"
            f"📤 Uploading to Telegram..."
        )
        
        try:
            if self.sub_tasks:
                main_task = self.sub_tasks[0]['task']
                
                if self.is_leech:
                    from ..mirror_leech_utils.telegram_uploader import TelegramUploader
                    main_task.dir = self.merge_path
                    main_task.name = os.path.basename(self.merged_file_path)
                    main_task.size = os.path.getsize(self.merged_file_path)
                    
                    uploader = TelegramUploader(main_task, self.merge_path)
                    await uploader.upload()
                else:
                    # For mirror upload to cloud
                    from ..mirror_leech_utils.gdrive_utils.upload import GoogleDriveUpload
                    uploader = GoogleDriveUpload(main_task, self.merge_path)
                    await uploader.upload()
                
                await edit_message(
                    self.status_message,
                    f"✅ **Merge Completed Successfully!**\n\n"
                    f"📦 Total links: {len(self.links)}\n"
                    f"🎬 Merged files: {len(await VideoMerger.get_video_files(self.merge_path))}\n"
                    f"📁 Output: `{os.path.basename(self.merged_file_path)}`"
                )
            else:
                await send_message(self.message, f"✅ Merge completed!\nFile saved at: {self.merged_file_path}")
        
        except Exception as e:
            LOGGER.error(f"Upload error in merge task: {e}")
            await send_message(
                self.message,
                f"⚠️ Merge completed but upload failed: {str(e)}\n"
                f"📁 File saved at: `{self.merged_file_path}`"
            )
        
        # Cleanup
        await self._cleanup()
    
    async def _handle_failure(self):
        """Handle failed downloads in merge task"""
        failed_tasks = [t for t in self.sub_tasks if t['status'] == 'failed']
        
        error_msg = (
            f"❌ **Merge Task Failed**\n\n"
            f"Failed downloads ({len(failed_tasks)}/{len(self.sub_tasks)}):\n"
        )
        
        for task in failed_tasks[:10]:  # Show first 10 failures
            error_msg += f"• `{task['link'][:80]}...`\n"
        
        if len(failed_tasks) > 10:
            error_msg += f"\n... and {len(failed_tasks) - 10} more"
        
        await send_message(self.message, error_msg)
        await self._cleanup()
    
    async def _cancel_merge(self):
        """Cancel the entire merge task"""
        for sub_task in self.sub_tasks:
            if hasattr(sub_task['task'], 'cancel_task'):
                sub_task['task'].cancel_task()
        
        await send_message(self.message, "❌ Merge task cancelled by user.")
        await self._cleanup()
    
    async def _cleanup(self):
        """Clean up temporary files and directories"""
        try:
            if self.merge_path and os.path.exists(self.merge_path):
                shutil.rmtree(self.merge_path, ignore_errors=True)
            
            # Clean up sub-task directories
            for sub_task in self.sub_tasks:
                if sub_task.get('download_path') and os.path.exists(sub_task['download_path']):
                    shutil.rmtree(sub_task['download_path'], ignore_errors=True)
                    
        except Exception as e:
            LOGGER.error(f"Merge task cleanup error: {e}")
    
    def cancel_task(self):
        """Public method to cancel the merge task"""
        self.is_cancelled = True
