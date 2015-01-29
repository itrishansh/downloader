#!/bin/python

#new enhanced downloader

import sys
import time
import random
import Queue
import cStringIO
import threading

try:
    import pycurl
except:
    print "Please install pycurl"
    sys.exit(0)

class DownloadThread (threading.Thread):
    def __init__(self,id, name, que, ql, exit, url):
        threading.Thread.__init__(self)
        self.id = id
        self.name = name
        self.q = que
        self.ql = ql
        self.exit = exit
    
    def run(self):
        while not self.exit():
            #print "%s: flag - %d" % (self.name, exitFlag)
            self.ql.acquire()
            if not self.q.empty():
                data = self.q.get()
                self.ql.release()
                print "%s processing %s" % (self.name, data)
                #time.sleep(random.randint(0,10))
            else:
                self.ql.release()
        print "Terminating ", self.name

        
class Downloader:

    def __init__(self, url, name = '', n_threads=2, part_size = 100000000):
        self.url = url
        self.name = name
        self.n_threads = n_threads
        self.part_size = part_size
        self.info = {}
        self.exitFlag = 0
        
        print "getting file information..."
        self.get_info()
        
        self.download()
    
    def create_file(name, size):
        with open(name,"wb") as out:
            out.truncate(size)
    
    def get_info(self):
        c = pycurl.Curl()
        buf = cStringIO.StringIO()
        c.setopt(c.URL, self.url)
        c.setopt(c.HEADER, 1)
        c.setopt(c.NOBODY, 1)
        c.setopt(c.WRITEFUNCTION, buf.write)
        c.perform()
        c.close()
        lines = buf.getvalue()#.splitlines()
        print lines
        lines = lines.split('\r\n')
        status = lines[0]
        #del lines[0]
        for line in lines[1:]:
            b = line.find(':')
            line = [line[:b], line[b+1:]]
            #print "parsing :",line
            if( len(line) is 2):
                self.info[line[0]] = line[1].strip()
		
        #print self.info
        
    def  download(self):
        try:
            self.d_size = long(self.info['Content-Length'])
            print "File size :", self.d_size
        except:
            print "Resume support not available."
            print "Exiting..."
            sys.exit(1)
        
        try:
            if self.info['Accept-Ranges'] != 'bytes':
                print 'It seems that server does not support byte ranges.I don\'t know how to handle this, so I am EXITING. If you know what can be done then please inform author at itrishansh[at]gmail[dot]com.'
                sys.exit(1)
        except:
            print "Server doesn\'t support ranges."
        self.parts = []
        end = 0
        while (end + self.part_size) < self.d_size:
            self.parts.append((str(end), str(end + self.part_size -1)))
            #print (str(end), str(end + self.part_size -1))
            end = end + self.part_size
            #print end
        if end < self.d_size:
            self.parts.append((str(end), ''))
        
        print self.parts
        queueLock = threading.Lock()
        workQueue = Queue.Queue(len(self.parts))
        threads = []
        threadID = 1
        
        # Create new threads
        while threadID <= self.n_threads:
            thread = DownloadThread(threadID, 'Thread-'+str(threadID), workQueue, queueLock, self.exit, self.url)
            thread.start()
            threads.append(thread)
            threadID += 1
        
        # Fill the queue
        queueLock.acquire()
        for part in self.parts:
            workQueue.put(part)
        queueLock.release()
        
        # Wait for queue to empty
        while not workQueue.empty():
            pass
            
        # Notify threads it's time to exit
        #print "Modifying exitFlag"
        self.exitFlag = 1
        
        # Wait for all threads to complete
        for t in threads:
            t.join()
        print "Exiting Main Thread"
        
    def exit(self):
        return self.exitFlag


def main():
    url = 'http://ftp.riken.jp/Linux/fedora/releases/21/Workstation/x86_64/iso/Fedora-Live-Workstation-x86_64-21-5.iso'
    d = Downloader(url)
    
if __name__ == '__main__':
    main()
