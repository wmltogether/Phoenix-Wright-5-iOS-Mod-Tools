# -*- coding: utf-8 -*-
from libMT_Framework import dir_fn
import codecs,os,struct
def checkAscii(string):
    try:
        string.encode('ascii')
        return True
    except:
        return False
def export_gmd_msg():
    if not os.path.exists('assets/'):
        print('NO assets folder found,please put .gmd into assets folder')
        os.makedirs('assets/')
    if not os.path.exists('c/'):
        print('NO assets folder found')
        os.makedirs('c/')
    if not os.path.exists('j/'):
        print('NO assets folder found')
        os.makedirs('j/')
    if not os.path.exists('import/'):
        print('NO import folder found')
        os.makedirs('import/')
    index_list=codecs.open(u'log.txt','wb','utf-8')
    fl=dir_fn('assets')
    a=0
    if len(fl) == 0:
        print('Please put gmd folder into "assets" ')
    for i in range(len(fl)):
        fn=fl[i]
        if not (fn[-4:].lower()=='.gmd'):continue
        print(fn)
        real_name = fn.split('\\')[-1]
        new_fn = fn.replace('\\','++')
        id_name = '%04d_%s'%(a,real_name)
        index_list.write('%s|%s|\r\n'%(id_name,new_fn))
        fp=open(fn,'rb')
        dest = codecs.open('j//%s.txt'%id_name,'w','utf-8')
        ptr = codecs.open('p//%s.txt'%id_name,'wb','utf-8')
        if fp.read(4)!= '\x47\x4d\x44\x00':continue
        fp.seek(0x14)
        pnums = struct.unpack('I',fp.read(4))[0]
        fp.seek(0x20)
        size = struct.unpack('I',fp.read(4))[0]
        fp.seek(0x24)
        name_len = struct.unpack('I',fp.read(4))[0]
        name = fp.read(name_len)
        null = fp.read(1)
        plist = []
        for i in range(pnums):
            pid = fp.read(4)
            pstr = fp.read(4)
            if not pstr == '\xff\xff\xff\xff':
                plist.append((struct.unpack('I',pid)[0],struct.unpack('I',pstr)[0]))
        tmp_ofs = fp.tell()
        for i in range(len(plist)):
            (pid,p_addr) = plist[i]
            real_offset = p_addr - plist[0][1] + tmp_ofs
            fp.seek(real_offset)
            #print('%08x'%real_offset)
            bstr = fp.read(0x100).split('\x00')[0]
            string = bstr.decode('utf-8')
            #dest.write('#### control,%d ####\r\n%s\r\n\r\n'%(pid,string))
            q_ofs = real_offset + len(bstr) + 1
        fp.seek(q_ofs)
        #print('%08x'%q_ofs)
        datalist = fp.read().split('\x00')[:len(plist)]
        #print(len(datalist))
        for i in range(len(datalist)):
            data = datalist[i]
            data = data.replace('\r','[CR]')
            data = data.replace('\n','[LF]')
            data = data.replace('<E025 ','\r\n<E025 ')
            data = data.replace('<PAGE>','\r\n<PAGE>')
            data = data.replace('<E023>','\r\n<E023>')
            data = data.replace('<CNTR>','<CNTR>\r\n')
            data = data.replace('<E041 0 12>','<E041 0 12>\r\n')
            data = data.decode('utf-8')
            data = data.replace(u'\r\n<E025 8>‥‥',u'<E025 8>‥‥')
            data = data.replace(u'\r\n<E025 3>！',u'<E025 3>！')
            data = data.replace(u'\r\n<E025 3>。',u'<E025 3>。')
            data = data.replace(u'\r\n<E025 3>、',u'<E025 3>、')
            
            slist = data.split('\r\n')
            for j in range(len(slist)):
                string = slist[j]
                if checkAscii(string):
                    ptr.write('%d|%d|%s|\r\n'%(i,j,string))
                else:
                    ptr.write('%d|%d|%s|\r\n'%(i,j,'TEXT_STRING'))
                    string = string.replace('[LF]','[LF]\r\n')
                    dest.write('#### text,%d,%d ####\r\n%s\r\n\r\n'%(i,j,string))
        dest.close()
        fp.close()
        ptr.close()
        a+=1
export_gmd_msg()
        
        
