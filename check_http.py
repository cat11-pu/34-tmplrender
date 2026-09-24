"""check_http.py：起服务、按脚本走一圈，打印验收面。"""
import json
import sys
import threading
import urllib.error
import urllib.request

from server import serve


def call(method, url, body=None):
    request = urllib.request.Request(url, data=body, method=method, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            return response.status, response.read().decode()
    except urllib.error.HTTPError as error:
        return error.code, error.read().decode()


def parse(text):
    try:
        return json.loads(text)
    except Exception:
        return {"_raw": (text or "")[:60]}


def main() -> int:
    spec = json.load(open(sys.argv[1] if len(sys.argv) > 1 else "sample/templates.json", encoding="utf-8"))
    server = serve(0)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    base = "http://127.0.0.1:%d" % server.server_port
    body = json.dumps({"template": spec["template"], "context": spec["context"],
                       "partials": spec["partials"], "name": spec["name"]}).encode()
    first = parse(call("POST", base + "/render", body)[1])
    second = parse(call("POST", base + "/render", body)[1])
    checks = [parse(call("POST", base + "/check", json.dumps({"template": item}).encode())[1])
              for item in spec["bad"]]
    stats = parse(call("GET", base + "/stats")[1])
    recovered = parse(call("POST", base + "/recover", b"{}")[1])
    print("渲染输出 =", first.get("html"))
    print("第二次渲染输出一致 =", first.get("html") == second.get("html"))
    print("未定义变量次数 =", stats.get("undefined"))
    print("非法模板的错误行号 =", [item.get("line") for item in checks])
    print("编译缓存命中数 =", stats.get("cache_hits"))
    print("缓存条目数 =", stats.get("cached"))
    print("恢复后的缓存条目数 =", recovered.get("cached"))
    print("递归深度上限 =", stats.get("max_depth"))
    print("不变量（转义后不出现裸标签） =", spec["escape_invariant"])
    print("模板长度 =", len(spec["template"]))
    server.shutdown()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
