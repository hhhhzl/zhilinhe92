"""Reproducibly combine author-provided research clips; no synthetic research imagery.
Requires Python 3 with Pillow, Node.js, and ffmpeg on PATH (or pass --ffmpeg).
Run: python3 scripts/build-publication-composites.py
Sources are read from the preserved media arrays in src/publication-data.js.
Use --only mga,2go to rebuild a subset; existing manifest entries are retained.
"""
import pathlib,json,subprocess,hashlib,math,re,concurrent.futures,time,argparse,shutil,tempfile,os
from PIL import Image,ImageDraw,ImageFont
SITE=pathlib.Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--ffmpeg',default=shutil.which('ffmpeg'))
parser.add_argument('--node',default=shutil.which('node'))
parser.add_argument('--only',help='Comma-separated slugs: mga,2go,fedguide,md-coas,mdoc,acc')
options=parser.parse_args()
if not options.ffmpeg or not options.node:parser.error('Provide ffmpeg and Node.js on PATH, or --ffmpeg and --node executable paths.')
FF=pathlib.Path(options.ffmpeg);temp=tempfile.TemporaryDirectory(prefix='publication-composites-');WORK=pathlib.Path(temp.name)
OUT=SITE/'public/assets/publications/gallery'
font_candidates=['/System/Library/Fonts/Supplemental/Arial.ttf','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf','C:/Windows/Fonts/arial.ttf']
FONT=next((x for x in font_candidates if pathlib.Path(x).exists()),None)
if not FONT:parser.error('Arial or DejaVuSans TTF is required for the small source labels.')
source_module=(SITE/'src/publication-data.js').as_uri()
node_code='import {publications} from '+json.dumps(source_module)+';process.stdout.write(JSON.stringify(publications));'
papers=json.loads(subprocess.check_output([options.node,'--input-type=module','-e',node_code],text=True))
original=json.loads((SITE/'public/assets/publications/gallery-sources.json').read_text())
byfile={x['file']:x for x in original['assets']}
prepared={}
for paper in papers:
 for media in paper.get('media',[]):
  if media.get('type')!='video':continue
  path=SITE/'public'/media['src'].removeprefix('./')
  probe=subprocess.run([str(FF),'-hide_banner','-i',str(path)],capture_output=True,text=True).stderr
  match=re.search(r'Duration: (\d+):(\d+):([\d.]+)',probe)
  if not match:raise RuntimeError('Could not read video duration: '+str(path))
  prepared[path.name]={'duration_seconds':int(match[1])*3600+int(match[2])*60+float(match[3])}
# Rows group related experiments, retaining the complete source frame with letterboxing.
layouts={
 'he2026mga':('mga',1200,900,[(3,342),(3,255),(3,255)]),
 'he2026twogo':('2go',1200,900,[(3,236),(2,308),(2,308)]),
 'he2026fedguide':('fedguide',1200,656,[(4,308),(4,308)]),
 'he2026mdcoas':('md-coas',1200,840,[(3,462),(4,338)]),
 'he2026mdoc':('mdoc',1200,856,[(3,408),(3,408)]),
}

def run(args,log):
 p=subprocess.run([str(FF),'-hide_banner','-loglevel','error','-y',*map(str,args)],capture_output=True,text=True)
 pathlib.Path(log).write_text(p.stderr)
 if p.returncode:raise RuntimeError(p.stderr[-2500:])

