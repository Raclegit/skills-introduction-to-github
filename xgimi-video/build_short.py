import subprocess
F="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
W,H=1080,1920
# (duration, bg color, big text, small text, accent, show product)
scenes=[
 (2.5,"0x0b0f1a","TV KILLER?","XGIMI Horizon 20 Max","0xffb703",1),
 (2.2,"0x1b1030","5700","ISO LUMENS\nDAYLIGHT READY","0xff6b35",0),
 (2.2,"0x061a24","TRIPLE\nLASER 4K","X-Master RGB engine","0x00e5ff",0),
 (2.2,"0x1a0b0b","20,000:1","CONTRAST\n110% BT.2020","0xff3d71",0),
 (2.2,"0x0a1a10","300\" 240Hz","1ms INPUT LAG\nHDR GAMING","0x39ff88",0),
 (2.2,"0x0f1424","GOOGLE TV","+ Google Home built in","0x7aa2ff",0),
 (2.4,"0x14110a","LOSSLESS\nOPTICS","Lens shift + optical zoom","0xffd166",1),
 (3.5,"0x0b0f1a","WORTH IT?","LINK IN DESCRIPTION\nLIKE & SUBSCRIBE","0xffb703",1),
]
parts=[]
for i,(d,bg,big,small,acc,prod) in enumerate(scenes):
    out=f"v{i}.mp4"
    open(f'vbig{i}.txt','w').write(big); open(f'vsmall{i}.txt','w').write(small)
    longest=max(len(l) for l in big.split("\n"))
    fs=min(220,int(940/(longest*0.74)))
    ty=300 if prod else 640          # text block position
    vf=(
     f"drawbox=x=0:y=0:w=iw:h=16:color={acc}@1:t=fill,"
     f"drawbox=x=0:y=ih-16:w='iw*t/{d}':h=16:color={acc}@1:t=fill,"
     f"drawtext=fontfile={F}:textfile=vbig{i}.txt:expansion=none:fontsize={fs}:fontcolor={acc}:line_spacing=10:"
       f"x=(w-text_w)/2:y='{ty}+max(0,(0.3-t))*500':alpha='min(1,t/0.2)':borderw=6:bordercolor=black@0.6,"
     f"drawtext=fontfile={F}:textfile=vsmall{i}.txt:expansion=none:fontsize=52:fontcolor=white:line_spacing=12:"
       f"x=(w-text_w)/2:y={ty}+{fs*(big.count(chr(10))+1)+60}:alpha='min(1,max(0,(t-0.3)/0.25))',"
     f"vignette=PI/4,fade=t=out:st={d-0.12}:d=0.12"
    )
    base=["ffmpeg","-y","-loglevel","error","-f","lavfi","-i",f"color=c={bg}:s={W}x{H}:r=30:d={d}"]
    if prod:
        fc=(f"[0:v]{vf}[bg];[1:v]scale=960:-1,format=rgba[p];"
            f"[bg][p]overlay=x='(W-w)/2+max(0,0.45-t)*1600':y='H-h-170+10*sin(t*3)':format=auto")
        subprocess.run(base+["-loop","1","-framerate","30","-i","product.png","-filter_complex",fc,"-t",str(d),"-pix_fmt","yuv420p",out],check=True)
    else:
        subprocess.run(base+["-vf",vf,"-pix_fmt","yuv420p",out],check=True)
    parts.append(out)
open("vlist.txt","w").write("".join(f"file '{p}'\n" for p in parts))
total=sum(s[0] for s in scenes)
subprocess.run(["ffmpeg","-y","-loglevel","error","-f","concat","-i","vlist.txt","-c","copy","vvideo_only.mp4"],check=True)
expr="0.6*sin(2*PI*(55+80*exp(-30*mod(t,0.4)))*t)*exp(-8*mod(t,0.4))+0.12*(random(0)-0.5)*exp(-40*mod(t+0.2,0.4))"
subprocess.run(["ffmpeg","-y","-loglevel","error","-f","lavfi","-i",f"aevalsrc='{expr}':s=44100:d={total}",
  "-i","vvideo_only.mp4","-filter_complex",f"[0:a]afade=t=out:st={total-0.8}:d=0.8,volume=0.9[a]",
  "-map","1:v","-map","[a]","-c:v","copy","-c:a","aac","-shortest","XGIMI_Horizon_20_Max_short_9x16.mp4"],check=True)
print(total)
