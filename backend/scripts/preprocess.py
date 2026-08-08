"""CLI tool for text preprocessing — compress files, chat messages, or stdin.

Usage:
  python scripts/preprocess.py file <path> [--level lite|full|ultra] [--output <path>]
  python scripts/preprocess.py text <text> [--level lite|full|ultra]
  python scripts/preprocess.py stats <path> [--level lite|full|ultra]
  python scripts/preprocess.py stdinput [--level lite|full|ultra]   (reads from pipe)
"""

import os
import sys
import json
import importlib.util

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

_tp_path = os.path.join(os.path.dirname(__file__), '..', 'app', 'services', 'text_preprocessor.py')
_tp_spec = importlib.util.spec_from_file_location('text_preprocessor', _tp_path)
_tp_mod = importlib.util.module_from_spec(_tp_spec)
_tp_spec.loader.exec_module(_tp_mod)

preprocess_text = _tp_mod.preprocess_text
preprocess_for_upload = _tp_mod.preprocess_for_upload
preprocess_for_chat = _tp_mod.preprocess_for_chat
get_compression_stats = _tp_mod.get_compression_stats


def cmd_file(args):
    path = args[0]
    level = args[1] if len(args) > 1 else 'full'
    output = args[2] if len(args) > 2 else None

    with open(path, 'rb') as f:
        content = f.read()

    result = preprocess_for_upload(content, os.path.basename(path), level)
    if not result['text']:
        print(f'Format {result["format"]} — not processed (use txt/md)', file=sys.stderr)
        return 1

    if output:
        with open(output, 'w', encoding='utf-8') as f:
            f.write(result['text'])
        print(f'Written {len(result["text"])} chars to {output}')
    else:
        print(result['text'])

    sign = '' if result.get('savings_pct', 0) >= 0 else '-'
    print(f'({path}: {result["original_chars"]} → {result["processed_chars"]} chars, '
          f'{sign}{result.get("savings_pct", 0)}%)', file=sys.stderr)
    return 0


def cmd_text(args):
    text = args[0]
    level = args[1] if len(args) > 1 else 'full'
    result = preprocess_for_chat(text, level)
    print(result['message'])
    sign = '' if result.get('savings_pct', 0) >= 0 else '-'
    print(f'({sign}{result["savings_pct"]}%)', file=sys.stderr)
    return 0


def cmd_stats(args):
    path = args[0]
    level = args[1] if len(args) > 1 else 'full'

    with open(path, 'rb') as f:
        content = f.read()

    filename = os.path.basename(path)
    result = preprocess_for_upload(content, filename, level)
    original = content.decode('utf-8', errors='replace')

    stats = get_compression_stats(original, result['text'] if result['text'] else original)
    print(json.dumps({
        'file': filename,
        'original_bytes': len(content),
        'original_chars': stats['original_chars'],
        'processed_chars': stats['processed_chars'],
        'savings_pct': stats['savings_pct'],
        'compression_level': level,
    }, indent=2))
    return 0


def cmd_stdinput(args):
    level = args[0] if args else 'full'
    text = sys.stdin.read()
    if not text.strip():
        print('No input', file=sys.stderr)
        return 1

    result = preprocess_for_chat(text, level)
    print(result['message'])
    sign = '' if result.get('savings_pct', 0) >= 0 else '-'
    print(f'({sign}{result["savings_pct"]}%)', file=sys.stderr)
    return 0


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 1

    command = sys.argv[1]
    args = sys.argv[2:]

    cmds = {
        'file': cmd_file,
        'text': cmd_text,
        'stats': cmd_stats,
        'stdinput': cmd_stdinput,
    }

    handler = cmds.get(command)
    if not handler:
        print(f'Unknown command: {command}', file=sys.stderr)
        print(__doc__)
        return 1

    return handler(args)


if __name__ == '__main__':
    sys.exit(main())
