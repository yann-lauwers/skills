#!/usr/bin/env node
import { execFileSync } from 'node:child_process';
import { readFileSync, writeFileSync } from 'node:fs';
import { createRequire } from 'node:module';
import { join, resolve } from 'node:path';

const usage = `inventory.mjs <repo> [--under <path>] [--json <file>]

Lists every comment in the files git tracks under <repo>, one per line:
  <path>:<line>\\t<whole lines it fills>\\t<its first 200 characters>
then a count per file type and the total of whole lines, which is what deleting them all sheds.

Reads TypeScript and JavaScript with the repo's own typescript package (install the repo's
packages first), Python with python3, and CSS, HTML, YAML, TOML, shell, Swift, Rust, C, Go, Java
and Kotlin with its own readers. A line a tool reads is listed like any other: the verdict is the
reader's. Skips node_modules, lockfiles and any fixtures folder.`;

const args = process.argv.slice(2);
if (args.length === 0 || args.includes('--help')) {
  process.stdout.write(`${usage}\n`);
  process.exit(args.length === 0 ? 2 : 0);
}
const flag = (name) => (args.includes(name) ? args[args.indexOf(name) + 1] : undefined);
const root = resolve(args[0]);
const under = flag('--under');
const jsonFile = flag('--json');

const listed = (paths) =>
  execFileSync('git', ['-C', root, 'ls-files', '-z', ...paths], { maxBuffer: 1 << 30 })
    .toString()
    .split('\0')
    .filter(Boolean);
const tracked = listed(under ? ['--', under] : []).filter(
  (path) => !/(^|\/)(fixtures|node_modules)\//.test(path) && !/(^|\/)([^/]*\.lock|[^/]*-lock\.(json|yaml))$/.test(path),
);

let typescript;
function loadTypescript() {
  if (typescript === undefined) {
    const manifests = ['package.json', ...listed(['--', '*/package.json'])];
    for (const manifest of manifests) {
      try {
        const candidate = createRequire(join(root, manifest))('typescript');
        if (candidate?.ScriptKind !== undefined) {
          typescript = candidate;
          break;
        }
      } catch {
        continue;
      }
    }
    if (typescript === undefined) {
      process.stderr.write(`no typescript package resolves from ${root}: install the repo's packages first\n`);
      process.exit(2);
    }
  }
  return typescript;
}

function scriptComments(path, text) {
  const ts = loadTypescript();
  const kind = /\.[jt]sx$/.test(path) ? ts.ScriptKind.TSX : ts.ScriptKind.TS;
  const source = ts.createSourceFile(path, text, ts.ScriptTarget.Latest, false, kind);
  const seen = new Set();
  const ranges = [];
  const add = (found) => {
    for (const range of found ?? []) {
      if (!seen.has(range.pos)) {
        seen.add(range.pos);
        ranges.push([range.pos, range.end]);
      }
    }
  };
  const walk = (node) => {
    if (node.kind !== ts.SyntaxKind.JsxText) {
      add(ts.getLeadingCommentRanges(text, node.getFullStart()));
      add(ts.getTrailingCommentRanges(text, node.getEnd()));
    }
    for (const child of node.getChildren(source)) walk(child);
  };
  walk(source);
  return ranges;
}

