#!/usr/bin/python

# This file parse command line options and call downloader.

import sys, getopt
import logging

from downloader.Downloader import Downloader

def usage():
    print "%s -u <url> -o <outputfile> -n <nthreads> -p <max part size>" % sys.argv[0]

def main():
    url = ''
    output_file = 'dummy'
    nthread = 20
    part = 10000000
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hu:o:n:p:", ["url=", "outputfile=", "nthread=", "part="])
    except getopt.GetoptError:
        
        sys.exit(2)
    
    for opt, arg in opts:
        if opt == '-h':
            usage()
            sys.exit(0)
        elif opt in ('-u', '--url'):
            url = arg
        elif opt in ('-o', '--outputfile'):
            output_file = arg
        elif opt in ('-n', '--nthread'):
            try:
                nthread = int(arg)
            except ValueError:
                usage()
                sys.exit(2)
        elif opt in ('-p', '--part'):
            try:
                part = int(arg)
            except ValueError:
                usage()
                sys.exit(2)
    
    if url == '':
        usage()
        sys.exit(2)
    #print "url = %s" % url
    #print "output file = %s" % output_file
    #print 'remove below line'
    #url = 'http://download.fedoraproject.org/pub/fedora/linux/releases/21/Workstation/x86_64/iso/Fedora-Live-Workstation-x86_64-21-5.iso'
    d = Downloader(url, output_file, nthread, part)
    
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
#handler.setFormatter(formatter)
if __name__ == '__main__':
    main()
