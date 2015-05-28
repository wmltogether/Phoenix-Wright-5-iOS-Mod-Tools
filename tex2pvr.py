from cStringIO import StringIO
import codecs,os,struct
from GIDecode import paintRGBA8888,paintRGBA4444
from PIL import Image
def dir_fn(adr):
    dirlst=[]
    for root,dirs,files in os.walk(adr):
        for name in files:
            adrlist=os.path.join(root, name)
            dirlst.append(adrlist)
    return dirlst
def tex2pvr(tex_texture_buffer):
    tBuffer=StringIO()
    tBuffer.write(tex_texture_buffer)
    tBuffer.seek(0)
    magic=tBuffer.read(4)
    if magic=='\x54\x45\x58\x20':
        tBuffer.seek(0xc)
        width=struct.unpack('H',tBuffer.read(2))[0]
        height = width
        tBuffer.seek(0x7)
        color_mode=ord(tBuffer.read(1))
        unk=struct.unpack('H',tBuffer.read(2))[0]
        tBuffer.seek(0x10,0)
        if color_mode == 0x4:
            #PVRTC_4
            Size = width*height/2
        if color_mode == 0x10:
            #RGBA4444
            Size = width*height*2
        if color_mode == 0x20:
            #RGBA8888
            Size = width*height*4
        zdata=tBuffer.read(Size)
        dec_data=zdata
    tBuffer.flush()
    if color_mode==0x4:
        #Build PVRTC4 Header For texture
        pBuffer=StringIO()
        pBuffer.write('\x00'*0x34)
        pBuffer.write('\x00'*(width*height/2))
        pBuffer.seek(0)
        pBuffer.write('\x34\x00\x00\x00')
        pBuffer.write(struct.pack('I',width))
        pBuffer.write(struct.pack('I',height))
        pBuffer.seek(4,1)
        pBuffer.write(struct.pack('I',0x8019))
        pBuffer.write(struct.pack('I',(width*height/2)))
        pBuffer.write(struct.pack('I',4))
        pBuffer.seek(0xc,1)
        pBuffer.write(struct.pack('I',1))
        pBuffer.write('PVR!')
        pBuffer.write(struct.pack('I',1))
        pBuffer.write(dec_data)
        return pBuffer.getvalue(),'PVRTC4'
    elif color_mode==0x20:
        #build 32BPP Header For texture
        pBuffer=StringIO()
        pBuffer.write('\x00'*0x34)
        pBuffer.write('\x00'*(width*height*4))
        pBuffer.seek(0)
        pBuffer.write('\x34\x00\x00\x00')
        pBuffer.write(struct.pack('I',width))
        pBuffer.write(struct.pack('I',height))
        pBuffer.seek(4,1)
        pBuffer.write(struct.pack('I',0x8012))
        pBuffer.write(struct.pack('I',(width*height*4)))
        pBuffer.write(struct.pack('I',0x20))
        pBuffer.write(struct.pack('I',0xff))
        pBuffer.write(struct.pack('I',0xff00))
        pBuffer.write(struct.pack('I',0xff0000))
        pBuffer.write(struct.pack('I',0xff000000))
        pBuffer.write('PVR!')
        pBuffer.write(struct.pack('I',1))
        pBuffer.write(dec_data)
        datalist = paintRGBA8888(width,height,width,height,dec_data,'RGBA')
        return datalist,'RGBA8888'
    elif color_mode==0x10:
        datalist = paintRGBA4444(width,height,width,height,dec_data,'RGBA')
        return datalist,'RGBA4444'
    else:
        print('error color mode,%x'%color_mode)
        return None
def texconverter(fn):
    fp=open(fn,'rb')
    fp.seek(0)
    tex_texture_buffer = fp.read()
    fp.seek(0xc)
    width = struct.unpack('H',fp.read(2))[0]
    pBuffer,ftype = tex2pvr(tex_texture_buffer)
    if ftype == 'RGBA8888':
        im = Image.new('RGBA', (width, width))
        im.putdata(tuple(pBuffer))
        im.save('%s.RGBA8888.PNG'%fn)
    elif ftype == 'PVRTC4':
        im = open('%s.PVRTC4.pvr'%fn,'wb')
        im.write(pBuffer)
        im.close()
    if ftype == 'RGBA4444':
        im = Image.new('RGBA', (width, width))
        im.putdata(tuple(pBuffer))
        im.save('%s.RGBA4444.PNG'%fn)     
    fp.close()
def main():
    fl = dir_fn('images')
    for fn in fl:
        if fn[-4:].lower() == '.tex':
            texconverter(fn)
if __name__ == '__main__':
    main()
        
    
    
