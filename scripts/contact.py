import sys,os,glob
from PIL import Image,ImageDraw
src,out,n=sys.argv[1],sys.argv[2],int(sys.argv[3]) if len(sys.argv)>3 else 48
fs=sorted(glob.glob(src+"/*.png")); os.makedirs(out,exist_ok=True); T=170; C=8
for i in range(0,len(fs),n):
    ch=fs[i:i+n]; R=(len(ch)+C-1)//C; im=Image.new("RGB",(C*T,R*(T+14)),"white"); d=ImageDraw.Draw(im)
    for j,f in enumerate(ch):
        t=Image.open(f).convert("RGB").resize((T,T)); x,y=(j%C)*T,(j//C)*(T+14); im.paste(t,(x,y)); d.text((x+2,y+T),os.path.basename(f)[:-4][-28:],fill="black")
    im.save(f"{out}/sheet_{i//n:02d}.jpg",quality=80)
print("ok")
