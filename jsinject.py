import uuid
from Queue import Queue
from threading import Thread
import mrisa
import json
import string

num_threads = 10

class JobCollection:
    def __init__():
        # uuid -> Job
        self.jobs = {}
        self.jobs_queue = Queue(maxsize=0)

    def AddJob(job):
        ID = job.ID()
        self.jobs[ID] = job
        self.jobs_queue.put(job)

    def GetJob(ID):
        return self.jobs[ID]

    def DoNextJob():
        job = self.jobs_queue.get()
        job.Work()
        self.jobs_queue.task_done()


class Job:
    def __init__(work, args):
        self.work = work
        self.args = args
        self.done = False
        self._id = filter(lambda c: c.isalnum(), uuid.uuid4().urn)
        self.result = None

    def Work():
        self.result = self.work(self.args)
        self.done = True

    def isDone():
        return self.done

    def Result():
        return self.result

    def ID():
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
    def __init__():
        self._id = filter(lambda c: c.isalnum(), uuid.uuid4().urn)
        self.job_collection = JobCollection()
        StartWorkers(self.job_collection)

    def MakePayload(js):
# TODO -- update to run only when page is fully loaded
        payload = "<script>"
        loader = filer(lambda c: c.isalnum(), uuid.uuid4().urn)
        payload += "function " + loader + "() { "
        payload += js
        payload += "}\n"
        payload += loader + "();"
        payload += "</script>"

    def AltTextPayload(image_path):
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
# TODO -- add javascript payload to make ajax request


    def ID():
        return self._id

def alttextjshandler(uuid):
