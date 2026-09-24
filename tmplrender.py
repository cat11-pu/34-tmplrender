"""tmplrender.py：模板渲染（基线：只做变量替换，不转义）。"""
from __future__ import annotations


class Renderer:
    def __init__(self, max_depth: int = 2):
        self.max_depth = max_depth
        self.cache = {}
        self.cache_hits = 0
        self.undefined = 0

    def render(self, template: str, context: dict, partials: dict = None, name: str = "inline") -> str:
        """基线：把 {{ name }} 换成值，别的一律原样输出。"""
        self.cache.setdefault(name, template)
        out = []
        index = 0
        while True:
            start = template.find("{{", index)
            if start < 0:
                out.append(template[index:])
                break
            end = template.find("}}", start)
            if end < 0:
                out.append(template[index:])
                break
            key = template[start + 2:end].strip()
            out.append(template[index:start])
            out.append(str(context.get(key, "")))
            index = end + 2
        return "".join(out)

    def check(self, template: str, name: str = "inline") -> dict:
        """基线：什么都不检查。"""
        return {"ok": True, "line": None}

    def persist(self) -> bytes:
        raise NotImplementedError("编译缓存落盘还没实现")

    def restore(self, blob: bytes = None) -> dict:
        raise NotImplementedError("编译缓存恢复还没实现")

    def stats(self) -> dict:
        return {"cached": len(self.cache), "cache_hits": self.cache_hits,
                "undefined": self.undefined, "max_depth": self.max_depth}
