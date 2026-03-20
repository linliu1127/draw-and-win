"""Build 後補丁：將 touch-action / user-select 注入 index.html。"""
import sys
from pathlib import Path

OLD = "            right: 0;\n        }"
NEW = "            right: 0;\n            touch-action: none;\n            user-select: none;\n        }"

def patch(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    if "touch-action" in text:
        print(f"[skip] {path} 已有 touch-action")
        return
    if OLD not in text:
        print(f"[error] {path} 找不到目標字串", file=sys.stderr)
        sys.exit(1)
    path.write_text(text.replace(OLD, NEW, 1), encoding="utf-8")
    print(f"[ok] {path}")

if __name__ == "__main__":
    base = Path(__file__).parent.parent
    patch(base / "build/web/index.html")
