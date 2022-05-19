import os
import re
import shutil

from collections import namedtuple
from sys import argv
from typing import List, Union


DATA_PATH = argv[1]
if DATA_PATH[-1] != "/":
    DATA_PATH += "/"

OUT_PATH = "humanized"

Block = namedtuple("Block", ["tag", "content"])


def parse(text: str) -> List[Union[Block, str]]:

    text = re.sub("<<", "«", text)
    text = re.sub(">>", "»", text)
    text = re.sub(r"\s+|\n", " ", text)
    s = re.sub(r"(</?\w+>)", r"[CUT]\1[CUT]", text)
    cut = list(filter(lambda t: len(t) > 0, map(str.strip, s.split("[CUT]"))))

    open_tag_pat = re.compile(r"<\w+>")

    cur_errors = []

    def parse_list(l: List[str]) -> List[Union[Block, str]]:
        it = iter(l)
        out = []
        while True:
            try:
                el = next(it)
            except StopIteration:
                break

            if re.match(open_tag_pat, el):
                tag = el[1:-1]
                next_it = []
                while not re.match(f"<\W{tag}>", el):
                    try:
                        el = next(it)
                    except StopIteration:
                        # raise SyntaxError(f"<{tag}> was not closed: {out[-1]}; {' '.join(next_it)}")
                        cur_errors.append(f"<{tag}> was not closed: {out[-1] if len(out) > 0 else ''}; {' '.join(next_it)}")
                        break
                    else:
                        next_it.append(el)
                if len(next_it) > 0:
                    out.append(Block(tag, parse_list(next_it[:-1])))
            else:
                out.append(el)

        for e in out:
            if isinstance(e, str) and re.match(r"</?.+>", e):
                i = out.index(e)
                cur_errors.append(f"Found tag in processed data: {e}; {out[max(i - 2, 0):i + 1]}")
        return out

    return parse_list(cut), cur_errors


cur_name = ""
def humanize(s: List[Union[Block, str]]) -> str:
    sentences = []

    global cur_name

    for el in s:
        if isinstance(el, str):
            sentences.append(el.strip())
        else:
            if el.tag == "header":
                continue
            elif el.tag == "footer":
                continue
            elif el.tag == "remark":
                sentences += ["\n" + "Ремарка --", humanize(el.content)]
            elif el.tag == "author":
                sentences += ["\n" + "Слова автора --", humanize(el.content)]
            elif el.tag == "title":
                sentences += ["\n\n" + "Заголовок --", humanize(el.content), "\n"]
            elif el.tag == "place":
                sentences += ["\n" + "Место действия --", humanize(el.content).strip(".") + "."]
            elif el.tag == "time":
                sentences += ["\n" + "Время действия --", humanize(el.content).strip(".").lower() + "."]
            elif el.tag == "chars":
                sentences += ["\n" + "Действующие лица --", humanize(el.content).strip(".") + "."]
            elif el.tag == "name":
                cur_name = humanize(el.content).strip().capitalize()
            elif el.tag == "line":
                sentences += ["\n" + cur_name, "говорит:", "«" + humanize(el.content).strip(".") + "»"]
            elif el.tag == "how":
                sentences.append(humanize(el.content).lower())

    sentences = filter(lambda t: not re.match(r"^\W*$", t) or t == "\n", sentences)
    sentences = " ".join(sentences)
    if sentences[0] == "\n":
        sentences = sentences[1:]
    return sentences


if __name__ == "__main__":
    paths = []
    for root, _, files in os.walk(DATA_PATH):
        for file in files:
            paths.append(os.path.join(root, file))

    parsed = []
    errors = []
    for path in paths:
        with open(path) as file:
            try:
                content = file.read()
            except Exception as e:
                print(e, path)
                raise

        try:
            t, e = parse(content)
            if len(e) > 0:
                raise SyntaxError("\n\n\n".join(e))
            parsed.append((path, t))
        except SyntaxError as e:
            errors.append((path, e))
            continue

    print(f"Errors occured in {len(errors)} files")
    print(f"Successfully parsed {len(parsed)} files")

    if os.path.isdir(os.path.join("errors", "data")):
        for f in os.listdir(os.path.join("errors", "data")):
            os.remove(os.path.join(os.path.join("errors", "data"), f))
    for p, e in errors:
        os.makedirs(os.path.join("errors", "data"), exist_ok=True)
        path = os.path.join("errors", "data", os.path.split(p)[-1])
        with open(path + ".log", "w") as f:
            f.write(str(e))

        os.system(f"cp '{p}' '{path}'")
        # break

    if os.path.isdir(OUT_PATH):
        for f in os.listdir(OUT_PATH):
            os.remove(os.path.join(OUT_PATH, f))
    os.makedirs(OUT_PATH, exist_ok=True)

    for i, (path, script) in enumerate(parsed):
        text = humanize(script)

        new_path = os.path.join(OUT_PATH, re.sub(DATA_PATH, "", path))
        os.makedirs(os.path.split(new_path)[0], exist_ok=True)
        with open(new_path, "w") as f:
            f.write(text)

    if os.path.isdir("invalid_files"):
        for f in os.listdir("invalid_files"):
            os.remove(os.path.join("invalid_files", f))
    for path, _ in errors:
        os.makedirs("invalid_files", exist_ok=True)
        shutil.copy(path, "invalid_files")
