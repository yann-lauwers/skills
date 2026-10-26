import CoreGraphics
import EventKit
import Foundation

struct Args {
    let verb: String
    private var flags: [String: [String]] = [:]
    private(set) var positionals: [String] = []

    init(_ argv: [String]) {
        guard argv.count > 1 else { die(.usage, "no verb given; try `help`") }
        verb = argv[1]
        var i = 2
        while i < argv.count {
            let a = argv[i]
            if a.hasPrefix("--") {
                let name = String(a.dropFirst(2))
                if let eq = name.firstIndex(of: "=") {
                    flags[String(name[name.startIndex..<eq]), default: []]
                        .append(String(name[name.index(after: eq)...]))
                } else if i + 1 < argv.count && !argv[i + 1].hasPrefix("--") {
                    flags[name, default: []].append(argv[i + 1])
                    i += 1
                } else {
                    flags[name, default: []].append("true")
                }
            } else {
                positionals.append(a)
            }
            i += 1
        }
    }

    func has(_ name: String) -> Bool { flags[name] != nil }
    func str(_ name: String) -> String? { flags[name]?.last }
    func list(_ name: String) -> [String] { flags[name] ?? [] }
    func int(_ name: String) -> Int? { flags[name]?.last.flatMap { Int($0) } }
    func bool(_ name: String) -> Bool {
        guard let v = flags[name]?.last else { return false }
        return !["false", "no", "0"].contains(v.lowercased())
    }
    func require(_ name: String) -> String {
        guard let v = flags[name]?.last else { die(.usage, "--\(name) is required") }
        return v
    }
}

// MARK: - Dates

let calendarSystem = Calendar.current

let isoOut: ISO8601DateFormatter = {
    let f = ISO8601DateFormatter()
    f.formatOptions = [.withInternetDateTime]
    f.timeZone = TimeZone.current
    return f
}()

let utcCompact: DateFormatter = {
    let f = DateFormatter()
    f.dateFormat = "yyyyMMdd'T'HHmmss'Z'"
    f.timeZone = TimeZone(identifier: "UTC")
    f.locale = Locale(identifier: "en_US_POSIX")
    return f
}()

func fixedFormatter(_ pattern: String) -> DateFormatter {
    let f = DateFormatter()
    f.dateFormat = pattern
    f.locale = Locale(identifier: "en_US_POSIX")
    f.timeZone = TimeZone.current
    return f
}

/// Accepts `now`, `today`, `tomorrow`, `yesterday`, relative offsets (`+7d`,
/// `-2w`, `+90m`), `YYYY-MM-DD`, `YYYY-MM-DD HH:mm[:ss]`, and full ISO 8601.
/// `endOfDay` pushes a bare date to 23:59:59 so `--to 2026-09-30` includes that day.
func parseDate(_ raw: String, endOfDay: Bool = false) -> Date? {
    let s = raw.trimmingCharacters(in: .whitespaces)
    let lower = s.lowercased()

    func dayEdge(_ offsetDays: Int) -> Date? {
        guard let base = calendarSystem.date(byAdding: .day, value: offsetDays, to: Date()) else { return nil }
        let start = calendarSystem.startOfDay(for: base)
        return endOfDay ? calendarSystem.date(byAdding: DateComponents(day: 1, second: -1), to: start) : start
    }

    switch lower {
    case "now": return Date()
    case "today": return dayEdge(0)
    case "tomorrow": return dayEdge(1)
    case "yesterday": return dayEdge(-1)
    default: break
    }

    if let m = lower.range(of: "^[+-][0-9]+[mhdw]$", options: .regularExpression), m.lowerBound == lower.startIndex {
        let sign = lower.hasPrefix("-") ? -1 : 1
        let unit = lower.last!
        let n = Int(lower.dropFirst().dropLast()) ?? 0
        var comp = DateComponents()
        switch unit {
        case "m": comp.minute = sign * n
        case "h": comp.hour = sign * n
        case "d": comp.day = sign * n
        case "w": comp.day = sign * n * 7
        default: return nil
        }
        return calendarSystem.date(byAdding: comp, to: Date())
    }

    if s.count == 10, let d = fixedFormatter("yyyy-MM-dd").date(from: s) {
        return endOfDay ? calendarSystem.date(byAdding: DateComponents(day: 1, second: -1), to: d) : d
    }

    for pattern in ["yyyy-MM-dd'T'HH:mm:ssZZZZZ", "yyyy-MM-dd'T'HH:mm:ss", "yyyy-MM-dd'T'HH:mm",
                    "yyyy-MM-dd HH:mm:ss", "yyyy-MM-dd HH:mm"] {
        if let d = fixedFormatter(pattern).date(from: s) { return d }
    }

    let iso = ISO8601DateFormatter()
    iso.formatOptions = [.withInternetDateTime, .withFractionalSeconds]
    if let d = iso.date(from: s) { return d }
    iso.formatOptions = [.withInternetDateTime]
    return iso.date(from: s)
}

/// `90`, `90m`, `2h`, `1h30m` → seconds.
func parseDuration(_ raw: String) -> TimeInterval? {
    let s = raw.trimmingCharacters(in: .whitespaces).lowercased()
    if let plain = Double(s) { return plain * 60 }
    var total: Double = 0
    var seen = false
    var number = ""
    for ch in s {
        if ch.isNumber { number.append(ch); continue }
        guard let n = Double(number) else { return nil }
        switch ch {
        case "h": total += n * 3600
        case "m": total += n * 60
        case "d": total += n * 86400
        default: return nil
        }
        seen = true
        number = ""
    }
    if !number.isEmpty { return nil }
    return seen ? total : nil
}

/// `-15m` / `15m before` → a negative offset in seconds, EventKit's convention.
func parseAlarmOffset(_ raw: String) -> TimeInterval? {
    let s = raw.trimmingCharacters(in: .whitespaces).lowercased()
    if s == "0" || s == "start" { return 0 }
    let body = s.hasPrefix("-") ? String(s.dropFirst()) : s
    guard let seconds = parseDuration(body) else { return nil }
    return -seconds
}

// MARK: - Store access