def fileinfo(path):
 return {'file':'gallery/'+path.name,'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}

def assets(paper):
 return [m for m in paper['media'] if m['type']=='video']

def make(paper):
 pid,width,height,rows=layouts[paper['id']]; clips=assets(paper);n=len(clips);assert sum(x[0] for x in rows)==n
 dest=OUT/f'{pid}-experiments'; positions=[];offset=0;y=16
 for count,h in rows:
  usable=width-32-(count-1)*8;tw=usable//count
  for j in range(count):positions.append({'x':16+j*(tw+8),'y':y,'width':tw,'height':h})
  y+=h+8
 assert y-8+16==height
 duration=math.ceil(max(prepared[pathlib.Path(x['src']).name]['duration_seconds'] for x in clips)*12)/12
 args=[];filters=[];sources=[]
 for i,(m,box) in enumerate(zip(clips,positions)):
  source=SITE/'public'/m['src'].removeprefix('./');assert source.exists()
  args+=['-stream_loop','-1','-threads','1','-i',source]
  title=m.get('caption') or m.get('alt') or f'Experiment {i+1}'
  label=WORK/f'{pid}-label-{i}.txt';label.write_text(title)
  textsize=14
  while ImageFont.truetype(FONT,textsize).getlength(title)>box['width']-20 and textsize>10:textsize-=1
  tw,th=box['width'],box['height']
  filters.append(f"[{i}:v]setpts=PTS-STARTPTS,fps=12,scale=w={tw-12}:h={th-38}:force_original_aspect_ratio=decrease:force_divisible_by=2,pad={tw}:{th}:(ow-iw)/2:(oh-26-ih)/2:color=white,setsar=1,drawbox=x=0:y=ih-26:w=iw:h=26:color=0xf0ede8:t=fill,drawtext=fontfile='{FONT}':textfile='{label}':fontsize={textsize}:fontcolor=0x554e58:x=10:y=h-19[t{i}]")
  provenance=byfile.get('gallery/'+source.name,{})
  sources.append({'file':'gallery/'+source.name,'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'caption':title,'duration_seconds':prepared[source.name]['duration_seconds'],'placement_px':box,'source_url':provenance.get('source_url'),'author_provided_source':provenance.get('author_provided_source')})
 inputs=''.join(f'[t{i}]' for i in range(n));layout='|'.join(f"{p['x']}_{p['y']}" for p in positions)
 filters.append(f'{inputs}xstack=inputs={n}:layout={layout}:fill=white,pad={width}:{height}:0:0:color=white,format=yuv420p[v]')
 graph=WORK/f'{pid}-filter.txt';graph.write_text(';\n'.join(filters))
 mp4=dest.with_suffix('.mp4')
 run(args+['-filter_complex_threads','1','-filter_complex_script',graph,'-map','[v]','-an','-t',duration,'-c:v','libx264','-threads','2','-preset','medium','-crf','24','-pix_fmt','yuv420p','-movflags','+faststart',mp4],WORK/f'{pid}-mp4.log')
 jpg=dest.with_suffix('.jpg');run(['-i',mp4,'-frames:v','1','-q:v','2','-update','1',jpg],WORK/f'{pid}-poster.log')
 gif=dest.with_suffix('.gif');gifwidth=960;giffps=10;colors=192;dither='bayer:bayer_scale=3'
 def gifencode():
  run(['-i',mp4,'-filter_complex_threads','1','-filter_complex',f'[0:v]fps={giffps},scale={gifwidth}:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors={colors}:stats_mode=diff[p];[b][p]paletteuse=dither={dither}:diff_mode=rectangle','-an','-loop','0',gif],WORK/f'{pid}-gif.log')
 gifencode()
 if gif.stat().st_size>12_000_000:
  gifwidth=800;giffps=8;gifencode()
 with Image.open(gif) as im:gifdimensions=list(im.size);gifframes=im.n_frames
 result={'paper_id':paper['id'],'slug':pid,'kind':'simultaneous_experiment_composite','source_count':n,'sources':sources,'duration_seconds':duration,'dimensions':[width,height],'aspect_ratio':f'{width}:{height}','video':{**fileinfo(mp4),'codec':'H.264','pixel_format':'yuv420p','fps':12,'audio':False,'faststart':True},'gif':{**fileinfo(gif),'dimensions':gifdimensions,'fps':giffps,'palette_colors':colors,'dither':dither,'frames':gifframes,'loop':0},'poster':{**fileinfo(jpg),'frame':0},'transform':'All source clips start together, retain source playback speed, and loop independently for the longest source duration. Each complete input frame is aspect-fitted without new cropping. Grid, caption bands, resampling and encoding only. The source clips may already contain upstream crops or time-normalization (see gallery-sources.json).'}
 (WORK/f'{pid}-result.json').write_text(json.dumps(result,indent=2))
 print(pid,'done',n,'sources',duration,'seconds',round(mp4.stat().st_size/1e6,2),'MB MP4',round(gif.stat().st_size/1e6,2),'MB GIF',flush=True)
 return result

def make_acc(paper):
 # Preserve these wide scientific figures at a readable width in a static composition.
 width=840; margin=24; gap=18; labelh=36
 imgs=[]
 for m in paper['media']:
  if not m['src'].endswith('acc_experiment_results.png'):continue
  src=SITE/'public'/m['src'].removeprefix('./');im=Image.open(src).convert('RGB');imgs.append((m,src,im))
 # Only the original experiment results belong here; routing diagrams are mechanism figures.
 content_width=width-2*margin; rows=[]
 for m,src,im in imgs:
  target=min(content_width,im.width);h=round(im.height*target/im.width);rows.append((target,h))
 height=2*margin+sum(h+labelh for w,h in rows)+gap*(len(rows)-1)
 canvas=Image.new('RGB',(width,height),'white');draw=ImageDraw.Draw(canvas);font=ImageFont.truetype(FONT,22);y=margin;sources=[]
 for (m,src,im),(w,h) in zip(imgs,rows):
  im=im.resize((w,h),Image.Resampling.LANCZOS);x=(width-w)//2;canvas.paste(im,(x,y));draw.rectangle((margin,y+h,width-margin,y+h+labelh),fill='#f0ede8');draw.text((margin+12,y+h+6),m.get('caption') or m['alt'],font=font,fill='#554e58')
  prov=byfile.get('gallery/'+src.name,{})
  sources.append({'file':'gallery/'+src.name,'caption':m.get('caption') or m['alt'],'source_url':prov.get('source_url'),'sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'placement_px':{'x':x,'y':y,'width':w,'height':h}});y+=h+labelh+gap
 png=OUT/'acc-results-composite.png';canvas.save(png,optimize=True)
 jpg=OUT/'acc-results-composite.jpg';canvas.save(jpg,quality=92,optimize=True)
 return {'paper_id':paper['id'],'slug':'acc','kind':'static_results_composite','source_count':len(sources),'sources':sources,'dimensions':[width,height],'aspect_ratio':f'{width}:{height}','image':fileinfo(png),'poster':fileinfo(jpg),'transform':'Static presentation of the original experimental-results figure; model diagrams are excluded and handled separately as mechanism figures. No fabricated motion or animated file.'}

if __name__=='__main__':
 start=time.time()
 selected=set(options.only.split(',')) if options.only else None
 chosen=[p for p in papers if p['id'] in layouts and (not selected or layouts[p['id']][0] in selected)]
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(make,chosen))
 if not selected or 'acc' in selected:results.append(make_acc(next(p for p in papers if p['id']=='wang2024antivirus')))
 manifest_path=OUT/'composites-manifest.json'
 if selected and manifest_path.exists():
  retained=[r for r in json.loads(manifest_path.read_text())['artifacts'] if r['slug'] not in selected];results=retained+results
 order=['mga','2go','fedguide','md-coas','mdoc','acc'];results.sort(key=lambda r:order.index(r['slug']))
 manifest={'created':'2026-10-16','rights':original['rights'],'source_manifest':'../gallery-sources.json','note':'Synchronized playback is a presentation device: clips are independent experiments, not synchronized measurements. All 37 input MP4 files are covered. No synthetic research visuals. Original arrays and individual media files remain available.','artifacts':results}
 (OUT/'composites-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 lines=['# Simultaneous experiment composites','',original['rights'],'','Each animation shows every available experiment for that paper at once. Videos retain their source speed; shorter clips loop independently while the longest completes. This is a presentation collage, not evidence that experiments occurred in sync. No input frame is newly cropped; original clips may contain pre-existing crops or time normalization documented in [the original source manifest](../gallery-sources.json).','', 'The GIF and H.264 MP4 for each paper show the same montage. MP4 is the lightweight browser playback version. JPEG posters are the first decoded frame. ACC has only its original static experiment-results figure and therefore has no fabricated animation.','','| Paper | Inputs | Outputs |','| --- | ---: | --- |']
 for r in results:
  names=[r[k]['file'].removeprefix('gallery/') for k in ['video','gif','image','poster'] if k in r];lines.append(f"| {r['slug']} | {r['source_count']} | "+' · '.join(f'[{n}]({n})' for n in names)+' |')
 lines+=['','Per-input original URLs/local provenance, hashes, complete placement coordinates, dimensions, timing and transformations are in [composites-manifest.json](composites-manifest.json). Reproduction script: `scripts/build-publication-composites.py` at the repository root (requires Python/Pillow, Node.js, ffmpeg and the original local media arrays/assets).','']
 (OUT/'COMPOSITES-CREDITS.md').write_text('\n'.join(lines))
 print('TOTAL seconds',round(time.time()-start,2),'bytes',sum(r[k]['bytes'] for r in results for k in ['video','gif','image','poster'] if k in r),flush=True)
