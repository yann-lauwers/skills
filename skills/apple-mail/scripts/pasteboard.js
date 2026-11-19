// Pasteboard flavours for mail-draft.sh, via NSPasteboard.
//
//   save <dir>          writes <dir>/pb.html and <dir>/pb.txt from the current pasteboard
//   load <html> <text>  puts an HTML flavour plus a plain-text fallback on the pasteboard
//   load-files <path>…  puts those files on the pasteboard, as Finder's Copy does
//   restore <dir>       puts back what `save` captured
//
// The pasteboard is machine-wide, so a concurrent copy can land between `load` and
// the paste. mail-draft.sh reads the composed body back and re-asserts on a mismatch;
// nothing here can prevent the race, only make it detectable.
ObjC.import('AppKit')

const HTML = $.NSPasteboardTypeHTML
const TEXT = $.NSPasteboardTypeString

function readFile(p) {
  const s = $.NSString.stringWithContentsOfFileEncodingError(p, $.NSUTF8StringEncoding, null)
  return !s || s.isNil() ? null : s
}

function writeFile(p, nsstring) {
  const s = nsstring && !nsstring.isNil() ? nsstring : $.NSString.alloc.initWithUTF8String('')
  s.writeToFileAtomicallyEncodingError(p, true, $.NSUTF8StringEncoding, null)
}

function run(argv) {
  const pb = $.NSPasteboard.generalPasteboard
  const verb = argv[0]

  if (verb === 'save') {
    writeFile(argv[1] + '/pb.html', pb.stringForType(HTML))
    writeFile(argv[1] + '/pb.txt', pb.stringForType(TEXT))
    return 'saved'
  }

  if (verb === 'load') {
    const h = readFile(argv[1])
    const t = readFile(argv[2])
    if (!h || !t) throw new Error('cannot read the html or text file')
    pb.clearContents
    pb.setStringForType(h, HTML)
    pb.setStringForType(t, TEXT)
    return 'loaded'
  }

  if (verb === 'load-files') {
    const paths = argv.slice(1)
    if (paths.length === 0) throw new Error('load-files needs at least one path')
    const urls = $.NSMutableArray.alloc.init
    paths.forEach((path) => urls.addObject($.NSURL.fileURLWithPath(path)))
    pb.clearContents
    if (!pb.writeObjects(urls)) throw new Error('the pasteboard refused the files')
    return 'loaded'
  }

  if (verb === 'restore') {
    const h = readFile(argv[1] + '/pb.html')
    const t = readFile(argv[1] + '/pb.txt')
    pb.clearContents
    if (h && h.length > 0) pb.setStringForType(h, HTML)
    if (t && t.length > 0) pb.setStringForType(t, TEXT)
    return 'restored'
  }

  throw new Error('usage: pasteboard.js save <dir> | load <html> <text> | load-files <path>… | restore <dir>')
}
