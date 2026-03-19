"""
重建 Iansui-Regular.ttf subset。

每次新增遊戲文字後，執行：
    python tools/rebuild_font_subset.py

會自動掃描所有 .py 原始碼，收集漢字與特殊符號，
加上完整 ASCII 可列印字元，產生精簡字型並覆寫
Iansui-Regular.ttf。
"""

import os
import sys
import re
import subprocess
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SCAN_DIRS = [
    'constants.py',
    'main.py',
    'game',
    'core',
    'gui',
    'players',
]

# ── 額外手動補充（掃描不到但實際會顯示的字） ──────────────────────────
EXTRA_CHARS = ''
# ─────────────────────────────────────────────────────────────────────────


def collect_chars() -> set[int]:
    codepoints: set[int] = set()

    # ASCII 可列印字元 U+0020–U+007E
    codepoints.update(range(0x20, 0x7F))

    # 掃描 .py 原始碼
    pattern = re.compile(r'[\u4e00-\u9fff\uf900-\ufaff\u2192\u00b7\u2014\u300c\u300d]')
    for entry in SCAN_DIRS:
        path = os.path.join(ROOT, entry)
        if os.path.isfile(path):
            files = [path]
        else:
            files = []
            for dirpath, _, fnames in os.walk(path):
                for fn in fnames:
                    if fn.endswith('.py'):
                        files.append(os.path.join(dirpath, fn))
        for fpath in files:
            with open(fpath, encoding='utf-8', errors='ignore') as f:
                for ch in pattern.findall(f.read()):
                    codepoints.add(ord(ch))

    # 手動補充
    for ch in EXTRA_CHARS:
        codepoints.add(ord(ch))

    return codepoints


def main():
    font_path = os.path.join(ROOT, 'Iansui-Regular.ttf')
    if not os.path.exists(font_path):
        print(f'找不到字型檔：{font_path}')
        sys.exit(1)

    codepoints = collect_chars()
    unicodes_str = ','.join(f'U+{cp:04X}' for cp in sorted(codepoints))

    with tempfile.NamedTemporaryFile('w', suffix='.txt', delete=False, encoding='utf-8') as f:
        f.write(unicodes_str)
        tmp_path = f.name

    out_path = font_path.replace('.ttf', '_subset.ttf')
    try:
        subprocess.run(
            [
                sys.executable, '-m', 'fontTools.subset',
                font_path,
                f'--output-file={out_path}',
                f'--unicodes-file={tmp_path}',
                '--no-hinting',
                '--desubroutinize',
            ],
            check=True,
        )
        os.replace(out_path, font_path)
        size_kb = os.path.getsize(font_path) // 1024
        print(f'完成：{font_path}  ({size_kb} KB，{len(codepoints)} 個字元)')
    finally:
        os.unlink(tmp_path)
        if os.path.exists(out_path):
            os.unlink(out_path)


if __name__ == '__main__':
    main()
