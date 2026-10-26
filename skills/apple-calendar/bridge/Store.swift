import CoreGraphics
import EventKit
import Foundation

func resolveCalendars(_ store: EKEventStore, _ names: [String]) -> [EKCalendar]? {
    guard !names.isEmpty else { return nil }
    let all = store.calendars(for: .event)
    var out: [EKCalendar] = []
    for name in names {
        let needle = name.lowercased()
        guard let match = all.first(where: { $0.calendarIdentifier == name })
            ?? all.first(where: { $0.title.lowercased() == needle })
            ?? all.first(where: { $0.title.lowercased().contains(needle) })
        else {
            die(.notFound, "no calendar matches \"\(name)\"; run `calendars` to see the list")
        }
        out.append(match)
    }
    return out
}

/// A ref is `identifier` or `identifier@occurrenceISO`. The occurrence half is what
/// separates one instance of a recurring event from the series.
func resolveEvent(_ store: EKEventStore, _ ref: String) -> EKEvent {
    let parts = ref.split(separator: "@", maxSplits: 1).map(String.init)
    let identifier = parts[0]
    guard let base = store.event(withIdentifier: identifier) else {
        die(.notFound, "no event with identifier \(identifier); ids move when an event is edited, so re-run `events` and use the ref it prints")
    }
    // The occurrence half only disambiguates a series. On a one-off the identifier
    // is already unique, and honouring a stamp read before the event was moved
    // would fail to find an event that is sitting right there.
    guard base.hasRecurrenceRules, parts.count == 2, let occurrence = parseDate(parts[1]) else { return base }

    let window = store.predicateForEvents(withStart: occurrence.addingTimeInterval(-86400),
                                          end: occurrence.addingTimeInterval(86400),
                                          calendars: base.calendar.map { [$0] })
    let match = store.events(matching: window).first {
        $0.eventIdentifier == identifier &&
        abs(($0.startDate ?? .distantPast).timeIntervalSince(occurrence)) < 60
    }
    guard let match else {
        die(.notFound, "event \(identifier) has no occurrence starting \(parts[1])")
    }
    return match
}

func span(_ args: Args) -> EKSpan {
    switch (args.str("span") ?? "this").lowercased() {
    case "this", "thisevent", "occurrence": return .thisEvent
    case "future", "series", "following": return .futureEvents
    default: die(.usage, "--span takes `this` or `future`")
    }
}

/// EventKit caps one predicate at a four-year window; longer ranges are chunked.
func fetchEvents(_ store: EKEventStore, from: Date, to: Date, calendars: [EKCalendar]?) -> [EKEvent] {
    var collected: [EKEvent] = []
    var cursor = from
    let chunk: TimeInterval = 365 * 24 * 3600 * 3
    while cursor < to {
        let slice = min(cursor.addingTimeInterval(chunk), to)
        let predicate = store.predicateForEvents(withStart: cursor, end: slice, calendars: calendars)
        collected.append(contentsOf: store.events(matching: predicate))
        cursor = slice
    }
    var seen = Set<String>()
    return collected
        .filter { seen.insert("\($0.eventIdentifier ?? "")|\($0.startDate?.timeIntervalSince1970 ?? 0)").inserted }
        .sorted { ($0.startDate ?? .distantPast) < ($1.startDate ?? .distantPast) }
}

// MARK: - Verbs

func applyEventFields(_ event: EKEvent, _ args: Args, store: EKEventStore, isNew: Bool) {
    if let title = args.str("title") { event.title = title }
    if args.has("all-day") { event.isAllDay = args.bool("all-day") }
    if let location = args.str("location") { event.location = location }
    if let notes = args.str("notes") { event.notes = notes }
    if let url = args.str("url") { event.url = URL(string: url) }

    if let startRaw = args.str("start") {
        guard let start = parseDate(startRaw) else { die(.usage, "could not read --start \"\(startRaw)\"") }
        event.startDate = start
    }
    if let endRaw = args.str("end") {
        guard let end = parseDate(endRaw) else { die(.usage, "could not read --end \"\(endRaw)\"") }
        event.endDate = end
    } else if let durationRaw = args.str("duration") {
        guard let seconds = parseDuration(durationRaw) else { die(.usage, "could not read --duration \"\(durationRaw)\"") }
        guard let start = event.startDate else { die(.usage, "--duration needs a start date") }
        event.endDate = start.addingTimeInterval(seconds)
    } else if isNew, let start = event.startDate {
        // An all-day event's end lands on its own last day, so a one-day event ends
        // where it starts. Adding a day here books two days.
        event.endDate = event.isAllDay ? start : start.addingTimeInterval(3600)
    }

    if let availability = args.str("availability") {
        switch availability.lowercased() {
        case "busy": event.availability = .busy
        case "free": event.availability = .free
        case "tentative": event.availability = .tentative
        case "unavailable": event.availability = .unavailable
        default: die(.usage, "--availability takes busy, free, tentative or unavailable")
        }
    }

    let alarmFlags = args.list("alarm")
    if !alarmFlags.isEmpty {
        event.alarms?.forEach { event.removeAlarm($0) }
        if alarmFlags != ["none"] {
            for raw in alarmFlags {
                guard let offset = parseAlarmOffset(raw) else { die(.usage, "could not read --alarm \"\(raw)\"") }
                event.addAlarm(EKAlarm(relativeOffset: offset))
            }
        }
    }

    if let repeatSpec = args.str("repeat") {
        if repeatSpec.lowercased() == "none" {
            event.recurrenceRules?.forEach { event.removeRecurrenceRule($0) }
        } else {
            event.recurrenceRules?.forEach { event.removeRecurrenceRule($0) }
            event.addRecurrenceRule(buildRule(repeatSpec, until: args.str("until"), count: args.int("count")))
        }
    }
}

func buildRule(_ spec: String, until: String?, count: Int?) -> EKRecurrenceRule {
    var interval = 1
    var body = spec.lowercased()
    if let slash = body.firstIndex(of: "/") {
        interval = Int(body[body.index(after: slash)...]) ?? 1
        body = String(body[body.startIndex..<slash])
    }

    var frequency: EKRecurrenceFrequency
    var days: [EKRecurrenceDayOfWeek]?
    switch body {
    case "daily": frequency = .daily
    case "weekly": frequency = .weekly
    case "monthly": frequency = .monthly
    case "yearly": frequency = .yearly
    case "weekdays":
        frequency = .weekly
        days = [EKRecurrenceDayOfWeek(.monday), EKRecurrenceDayOfWeek(.tuesday),
                EKRecurrenceDayOfWeek(.wednesday), EKRecurrenceDayOfWeek(.thursday),
                EKRecurrenceDayOfWeek(.friday)]
    default:
        die(.usage, "--repeat takes daily, weekly, monthly, yearly, weekdays, or one of those with /N (e.g. weekly/2)")
    }

    var end: EKRecurrenceEnd?
    if let until, let date = parseDate(until, endOfDay: true) { end = EKRecurrenceEnd(end: date) }
    else if let count { end = EKRecurrenceEnd(occurrenceCount: count) }

    return EKRecurrenceRule(recurrenceWith: frequency, interval: max(1, interval),
                            daysOfTheWeek: days, daysOfTheMonth: nil, monthsOfTheYear: nil,
                            weeksOfTheYear: nil, daysOfTheYear: nil, setPositions: nil, end: end)
}
