from pathlib import Path
import subprocess, math, glob, os
from PIL import Image, ImageDraw, ImageFont

root = Path.cwd()
dl = Path(os.environ['USERPROFILE']) / 'Downloads'
ff = root / 'tools' / 'ffmpeg' / 'ffmpeg-9.0.2-essentials_build' / 'bin' / 'ffmpeg.exe'
music = Path(r'D:\不知道就别碰\Codex\2026-10-13\z-m-r\work\对比视频背景音乐.MP3')
out = root / '上海对比游_17镜头.mp4'
work = root / 'render_work'
work.mkdir(exist_ok=True)

def find(prefix):
    matches = list(dl.glob(prefix + '*.mp4'))
    if not matches: raise FileNotFoundError(prefix)
    return matches[0]

skyline = find('看魔都夜景')
hostel = find('vlog来看看00后毕业生沪漂住青旅')
snack = find('来上海吃生煎')
street = find('video_#繁华都市')
restaurant = find('video_米二星厨')
hotel = find('video_魔都宝格丽酒店')
car = find('video_上海顶级富婆')
metro = find('video_上海早高峰的地铁')
bus = find('video_有幸见证了中国大陆沃尔沃牌公交车')
fashion = find('video_LACERTA')

# 17 shots: intro + eight everyday Shanghai shots + eight luxury shots.
shots = [
    (skyline, 3, 'title'),
    (hostel, 14, '普通人｜住青旅'),
    (hostel, 72, '普通人｜青旅日常'),
    (snack, 4, '普通人｜路边生煎'),
    (snack, 23, '普通人｜网红小吃'),
    (bus, 8, '普通人｜公交出行'),
    (metro, 4, '普通人｜挤地铁'),
    (street, 12, '普通人｜南京路逛街'),
    (street, 38, '普通人｜步行街打卡'),
    (fashion, 1, '有钱人｜时装周秀场'),
    (fashion, 8, '有钱人｜高端活动'),
    (car, 1, '有钱人｜劳斯莱斯出行'),
    (car, 8, '有钱人｜豪车接送'),
    (restaurant, 8, '有钱人｜米其林晚餐'),
    (restaurant, 47, '有钱人｜私享包厢'),
    (hotel, 12, '有钱人｜宝格丽酒店'),
    (hotel, 65, '有钱人｜顶奢入住'),
]
# Beat points sampled from the Paris reference; 455 frames at 30 fps preserves the full 15.151 s track.
cut_frames = [0,37,55,71,87,103,118,133,149,163,181,211,243,274,332,365,422,455]
assert len(shots) == 17 and len(cut_frames) == 18

font_path = r'C:\Windows\Fonts\msyhbd.ttc'
font = ImageFont.truetype(font_path, 54)
title_font = ImageFont.truetype(font_path, 90)

def bounds(draw, text, f):
    b = draw.textbbox((0,0), text, font=f)
    return b[2]-b[0], b[3]-b[1]

def paint_label(draw, text, x, y, f):
    w,h = bounds(draw,text,f)
    pad_x,pad_y = 12,7
    draw.rectangle((x,y,x+w+pad_x*2,y+h+pad_y*2), fill=(255,255,255,255))
    draw.text((x+pad_x,y+pad_y), text, font=f, fill=(0,0,0,255))

for i, (_, _, text) in enumerate(shots):
    im = Image.new('RGBA', (1080, 1920), (0,0,0,0))
    d = ImageDraw.Draw(im)
    if i == 0:
        lines = ['普通人去上海游玩', 'VS 有钱人的上海奢游']
        centers = [(540, 845), (540, 1010)]
        for line, (cx,cy) in zip(lines, centers):
            w,h = bounds(d,line,title_font)
            pad_x,pad_y = 26,12
            d.rectangle((cx-w//2-pad_x,cy-h//2-pad_y,cx+(w+1)//2+pad_x,cy+(h+1)//2+pad_y), fill=(255,255,255,255))
            d.text((cx,cy),line,font=title_font,fill=(12,12,12,255),anchor='mm')
    else:
        if i <= 8:
            lines = ['普通人：', '住青旅快捷酒店吃网红小吃', '打卡这种景点逛网红景点']
        elif i <= 10:
            lines = ['有钱人：', '与明星同框看时装周']
        elif i <= 12:
            lines = ['有钱人：', '劳斯莱斯同级豪车出行']
        elif i <= 14:
            lines = ['有钱人：', '米其林餐厅用餐']
        else:
            lines = ['有钱人：', '入住顶奢酒店']
        for row,line in enumerate(lines):
            paint_label(d,line,70,185+row*84,font)
    im.save(work / f'caption_{i:02d}.png')

args = [str(ff), '-hide_banner', '-y']
for src, seek, _ in shots:
    args += ['-ss', str(seek), '-i', str(src)]
for i in range(len(shots)):
    args += ['-loop','1','-framerate','30','-i',str(work / f'caption_{i:02d}.png')]
args += ['-i', str(music)]
filters=[]
for i in range(len(shots)):
    nframes = cut_frames[i+1] - cut_frames[i]
    dur = nframes/30
    cleanup = {1:'x=150:y=1565:w=780:h=135',2:'x=150:y=1565:w=780:h=135',3:'x=100:y=1415:w=880:h=155',4:'x=100:y=1415:w=880:h=155',13:'x=130:y=1565:w=820:h=135',14:'x=130:y=1565:w=820:h=135',15:'x=130:y=1580:w=820:h=140',16:'x=130:y=1580:w=820:h=140'}
    clean = f",delogo={cleanup[i]}" if i in cleanup else ''
    filters.append(f'[{i}:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920{clean},fps=30,trim=duration={dur:.9f},setpts=PTS-STARTPTS,setsar=1[v{i}]')
    filters.append(f'[v{i}][{len(shots)+i}:v]overlay=0:0:shortest=1,format=yuv420p,trim=duration={dur:.9f},setpts=PTS-STARTPTS[s{i}]')
filters.append(''.join(f'[s{i}]' for i in range(len(shots))) + f'concat=n={len(shots)}:v=1:a=0[vout]')
args += ['-filter_complex',';'.join(filters),'-map','[vout]','-map',f'{len(shots)*2}:a:0','-t','15.166667','-r','30','-fps_mode','cfr','-c:v','libx264','-preset','medium','-crf','19','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-movflags','+faststart',str(out)]
print('Rendering:', out, flush=True)
print('Shots:',len(shots),'total frames:',cut_frames[-1], 'music:', music.stat().st_size, 'bytes',flush=True)
subprocess.run(args, check=True)
print('DONE',out.stat().st_size,'bytes',flush=True)
