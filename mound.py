import json
import pathlib
import os
import uuid

# commit e81947e661376251b41e49ee3f5e71dc30adc274

def uuidToDocDirArray(did):
    return [did[0:2], did[2:4], did[4:6], did[6:8], did]

class Mound:
    MOUND_DATA_DIR = '/tmp/mound'

    @staticmethod
    def setup(MOUND_DATA_DIR):
        Mound.MOUND_DATA_DIR = MOUND_DATA_DIR

    def __init__(self, program, version):
        self.did = str(uuid.uuid4())
        self.program = program
        self.version = version
        self.status = -1
        self.blobs = []
        self.sources = []

        self._open()

    def _open(self):
        docDir = os.path.join(Mound.MOUND_DATA_DIR, *uuidToDocDirArray(self.did))
        os.makedirs(docDir)
        self._writeDoc()

    def close(self, status):
        self.status = status
        self._writeDoc()

    def link(self, sourceDID):
        if sourceDID not in self.sources:
            self.sources.append(sourceDID)
        self._writeDoc()

    def _writeDoc(self):
        docPath = os.path.join(Mound.MOUND_DATA_DIR, *uuidToDocDirArray(self.did), 'doc')
        with open(docPath, 'w') as fout:
            fout.write(json.dumps({
                'did': self.did,
                'program': self.program,
                'version': self.version,
                'status': self.status,
                'blobs': self.blobs,
                'sources': self.sources,
            }, separators = (',', ':')))
            fout.write('\n')

    def blob(self, *args):
        if len(args) > 1:
            raise Exception('Max one argument expected.')
        bno = len(self.blobs)
        name = bno if len(args) == 0 else args[0]
        self.blobs.append(name)
        self._writeDoc()
        return bno

    def write(self, bno, data):
        blobPath = os.path.join(Mound.MOUND_DATA_DIR, *uuidToDocDirArray(self.did), str(bno))
        with open(blobPath, 'ab') as fout:
            if isinstance(data, str):
                fout.write(data.encode('utf-8'))
            else:
                fout.write(data)

    def println(self, bno, data):
        self.write(bno, data)
        self.write(bno, '\n')

## NEW STUFF AFTER HERE, NEED TO INTEGRATE INTO mound UPSTREAM?

class MoundDescriptor:
    # obj is a parsed JSON obj, so a dict in python speak.
    def __init__(self, pdid, obj):
        self._pdid = pdid
        self._obj = obj
        self.did = obj['did']
        self.program = obj['program']
        self.version = obj['version']
        self.status = obj['status']
        self.blobs = obj['blobs']
        self.sources = obj['sources']

    def read_blob(self, bno):
        if isinstance(bno, int):
            bno = str(bno)
        elif isinstance(bno, str):
            bno = str(self.blobs.index(bno))
        else:
            raise ValueError('bno is not an int or str')
        with open(os.path.join(self._pdid, bno), 'rb') as fin:
            return fin.read()

    def __repr__(self):
        return repr(self._obj)

def mound_find(did=None, predicate=None, ignore_bad_files=False):
    for l1 in os.listdir(Mound.MOUND_DATA_DIR):
        for l2 in os.listdir(os.path.join(Mound.MOUND_DATA_DIR, l1)):
            for l3 in os.listdir(os.path.join(Mound.MOUND_DATA_DIR, l1, l2)):
                for l4 in os.listdir(os.path.join(Mound.MOUND_DATA_DIR, l1, l2, l3)):
                    # l5 is the full uuid did
                    for l5 in os.listdir(os.path.join(Mound.MOUND_DATA_DIR, l1, l2, l3, l4)):
                        # TODO: Turn this inner portion into a function, mound_load() or maybe doc_load() so I can use it elsewhere. Then I don't need a did filter on this fn.
                        pdid = os.path.join(Mound.MOUND_DATA_DIR, l1, l2, l3, l4, l5)
                        pdoc = os.path.join(pdid, 'doc')
                        try:
                            with open(pdoc, 'r') as fin:
                                content = fin.read()
                                d = MoundDescriptor(pdid, json.loads(content))
                            # This is going to need some restructuring if more filters are added and combinations of them can be used
                            # As it stands you already can't use did and predicate at the same time
                            if did is not None:
                                if l5 == did:
                                    yield d
                            elif predicate is not None:
                                if predicate(d):
                                    yield d
                            else:
                                yield d
                        except:
                            if not ignore_bad_files:
                                raise
