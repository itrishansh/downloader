#!/usr/bin/python

# This file parse command line options and call downloader.

import sys, getopt

from downloader import Downloader, DownloadThread

def main():
    url = ''
    output_file = ''
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hu:o:", ["url=", "outputfile="])
    except getopt.GetoptError:
        print "%s -u <url> -o <outputfile> " % sys.argv[0]
        sys.exit(2)
    
    for opt, arg in opts:
        if opt == '-h':
            print "%s -u <url> -o <outputfile> " % sys.argv[0]
            sys.exit(0)
        elif opt in ('-u', '--url'):
            url = arg
        elif opt in ('-o', '--outputfile'):
            output_file = arg
    
    #print "url = %s" % url
    #print "output file = %s" % output_file
    print 'remove below line'
    url = 'http://ftp.riken.jp/Linux/fedora/releases/21/Workstation/x86_64/iso/Fedora-Live-Workstation-x86_64-21-5.iso'
    d = Downloader(url, output_file)
    

if __name__ == '__main__':
    main()
