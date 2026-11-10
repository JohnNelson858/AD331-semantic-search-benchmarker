"""Download pinned model assets without requiring a Hugging Face account."""
import os
from pathlib import Path
from urllib.request import urlopen
from shutil import copyfileobj

MODEL_ID = "jinaai/jina-embeddings-v2-small-en"
REVISION = "523cadcb9c2e71c7153fc46016e1fe79acb4f58f"
FILES = ("config.json", "tokenizer.json", "tokenizer_config.json", "special_tokens_map.json", "onnx/model.onnx")

def prepare() -> Path:
    root = Path(os.getenv("MODEL_DIR", ".cache/models/jina-small")).resolve()
    for name in FILES:
        target = root / name
        if target.is_file():
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        url = f"https://huggingface.co/Xenova/jina-embeddings-v2-small-en/resolve/{REVISION}/{name}"
        part = target.with_suffix(".part")
        try:
            with urlopen(url, timeout=90) as response, part.open("wb") as out:
                copyfileobj(response, out)
            part.replace(target)
        finally:
            part.unlink(missing_ok=True)
    return root

if __name__ == "__main__":
    print(prepare())
