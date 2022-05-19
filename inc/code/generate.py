import time
import os
import sys
import random

from zipfile import ZipFile

import numpy as np
import torch

from transformers import GPT2LMHeadModel, GPT2Tokenizer


USE_CUDA = True
CACHE_DIR = os.path.join(os.curdir, "model_cache")
SEED = random.randint(0, 1000)

if not os.path.isdir(CACHE_DIR):
    print("Extracting model...")
    with ZipFile("model.zip") as f:
        f.extractall(CACHE_DIR)

device = "cuda" if torch.cuda.is_available() and USE_CUDA else "cpu"

print(f"Running on {device}")


def load_tokenizer_and_model(model_name_or_path):
    print("Loading tokenizer and model from " + CACHE_DIR)
    tokenizer = GPT2Tokenizer.from_pretrained(model_name_or_path)
    model = GPT2LMHeadModel.from_pretrained(model_name_or_path).to(device)
    return tokenizer, model


def generate(
    model, tok, text,
    do_sample=True, max_length=50, repetition_penalty=5.0,
    top_k=5, top_p=0.95, temperature=1,
    num_beams=None,
    no_repeat_ngram_size=3
    ):
    input_ids = tok.encode(text, return_tensors="pt").to(device)
    out = model.generate(
        input_ids.to(device),
        max_length=max_length,
        repetition_penalty=repetition_penalty,
        do_sample=do_sample,
        top_k=top_k, top_p=top_p, temperature=temperature,
        num_beams=num_beams, no_repeat_ngram_size=no_repeat_ngram_size
    )
    return list(map(tok.decode, out))


def main(beginning):
    np.random.seed(SEED)
    torch.manual_seed(SEED)

    tok, model = load_tokenizer_and_model(CACHE_DIR)

    print("Generating")
    prev_timestamp = time.time()
    generated = generate(model, tok, beginning, max_length=200, top_p=0.95, temperature=0.7)
    time_spent = time.time() - prev_timestamp

    print(generated[0])

    print(f"Elapsed time: {time_spent} s.")


if __name__ == "__main__":
    main(sys.argv[1])
