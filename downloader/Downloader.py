import os
import sys
import Queue
import cStringIO
import threading

from DownloadThread import DownloadThread

try:
    import pycurl
except:
    print "Please install pycurl"
    sys.exit(0)

class Downloader:

    def __init__(self, url, fname , n_threads=2, part_size = 100000000):
        self.url = url
        self.name = fname
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
        #c.setopt(c.FOLLOWLOCATION, 1)
        c.perform()
        c.close()
        lines = buf.getvalue()#.splitlines()
        #print lines
        lines = lines.split('\r\n')
        status = lines[0]
        #del lines[0]
        for line in lines[1:]:
            b = line.find(':')
            line = [line[:b], line[b+1:]]
            #print "parsing :",line
            if( len(line) is 2):
                self.info[line[0]] = line[1].strip()
        
        #using redirected url
        if status == 'HTTP/1.0 302 Moved Temporarily':
            print "redirecting to %s" % self.info['Location']
            self.url = self.info['Location']
            self.get_info()
            return
        
        #if server tells name of file then set name of file
        #try:
        #    self.info['']
        #except KayError:
        #    pass
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
        self.nparts = len(self.parts)
        
        #print self.parts
        queueLock = threading.Lock()
        workQueue = Queue.Queue(len(self.parts))
        threads = []
        threadID = 1
        
        # Create new threads
        while threadID <= self.n_threads:
            thread = DownloadThread(threadID, 'Thread-'+str(threadID), self.name, workQueue, queueLock, self.exit, self.url)
            thread.start()
            threads.append(thread)
            threadID += 1
        
        # Fill the queue
        queueLock.acquire()
        i = 0
        for part in self.parts:
            workQueue.put(part + (i,))
            i += 1
        queueLock.release()
        del i
        
        # Wait for queue to empty
        while not workQueue.empty():
            pass
            
        # Notify threads it's time to exit
        #print "Modifying exitFlag"
        self.exitFlag = 1
        
        # Wait for all threads to complete
        for t in threads:
            t.join()
        
        print 'Merging downloaded parts'
        self.merge()
        
        print "Exiting Main Thread"
        
    def exit(self):
        return self.exitFlag
        
    def merge(self):
        suffix = '.part'
        fout = open(self.name, "wb")
        for part in xrange(self.nparts):
            fin = open(self.name + suffix + str(part))
            fout.write(fin.read())
            fin.close()
            os.remove(self.name + suffix + str(part))
        fout.close()


