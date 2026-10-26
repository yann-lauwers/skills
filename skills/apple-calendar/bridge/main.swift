// Calendar Bridge — EventKit over a JSON command line.
//
// Every verb prints JSON on stdout, diagnostics on stderr, and exits non-zero on
// failure. It runs inside CalendarBridge.app so that macOS attributes the
// Calendars TCC grant to a stable bundle identity rather than to whichever
// terminal happened to launch it.

import CoreGraphics
import EventKit
import Foundation

let args = Args(CommandLine.arguments)
envelopePath = args.str("out")
let pretty = args.bool("pretty")

let helpText = """
calendar-bridge <verb> [flags]

  calendars                          every calendar, with its id, source and whether it is writable
  events --from X --to Y             events in a window
        [--calendar NAME]... [--query TEXT] [--limit N] [--include-declined] [--include-all-day false]
  show <ref>                         one event in full
  free --from X --to Y               open slots
        [--duration 30m] [--between 09:00-18:00] [--weekdays] [--calendar NAME]...
  create --title T --start S         a new event; prints it back, read from the store
        [--end E | --duration 45m] [--calendar NAME] [--all-day] [--location L] [--notes N]
        [--url U] [--alarm -15m]... [--repeat weekly[/2]] [--until YYYY-MM-DD | --count N]
        [--availability busy|free] [--dry-run]
  update <ref>                       change an existing event; same field flags as create
        [--span this|future] [--dry-run]
  delete <ref> [--span this|future] [--dry-run]
  open <ref>                         reveal it in Calendar.app
  access                             what the Calendars permission currently allows

Dates accept: now, today, tomorrow, yesterday, +7d, -2w, +90m, YYYY-MM-DD,
"YYYY-MM-DD HH:mm", and full ISO 8601. A bare --to date covers that whole day.

A ref is what `events` prints: an identifier, optionally @occurrence for one
instance of a repeating event. Ids change when an event is edited — read one and
act on it in the same breath.

Adding invitees is not possible here; EventKit and Calendar's AppleScript
dictionary both expose attendees read-only. `open` the event and add them in
Calendar.app.
"""

