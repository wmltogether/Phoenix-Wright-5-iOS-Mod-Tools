# -*- coding: utf-8 -*-
import os,codecs,zlib,trace
import struct,traceback
from libMT_Framework import get_resources_key,unpack_arc,dir_fn
def main():
    print('MT Framework arc package Phoenix Wright 5 ios(arc ver 7)')
    print('using BlowFish xor Method')
    if not os.path.exists('assets/'):
        print('NO assets folder found,please put .arc into assets folder')
        os.makedirs('assets/')
    fl = dir_fn('assets')
    senario_key=get_resources_key()
    for fn in fl:
        unpack_arc(fn,senario_key)
if __name__ == '__main__':
    try:
        main()
    except:
        traceback.print_exc()
    os.system('pause')
    os._exit(0)
