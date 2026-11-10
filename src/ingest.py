"""Read UTF-8 Markdown or normalize HTML into heading/fence-aware text."""
from html.parser import HTMLParser
from pathlib import Path
import re

class MarkdownHTML(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts=[]
        self.code=None
        self.skip=0

    def handle_starttag(self, tag, attrs):
        if tag in {"script","style"}:
            self.skip+=1
        if self.skip or self.code is not None:
            return
        if re.fullmatch(r"h[1-6]",tag):
            self.parts.append("\n\n"+"#"*int(tag[1])+" ")
        elif tag=="pre":
            self.code=[]
        elif tag in {"p","div","section","article","br","tr"}:
            self.parts.append("\n")
        elif tag=="li":
            self.parts.append("\n- ")
        elif tag in {"td","th"}:
            self.parts.append(" | ")

    def handle_endtag(self,tag):
        if tag in {"script","style"}:
            self.skip=max(0,self.skip-1)
        if self.skip:
            return
        if tag=="pre" and self.code is not None:
            code="".join(self.code).strip("\n")
            fence="`"*max(3,1+max((len(x) for x in re.findall(r"`+",code)),default=0))
            self.parts.append(f"\n\n{fence}\n{code}\n{fence}\n\n")
            self.code=None
        elif self.code is None and re.fullmatch(r"h[1-6]",tag):
            self.parts.append("\n\n")

    def handle_data(self,data):
        if not self.skip:
            if self.code is not None:
                self.code.append(data)
            else:
                self.parts.append(re.sub(r"\s+"," ",data))

def read_document(path: Path) -> str:
    source=path.read_text(encoding="utf-8")
    if path.suffix.lower() in {".html",".htm"}:
        parser=MarkdownHTML()
        parser.feed(source)
        parser.close()
        if parser.code is not None:
            parser.handle_endtag("pre")
        return "".join(parser.parts).strip()+"\n"
    return source