function slashComments(text, { rust = false } = {}) {
  const ranges = [];
  const end = text.length;
  let at = 0;
  while (at < end) {
    if (text.startsWith('//', at)) {
      const stop = text.indexOf('\n', at);
      ranges.push([at, stop < 0 ? end : stop]);
      at = stop < 0 ? end : stop;
    } else if (text.startsWith('/*', at)) {
      let depth = 1;
      let cursor = at + 2;
      while (cursor < end && depth > 0) {
        if (text.startsWith('/*', cursor)) {
          depth += 1;
          cursor += 2;
        } else if (text.startsWith('*/', cursor)) {
          depth -= 1;
          cursor += 2;
        } else cursor += 1;
      }
      ranges.push([at, cursor]);
      at = cursor;
    } else if (text.startsWith('"""', at)) {
      const stop = text.indexOf('"""', at + 3);
      at = stop < 0 ? end : stop + 3;
    } else if (rust && /^r#*"/.test(text.slice(at, at + 8))) {
      const hashes = text.slice(at).match(/^r(#*)"/)[1];
      const stop = text.indexOf(`"${hashes}`, at + 2 + hashes.length);
      at = stop < 0 ? end : stop + 1 + hashes.length;
    } else if (text[at] === '"') {
      at += 1;
      while (at < end && text[at] !== '"' && text[at] !== '\n') at += text[at] === '\\' ? 2 : 1;
      at += 1;
    } else if (rust && text[at] === "'") {
      const character = text.slice(at, at + 12).match(/^'(\\.[^']*|[^'\\])'/);
      at += character ? character[0].length : 1;
    } else at += 1;
  }
  return ranges;
}

function hashComments(text, { afterCode = true } = {}) {
  const ranges = [];
  let start = 0;
  text.split('\n').forEach((line, row) => {
    const whole = line.match(/^(\s*)#/);
    const trailing = afterCode ? line.match(/^(?:\$\{?#|[^'"#]|"[^"]*"|'[^']*')*?\s(#(?:\s.*)?)$/) : null;
    if (whole && !(row === 0 && line.startsWith('#!'))) ranges.push([start + whole[1].length, start + line.length]);
    else if (trailing) ranges.push([start + line.length - trailing[1].length, start + line.length]);
    start += line.length + 1;
  });
  return ranges;
}

const matches = (pattern) => (text) => [...text.matchAll(pattern)].map((found) => [found.index, found.index + found[0].length]);

const pythonReader = `
import ast, io, json, sys, tokenize
out = {}
for path in sys.argv[2:]:
    try:
        text = open(sys.argv[1] + "/" + path, encoding="utf-8").read()
        rows = [[t.start[0], t.end[0], t.string] for t in tokenize.generate_tokens(io.StringIO(text).readline)
                if t.type == tokenize.COMMENT and not (t.start[0] == 1 and t.string.startswith("#!"))]
        tree = ast.parse(text)
        for owner in [tree] + [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))]:
            first = owner.body[0] if owner.body else None
            if isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant) and isinstance(first.value.value, str):
                rows.append([first.lineno, first.end_lineno, first.value.value])
        out[path] = rows
    except (SyntaxError, UnicodeDecodeError, tokenize.TokenError):
        out[path] = []
print(json.dumps(out))
`;

const readers = [
  [/\.(ts|tsx|mts|cts|js|jsx|mjs|cjs)$/, scriptComments],
  [/\.(css|scss)$/, (_path, text) => matches(/\/\*[\s\S]*?\*\//g)(text)],
  [/\.(html|vue|svelte)$/, (_path, text) => matches(/<!--[\s\S]*?-->/g)(text)],
  [/\.rs$/, (_path, text) => slashComments(text, { rust: true })],
  [/\.(swift|c|h|go|java|kt)$/, (_path, text) => slashComments(text)],
  [/\.(ya?ml|toml|sh|bash|zsh|rb|ps1)$/, (_path, text) => hashComments(text)],
  [/(^|\/)\.(gitignore|gitattributes|prettierignore|dockerignore)$/, (_path, text) => hashComments(text, { afterCode: false })],
  [/\.(cmd|bat)$/, (_path, text) => matches(/^[ \t]*(?:@?rem\b|::).*$/gim)(text)],
];

const found = [];
const read = (path) => {
  try {
    return readFileSync(join(root, path), 'utf8');
  } catch {
    return undefined;
  }
};

for (const path of tracked) {
  const text = read(path);
  if (text === undefined) continue;
  const reader =
    readers.find(([pattern]) => pattern.test(path))?.[1] ??
    (!/\.[^/]*$/.test(path) && /^#!.*\b(sh|bash|zsh)\b/.test(text.split('\n', 1)[0])
      ? (_path, body) => hashComments(body)
      : undefined);
  if (reader === undefined) continue;
  const lineStarts = [0];
  for (let index = 0; index < text.length; index += 1) if (text[index] === '\n') lineStarts.push(index + 1);
  const lineOf = (offset) => {
    let low = 0;
    let high = lineStarts.length - 1;
    while (low < high) {
      const middle = (low + high + 1) >> 1;
      if (lineStarts[middle] <= offset) low = middle;
      else high = middle - 1;
    }
    return low;
  };
  for (const [from, to] of reader(path, text).sort((first, second) => first[0] - second[0])) {
    const firstLine = lineOf(from);
    const lastLine = lineOf(Math.max(from, to - 1));
    let wholeLines = 0;
    for (let line = firstLine; line <= lastLine; line += 1) {
      const lineStart = lineStarts[line];
      const lineEnd = (lineStarts[line + 1] ?? text.length + 1) - 1;
      const before = text.slice(lineStart, Math.max(lineStart, from)).trim();
      const after = text.slice(Math.min(lineEnd, to), lineEnd).trim();
      if ((line > firstLine || before === '') && (line < lastLine || after === '')) wholeLines += 1;
    }
    found.push({ path, line: firstLine + 1, wholeLines, text: text.slice(from, to) });
  }
}

const pythonFiles = tracked.filter((path) => path.endsWith('.py'));
for (let index = 0; index < pythonFiles.length; index += 200) {
  const batch = pythonFiles.slice(index, index + 200);
  const rows = JSON.parse(execFileSync('python3', ['-I', '-c', pythonReader, root, ...batch], { maxBuffer: 1 << 30 }));
  for (const [path, comments] of Object.entries(rows)) {
    for (const [line, endLine, text] of comments) {
      const source = (read(path) ?? '').split('\n');
      const alone = text.startsWith('#') ? source[line - 1].trim().startsWith('#') : true;
      found.push({ path, line, wholeLines: alone ? endLine - line + 1 : 0, text });
    }
  }
}

found.sort((first, second) => first.path.localeCompare(second.path) || first.line - second.line);
for (const { path, line, wholeLines, text } of found) {
  process.stdout.write(`${path}:${line}\t${wholeLines}\t${text.replace(/\s+/g, ' ').slice(0, 200)}\n`);
}
const perType = new Map();
for (const { path, wholeLines } of found) {
  const type = path.match(/\.([^./]+)$/)?.[1] ?? path.split('/').pop();
  const tally = perType.get(type) ?? { comments: 0, wholeLines: 0 };
  perType.set(type, { comments: tally.comments + 1, wholeLines: tally.wholeLines + wholeLines });
}
for (const [type, tally] of perType) {
  process.stdout.write(`# ${type}: ${tally.comments} comments, ${tally.wholeLines} whole lines\n`);
}
const total = found.reduce((sum, { wholeLines }) => sum + wholeLines, 0);
process.stdout.write(`# total: ${found.length} comments, ${total} whole lines\n`);
if (jsonFile) writeFileSync(jsonFile, JSON.stringify(found));
