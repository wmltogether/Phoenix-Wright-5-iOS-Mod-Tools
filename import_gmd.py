# -*- coding: utf-8 -*-
from libMT_Framework import dir_fn
import codecs,os,struct
from StringIO import StringIO
def getIndexDict():
    fp=open('log.txt','rb')
    dict0={}
    lines=fp.readlines()
    for line in lines:
        if "|" in line:
            fname = line.split('|')[0]
            original_name = line.split('|')[1]
            dict0['%s.txt'%fname] = original_name.replace('++','\\')
    fp.close()
    return dict0
def makestr(lines):
    string_list = []
    head_list = []
    num = len(lines)
    for index,line in enumerate(lines):
        if u'####' in line:
            head_list.append(line[5:-7])
            i = 1
            string = ''
            while True:
                if index+i >= num:
                    break
                if '####' in lines[index+i]:
                    break
                string += lines[index+i]
                i += 1
            string_list.append(string[:-4])
    return string_list, head_list
def import_gmd(fn):
    name_dict = getIndexDict()
    original_name = name_dict[fn]
    text = codecs.open('c\%s'%fn,'rb','utf-8')
    q = open(original_name,'rb')
    fp =StringIO()
    fp.write(q.read())
    q.close()
    fp.seek(0)
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
        q_ofs = real_offset + len(bstr) + 1
    fp.truncate(q_ofs)
    fp.seek(q_ofs)
    lines = text.readlines()
    string_list, head_list = makestr(lines)
    text_string_dict = {}
    for i in range(len(string_list)):
        string = string_list[i]
        head = head_list[i]
        sid,pid = int(head.split(',')[1],10),int(head.split(',')[2],10)
        text_string_dict[(sid,pid)] = string
    slist = []
    plist = []
    ptr = open('p\%s'%fn,'rb')
    plines = ptr.readlines()
    bstring = ''
    for i in range(len(plines)):
        sid,pid = int(plines[i].split('|')[0],10),int(plines[i].split('|')[1],10)
        pctr = plines[i].split('|')[2]
        if (sid,pid) in text_string_dict:
            pctr = text_string_dict[(sid,pid)]
        if not (pid==0 and sid!=0):
            plist.append(pctr)
        #print(pctr)
        if pid==0 and sid!=0:
            slist.append(''.join(plist))
            plist=[]
            plist.append(pctr)
            #print(pctr)
    slist.append(''.join(plist))
    for i in range(len(slist)):
        string = slist[i]
        string = string.replace('\r','')
        string = string.replace('\n','')
        string = string.replace(r'[CR]','\r')
        string = string.replace(r'[LF]','\n')
        data = string.encode('utf-8')
        fp.write(data)
        fp.write('\x00')
    end_ofs = fp.tell()
    size = end_ofs - q_ofs
    fp.seek(0x20)
    fp.write(struct.pack('I',size))
    finaldata = fp.getvalue()
    fp.flush()
    import_name = original_name.replace('assets\\','import\\')
    if not os.path.exists('/'.join(import_name.split('\\')[:-1])):
        os.makedirs('/'.join(import_name.split('\\')[:-1]))
    dest = open(import_name,'wb')
    dest.write(finaldata)
    dest.close()
def main():
    fl=os.listdir('c')
    for fn in fl:
        import_gmd(fn)
if __name__ == "__main__":
    main()
