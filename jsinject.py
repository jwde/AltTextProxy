import uuid
from Queue import Queue
from threading import Thread
import mrisa
import json
import string
import time
import re
import heapq
import datetime

num_threads = 10

class JobCollection:
    def __init__(self):
        self.jobs_queue = Queue(maxsize=0)

    def AddJob(self, job):
        ID = job.ID()
        self.jobs_queue.put(job)

    def DoNextJob(self):
        job = self.jobs_queue.get()
        job.Work()
        self.jobs_queue.task_done()


class Job:
    def __init__(self, work, args):
        self.work = work
        self.args = args
        self.done = False
        self._id = filter(lambda c: c.isalnum(), uuid.uuid4().urn)
        self.result = None

    def Work(self):
        self.result = self.work(self.args)
        self.done = True

    def isDone(self):
        return self.done

    def Result(self):
        return self.result

    def ID(self):
        return self._id

def DoWork(job_collection):
    while True:
        job_collection.DoNextJob()

def StartWorkers(job_collection):
    for i in xrange(num_threads):
        worker = Thread(target=DoWork, args=(job_collection,))
        worker.setDaemon(True)
        worker.start()

class LFACacheEntry:
    def __init__(self, ent):
        self.ent = ent
        self.points = 10
     
    def Touch(self):
        self.points += 1

    def Epoch(self):
        self.points *= .9

    def __cmp__(self, other):
        return cmp(self.points, other.points)

    def Get(self):
        return self.ent

class AltTextCache:
    def __init__(self, max_entries):
        self.cache = {}
        self.uuids = {}
        self.heap = []
        self.url_to_heap = {}
        self.max_entries = max_entries
        self.clock = 0
        self.epoch_time = 10
        self.time = datetime.datetime.now()

    def Evict(self):
        LFA = None
        while True:
            LFA = heapq.heappop(self.heap)
            # keep popping until we pop a valid entry
            if LFA[1]:
                break
        del self.cache[LFA.Get()[0]]
        del self.uuids[LFA.Get()[1].ID()]
        del self.url_to_heap[LFA.Get()[0]]

    def Epoch(self):
        for entry in self.cache:
            self.cache[entry].Epoch()

    def Tick(self, n):
        self.clock += n
        while self.clock >= self.epoch_time:
            self.clock -= self.epoch_time
            self.Epoch()

    def UpdateTime(self):
        now = datetime.datetime.now()
        self.Tick((now - self.time).total_seconds())
        self.time = now

    def Add(self, url, job):
        self.UpdateTime()
        while len(self.cache) > self.max_entries:
            self.Evict()
        self.cache[url] = LFACacheEntry((url, job))
        self.uuids[job.ID()] = self.cache[url]
        heap_entry = [self.cache[url], True]
        heapq.heappush(self.heap, heap_entry)
        self.url_to_heap[url] = heap_entry

    def Touch(self, url):
        self.UpdateTime()
        entry = self.url_to_heap[url]
        entry[0].Touch()
        # Invalidate this entry
        entry[1] = False
        # Add modified entry
        new_entry = [entry[0], True]
        self.url_to_heap[url] = new_entry
        heapq.heappush(self.heap, new_entry)

    def HasURL(self, url):
        self.UpdateTime()
        return url in self.cache

    def HasJobID(self, uuid):
        self.UpdateTime()
        return uuid in self.uuids

    def GetByURL(self, url):
        self.UpdateTime()
        self.Touch(url)
        return self.cache[url].Get()[1]

    def GetByJobID(self, uuid):
        self.UpdateTime()
        self.Touch(self.uuids[uuid].Get()[0])
        return self.uuids[uuid].Get()[1]



class Injector:
    def __init__(self):
        self._id = filter(lambda c: c.isalnum(), uuid.uuid4().urn)
        self.job_collection = JobCollection()
        self.alt_cache = AltTextCache(1000)
        StartWorkers(self.job_collection)

    def MakePayload(self, js):
        payload = "<script>"
        loader = filter(lambda c: c.isalnum(), uuid.uuid4().urn)
        payload += "function " + loader + "() { "
        payload += js
        payload += "}\n"
        interval = filter(lambda c: c.isalnum(), uuid.uuid4().urn)
        payload += "var " + interval + " = setInterval(function() {if(document.readyState === \"complete\") {clearInterval(" + interval + "); " + loader + "(); }}, 10);"
        payload += "</script>"
        return payload

    def GetURL(self, uuid):
        return "http://" + self._id + ".com/" + uuid

    # get (class name, javascript payload) to inject into html for an image tag
    def AltTextPayload(self, image_path):
        def GetAltText(image_path):
            reverse_image_scrape = json.loads(mrisa.mrisa_main(image_path))
            if len(reverse_image_scrape['description']) == 0:
                return ""
            description = reverse_image_scrape['description'][0]
            description = re.sub("\"", r'&#34;', description)
            description = re.sub("\'", r'&#39;', description)
            description = re.sub("<", r'&lt;', description)
            description = re.sub(">", r'&gt;', description)
            return filter(lambda c: c in string.printable, description)
        if not self.alt_cache.HasURL(image_path):
            job = Job(GetAltText, image_path)
            self.job_collection.AddJob(job)
            self.alt_cache.Add(image_path, job)
        retrieval_id = self.alt_cache.GetByURL(image_path).ID()
        imgclass = filter(lambda c: c.isalnum(), uuid.uuid4().urn)
        ajaxjs = "var xmlreq; if(window.XMLHttpRequest){xmlreq = new XMLHttpRequest();} else { xmlreq = new ActiveXObject(\"Microsoft.XMLHTTP\");} xmlreq.onreadystatechange = function() {if (xmlreq.readyState == XMLHttpRequest.DONE) {if(xmlreq.status == 200) {document.getElementsByClassName(\"" + imgclass + "\")[0].setAttribute(\"alt\", xmlreq.responseText);}}}; xmlreq.open(\"GET\", \"" + self.GetURL(retrieval_id) + "\", true); xmlreq.send();"
        return (imgclass, self.MakePayload(ajaxjs))


    def ID(self):
        return self._id

    def Retrieve(self, uuid):
        if not self.alt_cache.HasJobID(uuid):
            return ""
        job = self.alt_cache.GetByJobID(uuid)
        while not job.isDone():
            time.sleep(.1)
        return job.Result()