switch args.verb {

case "help", "--help", "-h":
    if envelopePath != nil {
        struct HelpOut: Encodable { let help: String }
        emit(HelpOut(help: helpText), pretty: pretty)
    } else {
        print(helpText)
    }

case "access":
    let status = EKEventStore.authorizationStatus(for: .event)
    struct AccessOut: Encodable { let status: String; let canRead: Bool; let canWrite: Bool }
    let full: Bool
    if #available(macOS 14.0, *) { full = status == .fullAccess } else { full = status == .authorized }
    let writeOnly: Bool
    if #available(macOS 14.0, *) { writeOnly = status == .writeOnly } else { writeOnly = false }
    emit(AccessOut(status: describe(status), canRead: full, canWrite: full || writeOnly), pretty: pretty)

case "calendars":
    let store = openStore(write: false)
    let fallback = store.defaultCalendarForNewEvents?.calendarIdentifier
    let out = store.calendars(for: .event).map { c in
        CalendarOut(id: c.calendarIdentifier, title: c.title, source: c.source.title,
                    sourceType: sourceTypeName(c.source.sourceType), color: hex(c.cgColor),
                    editable: c.allowsContentModifications,
                    subscribed: c.isSubscribed,
                    isDefaultForNewEvents: c.calendarIdentifier == fallback)
    }
    emit(out, pretty: pretty)

case "events":
    let store = openStore(write: false)
    guard let from = parseDate(args.str("from") ?? "today") else { die(.usage, "could not read --from") }
    guard let to = parseDate(args.str("to") ?? "+7d", endOfDay: true) else { die(.usage, "could not read --to") }
    guard to > from else { die(.usage, "--to must be after --from") }

    let calendars = resolveCalendars(store, args.list("calendar"))
    var events = fetchEvents(store, from: from, to: to, calendars: calendars)

    if !args.bool("include-declined") {
        events = events.filter { e in
            !(e.attendees ?? []).contains { $0.isCurrentUser && $0.participantStatus == .declined }
                && e.status != .canceled
        }
    }
    if args.has("include-all-day") && !args.bool("include-all-day") {
        events = events.filter { !$0.isAllDay }
    }
    if let query = args.str("query")?.lowercased(), !query.isEmpty {
        events = events.filter { e in
            [e.title, e.location, e.notes].compactMap { $0 }.joined(separator: " ").lowercased().contains(query)
        }
    }
    if let limit = args.int("limit") { events = Array(events.prefix(limit)) }

    emit(events.map(eventOut), pretty: pretty)

case "show":
    let store = openStore(write: false)
    guard let ref = args.positionals.first ?? args.str("ref") else { die(.usage, "show needs an event ref") }
    emit(eventOut(resolveEvent(store, ref)), pretty: pretty)

case "free":
    let store = openStore(write: false)
    guard let from = parseDate(args.str("from") ?? "today") else { die(.usage, "could not read --from") }
    guard let to = parseDate(args.str("to") ?? "+7d", endOfDay: true) else { die(.usage, "could not read --to") }
    let minimum = parseDuration(args.str("duration") ?? "30m") ?? 1800

    var dayStartMinutes = 0
    var dayEndMinutes = 24 * 60
    if let between = args.str("between") {
        let halves = between.split(separator: "-").map(String.init)
        guard halves.count == 2 else { die(.usage, "--between takes HH:mm-HH:mm") }
        func minutes(_ s: String) -> Int? {
            let hm = s.split(separator: ":").compactMap { Int($0) }
            guard hm.count == 2 else { return nil }
            return hm[0] * 60 + hm[1]
        }
        guard let a = minutes(halves[0]), let b = minutes(halves[1]), b > a else {
            die(.usage, "--between takes HH:mm-HH:mm with the end after the start")
        }
        dayStartMinutes = a
        dayEndMinutes = b
    }
    let weekdaysOnly = args.bool("weekdays")

    let calendars = resolveCalendars(store, args.list("calendar"))
    let busy = fetchEvents(store, from: from, to: to, calendars: calendars)
        .filter { e in
            guard e.status != .canceled, e.availability != .free else { return false }
            if (e.attendees ?? []).contains(where: { $0.isCurrentUser && $0.participantStatus == .declined }) { return false }
            return true
        }
        .compactMap { e -> (Date, Date)? in
            guard let s = e.startDate, let t = e.endDate else { return nil }
            return (s, t)
        }
        .sorted { $0.0 < $1.0 }

    var slots: [SlotOut] = []
    var day = calendarSystem.startOfDay(for: from)
    while day < to {
        defer { day = calendarSystem.date(byAdding: .day, value: 1, to: day)! }
        if weekdaysOnly {
            let weekday = calendarSystem.component(.weekday, from: day)
            if weekday == 1 || weekday == 7 { continue }
        }
        guard var cursor = calendarSystem.date(byAdding: .minute, value: dayStartMinutes, to: day),
              let windowEnd = calendarSystem.date(byAdding: .minute, value: dayEndMinutes, to: day)
        else { continue }
        cursor = max(cursor, from)
        let limit = min(windowEnd, to)
        guard cursor < limit else { continue }

        for (busyStart, busyEnd) in busy where busyEnd > cursor && busyStart < limit {
            if busyStart > cursor && busyStart.timeIntervalSince(cursor) >= minimum {
                slots.append(SlotOut(start: isoOut.string(from: cursor), end: isoOut.string(from: busyStart),
                                     durationMinutes: Int(busyStart.timeIntervalSince(cursor) / 60)))
            }
            cursor = max(cursor, busyEnd)
            if cursor >= limit { break }
        }
        if cursor < limit && limit.timeIntervalSince(cursor) >= minimum {
            slots.append(SlotOut(start: isoOut.string(from: cursor), end: isoOut.string(from: limit),
                                 durationMinutes: Int(limit.timeIntervalSince(cursor) / 60)))
        }
    }
    emit(slots, pretty: pretty)

case "create":
    let store = openStore(write: true)
    let event = EKEvent(eventStore: store)

    let named = args.list("calendar")
    let target: EKCalendar
    if let resolved = resolveCalendars(store, named)?.first {
        target = resolved
    } else if let fallback = store.defaultCalendarForNewEvents {
        target = fallback
    } else {
        die(.rejected, "no --calendar given and this Mac has no default calendar for new events")
    }
    guard target.allowsContentModifications else {
        die(.rejected, "\"\(target.title)\" is read-only (\(sourceTypeName(target.source.sourceType))); name a writable calendar with --calendar")
    }
    event.calendar = target

    _ = args.require("title")
    _ = args.require("start")
    applyEventFields(event, args, store: store, isNew: true)
    guard event.startDate != nil, event.endDate != nil else { die(.usage, "an event needs a start and an end") }

    if args.bool("dry-run") {
        emit(eventOut(event), pretty: pretty)
        break
    }
    do {
        try store.save(event, span: .futureEvents, commit: true)
    } catch {
        die(.rejected, "Calendar refused the save: \(error.localizedDescription)")
    }
    // Read it back rather than printing what was sent.
    guard let identifier = event.eventIdentifier, let saved = store.event(withIdentifier: identifier) else {
        die(.rejected, "the event saved but could not be read back; open Calendar.app and check")
    }
    emit(eventOut(saved), pretty: pretty)

case "update":
    let store = openStore(write: true)
    guard let ref = args.positionals.first ?? args.str("ref") else { die(.usage, "update needs an event ref") }
    let event = resolveEvent(store, ref)
    guard event.calendar?.allowsContentModifications ?? false else {
        die(.rejected, "\"\(event.calendar?.title ?? "that calendar")\" is read-only")
    }

    if let moveTo = args.str("move-calendar") {
        guard let destination = resolveCalendars(store, [moveTo])?.first else { die(.notFound, "no calendar matches \"\(moveTo)\"") }
        guard destination.allowsContentModifications else { die(.rejected, "\"\(destination.title)\" is read-only") }
        event.calendar = destination
    }
    applyEventFields(event, args, store: store, isNew: false)

    if args.bool("dry-run") {
        emit(eventOut(event), pretty: pretty)
        break
    }
    do {
        try store.save(event, span: span(args), commit: true)
    } catch {
        die(.rejected, "Calendar refused the save: \(error.localizedDescription)")
    }
    guard let identifier = event.eventIdentifier, let saved = store.event(withIdentifier: identifier) else {
        die(.rejected, "the event saved but could not be read back; open Calendar.app and check")
    }
    emit(eventOut(saved), pretty: pretty)

case "delete":
    let store = openStore(write: true)
    guard let ref = args.positionals.first ?? args.str("ref") else { die(.usage, "delete needs an event ref") }
    let event = resolveEvent(store, ref)
    let snapshot = eventOut(event)

    if args.bool("dry-run") {
        emit(snapshot, pretty: pretty)
        break
    }
    do {
        try store.remove(event, span: span(args), commit: true)
    } catch {
        die(.rejected, "Calendar refused the delete: \(error.localizedDescription)")
    }
    struct DeletedOut: Encodable { let deleted: EventOut; let span: String; let stillPresent: Bool }
    let stillThere = store.event(withIdentifier: snapshot.id) != nil && span(args) == .thisEvent
    emit(DeletedOut(deleted: snapshot, span: args.str("span") ?? "this", stillPresent: stillThere), pretty: pretty)

case "open":
    let store = openStore(write: false)
    guard let ref = args.positionals.first ?? args.str("ref") else { die(.usage, "open needs an event ref") }
    let event = resolveEvent(store, ref)
    let target = openUrlFor(event)
    let task = Process()
    task.executableURL = URL(fileURLWithPath: "/usr/bin/open")
    task.arguments = [target]
    try? task.run()
    task.waitUntilExit()
    struct OpenedOut: Encodable { let opened: String; let title: String }
    emit(OpenedOut(opened: target, title: event.title ?? ""), pretty: pretty)

default:
    die(.usage, "unknown verb \"\(args.verb)\"\n\n" + helpText)
}
