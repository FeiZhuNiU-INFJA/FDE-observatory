#!/usr/bin/env python3
"""
本地静态预览服务器。

修复 python3 -m http.server 默认行为：
  - .md 被当成 application/octet-stream 触发下载
  - 中文 .md / .txt 没有 charset=utf-8 导致浏览器乱码

用法：
    python3 serve.py            # 默认 8080
    python3 serve.py 9000       # 指定端口
"""
import json
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

# 让 _assets/build_manifest.py 可被 import
sys.path.insert(0, str(Path(__file__).resolve().parent / "_assets"))
import build_manifest  # noqa: E402


class UTF8Handler(SimpleHTTPRequestHandler):
    extensions_map = {
        **SimpleHTTPRequestHandler.extensions_map,
        ".md": "text/plain; charset=utf-8",
        ".markdown": "text/plain; charset=utf-8",
        ".txt": "text/plain; charset=utf-8",
        ".log": "text/plain; charset=utf-8",
        ".html": "text/html; charset=utf-8",
        ".htm": "text/html; charset=utf-8",
        ".css": "text/css; charset=utf-8",
        ".js": "application/javascript; charset=utf-8",
        ".json": "application/json; charset=utf-8",
        ".svg": "image/svg+xml; charset=utf-8",
    }

    def do_GET(self) -> None:  # noqa: N802
        # 动态 manifest 端点：每次请求都实时扫描文件系统
        if self.path.split("?", 1)[0] in ("/_manifest.json", "/_assets/manifest.json"):
            try:
                data = build_manifest.scan()
                payload = json.dumps(data, ensure_ascii=False).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(payload)))
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                self.wfile.write(payload)
                return
            except Exception as exc:  # pragma: no cover
                self.send_error(500, f"manifest build failed: {exc}")
                return
        super().do_GET()

    def end_headers(self) -> None:  # noqa: D401
        # 本地预览环境：永远不缓存，避免改 CSS/JS 后浏览器拿旧版
        self.send_header("Cache-Control", "no-store, must-revalidate")
        self.send_header("Pragma", "no-cache")
        super().end_headers()


def main() -> None:
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    # 启动时构建一次静态 manifest（用于 file:// 或不走 /_manifest.json 的场景）
    try:
        data = build_manifest.scan()
        out = Path(__file__).resolve().parent / "_assets" / "manifest.json"
        out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        total = sum(len(data[k]) for k in data if isinstance(data[k], list))
        print(f"✓ 初始 manifest 构建完成：{total} 篇文档")
    except Exception as exc:
        print(f"⚠ 初始 manifest 构建失败：{exc}")

    with ThreadingHTTPServer(("", port), UTF8Handler) as httpd:
        print(f"FDE 洞察站本地预览：http://localhost:{port}/")
        print(f"  · 动态 manifest 端点：http://localhost:{port}/_manifest.json")
        print("按 Ctrl+C 退出")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n已停止")


if __name__ == "__main__":
    main()
