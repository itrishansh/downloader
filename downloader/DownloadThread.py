import time
import random
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


