# This script should load all of the sample data from the data directory and train the model. It will save the model to a file to be used
#    stuff from data dir produces an out dir with various things. i.e. the trained model that can be loaded.

import os
from mound import Mound, mound_find

Mound.setup(os.path.join(os.getenv('HOME'), 'mound_data'))

def use_doc(doc):
    return doc.program == 'analogzer-ingest'

for doc in mound_find():
    # TODO: doc.read_blob() to get at the blobs
    # TODO: remember to add these as sources to the training mound I'll be creating.
    pass
