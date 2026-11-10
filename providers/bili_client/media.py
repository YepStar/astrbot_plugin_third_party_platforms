"""Frame sampler extracted from B站 AI Bot (MIT), with isolated bounded downloads."""
import asyncio,os,signal,tempfile
from pathlib import Path
from contextlib import asynccontextmanager
import re

class FrameSource:
    def __init__(self,root,credentials,settings):
        self.root=Path(root);self.root.mkdir(parents=True,exist_ok=True);self.root.chmod(0o700)
        self.config=credentials;self.settings=settings

    async def _run_process(self,*args,timeout=60):
        process=await asyncio.create_subprocess_exec(*args,stdout=asyncio.subprocess.PIPE,stderr=asyncio.subprocess.PIPE,start_new_session=True)
        try:
            out,err=await asyncio.wait_for(process.communicate(),min(timeout,120 if args[0]=='yt-dlp' else 30))
            if len(out)+len(err)>100000:raise ValueError('media_diagnostic_limit')
            return process.returncode,out.decode(errors='replace'),err.decode(errors='replace')
        except BaseException:
            try:os.killpg(process.pid,signal.SIGKILL)
            except ProcessLookupError:pass
            await process.wait()
            raise

    @asynccontextmanager
    async def capture(self,bvid):
        if not re.fullmatch(r'BV[0-9A-Za-z]{10}',bvid):raise ValueError('invalid_media_id')
        maximum=max(8,min(256,int(self.settings.get('vision_max_mb',96))))*1024*1024
        count=max(1,min(12,int(self.settings.get('vision_frame_count',5))))
        with tempfile.TemporaryDirectory(prefix='bili-',dir=self.root) as directory:
            root=Path(directory);root.chmod(0o700);cookie=root/'cookies.txt'
            rows=['# Netscape HTTP Cookie File']
            for key,name in [('SESSDATA','SESSDATA'),('BILI_JCT','bili_jct'),('DEDE_USER_ID','DedeUserID'),('BUVID3','buvid3')]:
                value=str(self.config.get(key,''))
                if any(c in value for c in '\r\n\t'):raise ValueError('invalid_media_cookie')
                if value:rows.append(f'.bilibili.com\tTRUE\t/\tFALSE\t0\t{name}\t{value}')
            cookie.write_text('\n'.join(rows)+'\n');cookie.chmod(0o600)
            proxy=[]
            if self.config.get('PROXY_URL'):proxy=['--proxy',str(self.config['PROXY_URL'])]
            args=['yt-dlp','--quiet','--no-warnings','--no-progress','--no-playlist','--retries','1','--fragment-retries','1',
                  '--max-filesize',str(maximum),'--socket-timeout','15','--cookies',str(cookie),
                  '--add-header','Referer: https://www.bilibili.com',
                  '--format','bestvideo[height<=360]/bestvideo[width<=360]/best[height<=360]/worst[vcodec!=none]',
                  '-o',str(root/'video.%(ext)s'),*proxy,'https://www.bilibili.com/video/'+bvid]
            code,_,_=await self._run_process(*args,timeout=120)
            cookie.unlink(missing_ok=True)
            candidates=[p for p in root.iterdir() if p.suffix.lower() in {'.mp4','.mkv','.webm','.mov'} and p.stat().st_size>0]
            if code!=0 or not candidates:raise RuntimeError('video_download_unavailable')
            video=max(candidates,key=lambda p:p.stat().st_size)
            if video.stat().st_size>maximum:raise ValueError('video_size_limit')
            frames=await self._extract_video_frames(str(video),count=count)
            duration=self.sample_duration
            if not frames:raise RuntimeError('video_frames_unavailable')
            result=[]
            for file in frames:
                index=int(Path(file).stem.rsplit('_',1)[-1])
                if Path(file).stat().st_size>2_000_000:raise ValueError('frame_size_limit')
                result.append({'path':file,'seconds':round(duration*(index+1)/(count+1),2)})
            yield result

    async def _extract_video_frames(self, video_path, count=5):
            frame_dir = video_path.rsplit(".", 1)[0] + "_frames"
            os.makedirs(frame_dir, exist_ok=True)
            code, stdout, _ = await self._run_process(
                "ffprobe", "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                video_path, timeout=60,
            )
            try:
                duration = float(stdout.strip()) if code == 0 and stdout.strip() else 0.0
            except ValueError:
                duration = 0.0
            import math
            self.sample_duration=duration
            if not math.isfinite(duration) or duration<=0:return []
            frames = []
            for i in range(count):
                ts = duration * (i + 1) / (count + 1)
                frame_path = os.path.join(frame_dir, f"frame_{i}.jpg")
                code, _, _ = await self._run_process(
                    "ffmpeg", "-y", "-ss", f"{ts:.2f}", "-i", video_path,
                    "-vframes", "1", "-vf", "scale=360:-2", "-q:v", "8",
                    frame_path, timeout=120,
                )
                if code == 0 and os.path.exists(frame_path):
                    frames.append(frame_path)
            return frames
