import time
import random
import threading

try:
    import pycurl
except:
    print "Please install pycurl"
    sys.exit(0)

class DownloadThread (threading.Thread):
    def __init__(self,id, name, fname, que, ql, exit, url):
        threading.Thread.__init__(self)
        self.id = id
        self.name = name
        self.fname = fname
        self.q = que
        self.ql = ql
        self.exit = exit
        self.url = url
    
    def run(self):
        while not self.exit():
            #print "%s: flag - %d" % (self.name, exitFlag)
            self.ql.acquire()
            if not self.q.empty():
                data = self.q.get()
                self.ql.release()
                print "%s downloading %s" % (self.name, data)
                fp = open( self.fname+'.part'+str(data[2]),'wb')
                c = pycurl.Curl()
                c.setopt(c.URL,self.url)
                part = "%s-%s" %(data[0], data[1])
                #print 'Downloading',part
                c.setopt(c.RANGE, part)
                c.setopt(c.WRITEDATA, fp)
                c.perform()
                fp.close()
                c.close()
                #time.sleep(random.randint(0,10))
            else:
                self.ql.release()
        print "Terminating ", self.name


