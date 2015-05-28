# -*- coding: utf-8 -*-
import os,codecs,zlib,trace
import struct
import libBlowFish
global senario_key
def getClassDict():
    ClassDict={}
    ClassDict[0x242bb29a]=('gmd text format','.gmd')
    ClassDict[0x22FA09]=('hpe format','.hpe')
    ClassDict[0x26E7FF]=('ccl format','.ccl')
    ClassDict[0x86B80F]=('plexp format','.plexp')
    ClassDict[0xFDA99B]=('ntr format','.ntr')
    ClassDict[0x2358E1A]=('spkg format','.spkg')
    ClassDict[0x2373BA7]=('spn format','.spn')
    ClassDict[0x2833703]=('efs format','.efs')
    ClassDict[0x4B4BE62]=('tmd format','.tmd')
    ClassDict[0x22948394]=('gui format','.gui')
    ClassDict[0x241F5DEB]=('tex format','.tex')
    ClassDict[0x10C460E6]=('msg format','.msg')
    return ClassDict
def get_resources_key():
    lr='imaguy_uyrag_igurustim_'
    r9='enokok_ikorodo_odohuran'
    r3=0
    senario_key=''
    for i in range(0,23,1):
        j=((ord(r9[i:i+1]) ^ ord(lr[22-i:23-i]))|r3)&0xff
        senario_key+=chr(j)
        r3=r3+0x40
    return senario_key
def dir_fn(adr):
    dirlst=[]
    for root,dirs,files in os.walk(adr):
        for name in files:
            adrlist=os.path.join(root, name)
            dirlst.append(adrlist)
    return dirlst
def getsize(fn):
    fsize=os.path.getsize(fn)
    return fsize
def unpack_arc(fn,key):
    ClassDict=getClassDict()
    fp=open(fn,'rb')
    magic = '\x41\x52\x43\x43'
    if fp.read(4) != magic:
        fp.close()
        return None
    ver,nums = struct.unpack('<HH',fp.read(4))
    flist = []
    for i in range(nums):
        index_block = fp.read(0x50)
        index_block = libBlowFish.decrypt_data(index_block,key)
        fname = index_block[:64].rstrip(b'\x00').decode('latin-1')
        ftype = struct.unpack('<I',index_block[0x40:0x44])[0]
        zsize = struct.unpack('<I',index_block[0x44:0x48])[0]
        sizetmp = struct.unpack('<I',index_block[0x48:0x4c])[0]
        #print('sizetmp:%08x'%sizetmp)
        size = sizetmp - (sizetmp>>24<<24)
        #print('size:%08x'%size)
        offset = struct.unpack('<I',index_block[0x4c:0x50])[0]
        comFlag = True
        if size == zsize:
            comFlag = False
        flist.append((fname,ftype,zsize,sizetmp,offset,comFlag))
        #print('%s,%08x,%08x,%08x,%08x'%(fname,ftype,zsize,sizetmp,offset))
    
    for (fname,ftype,zsize,size,offset,comFlag) in flist:
        destdir = '%s_unpacked\\%s'%(fn,'\\'.join(fname.split('\\')[:-1]))
        if ftype in ClassDict:
            extname = ClassDict[ftype][1]
        else:
            extname = '.bin'
        print('decompressing %s at:%08x with %08x'%(fname,offset,zsize))
        if not os.path.exists(destdir):
            os.makedirs(destdir)
        dest=open('%s\\%s%s'%(destdir,fname.split('\\')[-1],extname),'wb')
        fp.seek(offset)
        bstr=fp.read(zsize)
        bstr=libBlowFish.decrypt_data(bstr,key)
        print('zlib header check:%02x'%struct.unpack('>H',bstr[:2])[0])
        if comFlag:
            bstr=zlib.decompress(bstr)
        dest.write(bstr)
        dest.close()
def repack_arc(fn,key):
    ClassDict=getClassDict()
    print('repacking %s '%fn)
    base_addr = 0x8000
    offset = 0x8000
    if not os.path.exists('%s_unpacked\\'%fn):
        return None
    fp = open(fn,'rb+')
    magic = '\x41\x52\x43\x43'
    if fp.read(4) != magic:
        fp.close()
        return None
    ver,nums = struct.unpack('<HH',fp.read(4))
    flist = []
    for i in range(nums):
        tmp_ofs = fp.tell()
        index_block = fp.read(0x50)
        index_block = libBlowFish.decrypt_data(index_block,key)
        fname = index_block[:64].rstrip(b'\x00').decode('latin-1')
        
        ftype = struct.unpack('<I',index_block[0x40:0x44])[0]
        zsize = struct.unpack('<I',index_block[0x44:0x48])[0]
        sizetmp = struct.unpack('<I',index_block[0x48:0x4c])[0]
        size = sizetmp - (sizetmp>>24<<24)
        offset = struct.unpack('<I',index_block[0x4c:0x50])[0]
        comFlag = True
        flist.append((tmp_ofs,fname,ftype,comFlag))
        #print(fname,ftype,zsize,size,offset,comFlag)
    boffset = 0x8000
    fp.truncate(boffset)
    for (tmp_ofs,fname,ftype,comFlag) in flist:
        destdir = '%s_unpacked\\%s'%(fn,'\\'.join(fname.split('\\')[:-1]))
        if ftype in ClassDict:
            extname = ClassDict[ftype][1]
        else:
            extname = '.bin'
        dest_name = '%s\\%s%s'%(destdir,fname.split('\\')[-1],extname)
        dest = open(dest_name,'rb')
        zdata = dest.read()
        zlibdata=zlib.compress(zdata)
        sdata = libBlowFish.encrypt_data(zlibdata,key)
        print('eompressed size:%08x'%len(zlibdata))
        dest.close()
        index_block = ''
        index_block += fname.encode('latin-1')
        print(dest_name)
        index_block += ('\x00'*(0x40 - len(fname.encode('latin-1'))%0x40))
        index_block += struct.pack('<I',ftype)
        index_block += struct.pack('<I',len(sdata))
        index_block += struct.pack('<I',(len(zdata)|0x40000000))
        index_block += struct.pack('<I',boffset)
        #print('packing:zsize:%08x'%len(zdata),'size:%08x'%(len(file_data)<<3|0x0b010))
        #print('%s,%08x,%08x,%08x,%08x'%(fname,ftype,len(zdata),(len(file_data)|0x40000000),offset))
        block = libBlowFish.encrypt_data(index_block,key)
        #print(dblock,hex(tmp_ofs))
        fp.seek(tmp_ofs)
        fp.write(block)
        fp.seek(boffset)
        fp.write(sdata)
        print('encrypted size:%08x'%len(sdata))
        boffset += len(sdata)
        print('end offset:%08x'%boffset)
    fp.close()

        
        
        
        
