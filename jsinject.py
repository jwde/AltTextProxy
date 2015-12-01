import uuid
from Queue import Queue
from threading import Thread
import mrisa
import json
import string
import time

num_threads = 10

class JobCollection:
    def __init__(self):
        # uuid -> Job
        self.jobs = {}
        self.jobs_queue = Queue(maxsize=0)

    def AddJob(self, job):
        ID = job.ID()
        self.jobs[ID] = job
        self.jobs_queue.put(job)

    def GetJob(self, ID):
        return self.jobs[ID]

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

class Injector:
    def __init__(self):
        self._id = filter(lambda c: c.isalnum(), uuid.uuid4().urn)
        self.job_collection = JobCollection()
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
        job = Job(GetAltText, image_path)
        self.job_collection.AddJob(job)
        imgclass = filter(lambda c: c.isalnum(), uuid.uuid4().urn)
        ajaxjs = "var xmlreq; if(window.XMLHttpRequest){xmlreq = new XMLHttpRequest();} else { xmlreq = new ActiveXObject(\"Microsoft.XMLHTTP\");} xmlreq.onreadystatechange = function() {if (xmlreq.readyState == XMLHttpRequest.DONE) {if(xmlreq.status == 200) {document.getElementsByClassName(\"" + imgclass + "\")[0].setAttribute(\"alt\", xmlreq.responseText);}}}; xmlreq.open(\"GET\", \"" + self.GetURL(job.ID()) + "\", true); xmlreq.send();"
        return (imgclass, self.MakePayload(ajaxjs))


    def ID(self):
        return self._id

    def Retrieve(self, uuid):
        job = self.job_collection.GetJob(uuid)
        while not job.isDone():
            time.sleep(.1)
        return job.Result()
