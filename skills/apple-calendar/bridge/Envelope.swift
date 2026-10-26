import CoreGraphics
import EventKit
import Foundation

enum Failure: Int32 {
    case usage = 2
    case access = 3
    case notFound = 4
    case rejected = 5
}

/// Set from `--out` once the arguments are parsed. When the bridge runs under
/// LaunchServices its stdout goes nowhere, so every result travels through a file
/// as a `{ok, code, error, data}` envelope that the wrapper unwraps.
var envelopePath: String?

func writeEnvelope(ok: Bool, code: Int32, error: String?, data: Data?) {
    guard let path = envelopePath else { return }
    var body = Data("{\"ok\":\(ok),\"code\":\(code)".utf8)
    if let error {
        let escaped = String(decoding: (try? JSONEncoder().encode(error)) ?? Data("\"\"".utf8), as: UTF8.self)
        body.append(Data(",\"error\":\(escaped)".utf8))
    }
    if let data {
        body.append(Data(",\"data\":".utf8))
        body.append(data)
    }
    body.append(Data("}".utf8))
    try? body.write(to: URL(fileURLWithPath: path), options: .atomic)
}

func die(_ code: Failure, _ message: String) -> Never {
    if envelopePath != nil {
        writeEnvelope(ok: false, code: code.rawValue, error: message, data: nil)
    } else {
        FileHandle.standardError.write(("calendar-bridge: " + message + "\n").data(using: .utf8)!)
    }
    exit(code.rawValue)
}

// MARK: - Arguments
