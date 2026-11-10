import importlib,sys,json,asyncio
from pathlib import Path
from unittest.mock import AsyncMock
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[2]));base=Path(__file__).resolve().parents[1].name
FrameSource=importlib.import_module(base+'.providers.bili_client.media').FrameSource
media=importlib.import_module(base+'.core.media')

@pytest.mark.asyncio
async def test_actual_ffmpeg_frame_extraction_and_source_boundaries(tmp_path):
 source=FrameSource(tmp_path/'media',{},{});video=tmp_path/'synthetic.mp4'
 code,_,_=await source._run_process('ffmpeg','-v','error','-f','lavfi','-i','color=c=red:s=96x64:d=2','-c:v','libx264','-threads','1','-y',str(video),timeout=20)
 assert code==0
 frames=await source._extract_video_frames(str(video),count=3)
 assert len(frames)==3 and all(Path(f).read_bytes().startswith(b'\xff\xd8') for f in frames)
 generate=AsyncMock(return_value='{"observed":true,"frames":[{"index":1,"description":"红色的纯色画面"}]}')
 result=await media.describe_frames(generate,[{'path':f,'seconds':i+.5} for i,f in enumerate(frames)],{'provider':'bilibili'})
 assert '1.50s' in result['text'] and '没有音频' in result['text']
 data=generate.await_args.args[1]
 assert len(data['_validated_image_urls'])==3 and data['_validated_image_urls'][0].startswith('data:image/jpeg;base64,')

@pytest.mark.asyncio
async def test_visual_model_cannot_claim_unattached_or_unseen_images(tmp_path):
 file=tmp_path/'frame.jpg';file.write_bytes(b'jpeg-test')
 for result in [{'observed':False,'frames':[]},{'observed':True,'frames':[{'index':4,'description':'invented'}]}]:
  with pytest.raises(ValueError):await media.describe_frames(AsyncMock(return_value=json.dumps(result)),[{'path':str(file),'seconds':1}],{})

@pytest.mark.asyncio
async def test_media_subprocess_timeout_reaps_process(tmp_path):
 source=FrameSource(tmp_path/'media',{},{});
 with pytest.raises(TimeoutError):await source._run_process(sys.executable,'-c','import time;time.sleep(20)',timeout=.05)
