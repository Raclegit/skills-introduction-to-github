import subprocess, os
F="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
W,H=1920,1080
# (duration, bg color, big text, small text, accent)
scenes=[
 (3.5,"0x0b0f1a","TV KILLER?","XGIMI Horizon 20 Max","0xffb703",1),
 (3.5,"0x1b1030","5700","ISO LUMENS - DAYLIGHT READY","0xff6b35"),
 (3.5,"0x061a24","TRIPLE LASER 4K","X-Master RGB engine","0x00e5ff"),
 (3.5,"0x1a0b0b","20,000:1","CONTRAST  |  110% BT.2020","0xff3d71"),
 (3.5,"0x0a1a10","300\"  -  240Hz","1ms INPUT LAG - HDR GAMING","0x39ff88"),
 (3.5,"0x0f1424","GOOGLE TV","+ Google Home built in","0x7aa2ff"),
 (3.5,"0x14110a","LOSSLESS OPTICS","Lens shift + optical zoom","0xffd166",1),
 (4.5,"0x0b0f1a","WORTH IT?","LINK IN DESCRIPTION  -  LIKE & SUBSCRIBE","0xffb703",1),
]
parts=[]
for i,sc in enumerate(scenes):
    d,bg,big,small,acc=sc[:5]; prod=len(sc)>5
    out=f"s{i}.mp4"
    open(f'big{i}.txt','w').write(big); open(f'small{i}.txt','w').write(small.replace('  -  ','\n') if len(sc)>5 else small)
    fs=190 if len(big)<=10 else 120
    if prod: fs=130 if len(big)<=10 else 84; sfs=44
    else: sfs=54
    vf=(
     f"drawbox=x=0:y=0:w=iw:h=14:color={acc}@1:t=fill,"
     f"drawbox=x=0:y=ih-14:w='iw*t/{d}':h=14:color={acc}@1:t=fill,"
     f"drawtext=fontfile={F}:textfile=big{i}.txt:expansion=none:fontsize={fs}:fontcolor={acc}:"
       f"x={'90' if prod else '(w-text_w)/2'}:y='(h-text_h)/2-60+max(0,(0.35-t))*400':"
       f"alpha='min(1,t/0.25)':borderw=6:bordercolor=black@0.6,"
     f"drawtext=fontfile={F}:textfile=small{i}.txt:expansion=none:fontsize={sfs}:fontcolor=white:"
       f"x={'90' if prod else '(w-text_w)/2'}:y=(h/2)+140:alpha='min(1,max(0,(t-0.35)/0.3))',"
     f"vignette=PI/4,fade=t=out:st={d-0.15}:d=0.15"
    )
    base=["ffmpeg","-y","-loglevel","error","-f","lavfi","-i",f"color=c={bg}:s={W}x{H}:r=30:d={d}"]
    if prod:
        fc=(f"[0:v]{vf}[bg];[1:v]scale=700:-1,format=rgba[p];"
            f"[bg][p]overlay=x='W-w-50+max(0,0.5-t)*1400':y='(H-h)/2+20+8*sin(t*3)':format=auto")
        subprocess.run(base+["-loop","1","-framerate","30","-i","product.png","-filter_complex",fc,"-t",str(d),"-pix_fmt","yuv420p",out],check=True)
    else:
        subprocess.run(base+["-vf",vf,"-pix_fmt","yuv420p",out],check=True)
    parts.append(out)
open("list.txt","w").write("".join(f"file '{p}'\n" for p in parts))
total=sum(s[0] for s in scenes)
subprocess.run(["ffmpeg","-y","-loglevel","error","-f","concat","-i","list.txt","-c","copy","video_only.mp4"],check=True)
# synth beat: kick every 0.5s + hat on offbeats
expr="0.6*sin(2*PI*(55+80*exp(-30*mod(t,0.5)))*t)*exp(-7*mod(t,0.5))+0.12*(random(0)-0.5)*exp(-40*mod(t+0.25,0.5))"
subprocess.run(["ffmpeg","-y","-loglevel","error","-f","lavfi","-i",f"aevalsrc='{expr}':s=44100:d={total}",
  "-i","video_only.mp4","-filter_complex",f"[0:a]afade=t=out:st={total-1}:d=1,volume=0.9[a]",
  "-map","1:v","-map","[a]","-c:v","copy","-c:a","aac","-shortest","XGIMI_Horizon_20_Max_teaser.mp4"],check=True)
print(total)
