# Ok this file is just a copy of the GPT2 one
# which downloads the model from their repository.
# I just changed it to download automatically the model found in the config file
# This code is part of their repository at https://github.com/openai/gpt-2/
# licensed with Modified MIT License - Software Copyright (c) 2019 OpenAI


import os
import sys
import requests
from tqdm import tqdm

import json

with open("config.json", "r") as read_file:
        config = json.load(read_file)
        
        
        
# 1558M, 774M, 355M, 345M, 124M, and 117M
model = config['generator']['model']

os.mkdir('./models/')

subdir = os.path.join('models', model)
if not os.path.exists(subdir):
    os.makedirs(subdir)
subdir = subdir.replace('\\','/') # needed for Windows

for filename in ['checkpoint','encoder.json','hparams.json','model.ckpt.data-00000-of-00001', 'model.ckpt.index', 'model.ckpt.meta', 'vocab.bpe']:

    r = requests.get("https://storage.googleapis.com/gpt-2/" + subdir + "/" + filename, stream=True)

    with open(os.path.join(subdir, filename), 'wb') as f:
        file_size = int(r.headers["content-length"])
        chunk_size = 1000
        with tqdm(ncols=100, desc="Fetching " + filename, total=file_size, unit_scale=True) as pbar:
            # 1k for chunk_size, since Ethernet packet size is around 1500 bytes
            for chunk in r.iter_content(chunk_size=chunk_size):
                f.write(chunk)
                pbar.update(chunk_size)
