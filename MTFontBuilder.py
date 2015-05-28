# -*- coding: utf-8 -*-
from PIL import Image,ImageDraw,ImageFont
import codecs
import struct
from bitio import *
#from GIDecode import createRGBA8888
global logcat
logcat = codecs.open('log.txt','wb','utf-16')
def checkMaxPages(string,width,height,font_size):
    
    Font = ImageFont.truetype("xhei.ttc", font_size-2)
    str_lst = []
    x=0
    y=0
    page_buffer=[]
    print('Max unicode string:%d'%len(string))
    n=0
    for char in string:
        
        char_w,char_h=Font.getsize(char)
        if x +1 < width and y + font_size + 1< height:
            page_buffer.append(char)
            x += char_w +1
            if x + char_w >= 1024:
                y += font_size +1
                x = 0
        else:
            x = 0
            y = 0
            str_lst.append(page_buffer)
            page_buffer = []
            n+=1
        
        
    str_lst.append(page_buffer)
    return str_lst
def math_xy(unicode_char,x,y,char_width,char_height,pid):
    char_code = struct.unpack('H',unicode_char.encode('utf-16')[2:])[0]
    char_bin = struct.pack('I',char_code)
    pid_bin = chr(pid)
    a = x & 0xff
    b = y&0xf
    c = x>>8
    d = y>>4
    if a>255 or b>255 or c>255 or d>255 or (b<<4)+c>255:
        print(unicode_char,a,b,c,d)
    xybin = chr(a)+chr((b<<4)+c)+chr(d)
    nullbin = chr(0)
    
    a = (char_width & 0xff)
    b = char_height&0xf
    c = char_width>>8
    d = char_height>>4
    if a>255 or b>255 or c>255 or d>255 or b<<4+c>255:
        print(a,b,c,d)
    if a==0:
        print(u'%s'%unicode_char,(char_width,char_height),(a,b,c,d))
    chr_wh_bin = chr(a)+chr((b<<4)+c)+chr(d)
    rw_bin = chr(char_width)
    nullbin2 = '\x00\x00\x00'
    return char_bin+pid_bin+xybin+nullbin+chr_wh_bin+rw_bin+nullbin2
    
def str2fnt(string,font_size,h):
    res_block=''
    n=0
    str_lst=checkMaxPages(string,1024,h,32)
    for i in range(len(str_lst)):
        x=0
        y=0
        char_list = str_lst[i]
        im = Image.new(mode='RGBA',size=(1024,1024),color=(255,255,255,0))
        ImageFont.load_default()
        draw = ImageDraw.Draw(im)
        Font = ImageFont.truetype("xhei.ttc", font_size-2)
        for char in char_list:
            char_tuple=Font.getsize(char)
            
            draw.text((x,y),char,fill=(255,255,255,255),font=Font)#CR：x>1024:y+=font_size+1
            logcat.write('id:%d,%s,%d,%d\r\n'%(i,char,x,y))
            char_width = char_tuple[0]
            char_height = font_size+1
            bindat = math_xy(char,x,y,char_width,char_height,i)
            res_block += bindat
            x += char_tuple[0]+1
            if x + char_tuple[0] >= 1024:
                y += font_size+1
                x = 0
        im.save('font00_jpn_%02d_BM_NOMIP.tex.PVRTC4.png'%i,'png')
    return res_block
def test():
    
    text=codecs.open('char.txt','rb','utf-16')
    textdata=text.read()
    text.close()
    res_block=str2fnt(textdata,32,1024)
    dest = open('font00_jpn.bin','wb')
    dest.write('\x47\x46\x44\x00')
    dest.write('\x06\x0c\x01\x00')
    dest.write('\x00\x00\x00\x00')
    dest.write('\x03\x00\x00\x00')
    dest.write('\x00\x00\x00\x00')
    dest.write('\x20\x00\x00\x00')
    dest.write('\x03\x00\x00\x00')
    dest.write(struct.pack('I',len(res_block)/16))
    dest.write('\x01\x00\x00\x00')
    dest.write('\x00\x00\xe4\x41')
    dest.write('\x00\x00\x90\x40')
    dest.write('\x00\x00\x90\x40')
    dest.write('\x1e\x00\x00\x00')
    dest.write('UI\\0_system\\00_font\\font00_jpn'+'\x00')
    dest.write(res_block)
    dest.close()
test()
