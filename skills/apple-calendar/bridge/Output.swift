import CoreGraphics
import EventKit
import Foundation

func openStore(write: Bool) -> EKEventStore {
    let store = EKEventStore()
    var granted = false
    var settled = false
    let handler: (Bool, Error?) -> Void = { ok, _ in granted = ok; settled = true }
    if #available(macOS 14.0, *) {
        store.requestFullAccessToEvents(completion: handler)
    } else {
        store.requestAccess(to: .event, completion: handler)
    }
    let deadline = Date().addingTimeInterval(60)
    while !settled && Date() < deadline { CFRunLoopRunInMode(.defaultMode, 0.1, true) }

    let status = EKEventStore.authorizationStatus(for: .event)
    let full: Bool
    if #available(macOS 14.0, *) { full = status == .fullAccess } else { full = status == .authorized }

    if full { return store }
    if write, #available(macOS 14.0, *), status == .writeOnly { return store }

    die(.access, """
        Calendars access is \(describe(status)) (granted=\(granted)).
        Grant it in System Settings → Privacy & Security → Calendars → Calendar Bridge,
        then re-run. Reading events needs Full Access; write-only is not enough.
        """)
}

func describe(_ status: EKAuthorizationStatus) -> String {
    switch status.rawValue {
    case 0: return "not determined"
    case 1: return "restricted"
    case 2: return "denied"
    case 3: return "full"
    case 4: return "write-only"
    default: return "unknown(\(status.rawValue))"
    }
}

// MARK: - Output shapes

struct CalendarOut: Encodable {
    let id: String
    let title: String
    let source: String
    let sourceType: String
    let color: String?
    let editable: Bool
    let subscribed: Bool
    let isDefaultForNewEvents: Bool
}

struct ParticipantOut: Encodable {
    let name: String?
    let email: String?
    let status: String
    let role: String
    let isMe: Bool
}

struct EventOut: Encodable {
    let id: String
    let ref: String
    let title: String
    let calendar: String
    let calendarId: String
    let start: String
    let end: String
    let allDay: Bool
    let durationMinutes: Int
    let timeZone: String?
    let location: String?
    let notes: String?
    let url: String?
    let conferenceUrl: String?
    let status: String
    let availability: String
    let isRecurring: Bool
    let recurrence: String?
    let isDetached: Bool
    let organizer: ParticipantOut?
    let attendees: [ParticipantOut]
    let myStatus: String?
    let alarmsMinutesBefore: [Int]
    let lastModified: String?
    let openUrl: String
}

struct SlotOut: Encodable {
    let start: String
    let end: String
    let durationMinutes: Int
}

func hex(_ cg: CGColor?) -> String? {
    guard let c = cg?.components, c.count >= 3 else { return nil }
    return String(format: "#%02X%02X%02X", Int(c[0] * 255), Int(c[1] * 255), Int(c[2] * 255))
}

func sourceTypeName(_ t: EKSourceType) -> String {
    switch t {
    case .local: return "local"
    case .exchange: return "exchange"
    case .calDAV: return "caldav"
    case .mobileMe: return "mobileme"
    case .subscribed: return "subscribed"
    case .birthdays: return "birthdays"
    @unknown default: return "unknown"
    }
}

func statusName(_ s: EKEventStatus) -> String {
    switch s {
    case .none: return "none"
    case .confirmed: return "confirmed"
    case .tentative: return "tentative"
    case .canceled: return "canceled"
    @unknown default: return "unknown"
    }
}

func participantStatusName(_ s: EKParticipantStatus) -> String {
    switch s {
    case .unknown: return "unknown"
    case .pending: return "pending"
    case .accepted: return "accepted"
    case .declined: return "declined"
    case .tentative: return "tentative"
    case .delegated: return "delegated"
    case .completed: return "completed"
    case .inProcess: return "in-process"
    @unknown default: return "unknown"
    }
}

func participantRoleName(_ r: EKParticipantRole) -> String {
    switch r {
    case .unknown: return "unknown"
    case .required: return "required"
    case .optional: return "optional"
    case .chair: return "chair"
    case .nonParticipant: return "non-participant"
    @unknown default: return "unknown"
    }
}

func emailOf(_ p: EKParticipant) -> String? {
    let s = p.url.absoluteString
    return s.hasPrefix("mailto:") ? String(s.dropFirst("mailto:".count)) : (s.isEmpty ? nil : s)
}

func participantOut(_ p: EKParticipant) -> ParticipantOut {
    ParticipantOut(name: p.name, email: emailOf(p),
                   status: participantStatusName(p.participantStatus),
                   role: participantRoleName(p.participantRole),
                   isMe: p.isCurrentUser)
}

let conferenceHosts = ["meet.google.com", "zoom.us", "teams.microsoft.com", "teams.live.com",
                       "whereby.com", "meet.jit.si", "webex.com", "around.co", "gather.town",
                       "chime.aws", "bluejeans.com", "riverside.fm", "tldv.io", "slack.com/huddle"]

func findConferenceUrl(_ event: EKEvent) -> String? {
    let haystack = [event.url?.absoluteString, event.location, event.notes]
        .compactMap { $0 }.joined(separator: "\n")
    guard !haystack.isEmpty,
          let detector = try? NSDataDetector(types: NSTextCheckingResult.CheckingType.link.rawValue)
    else { return nil }
    let range = NSRange(haystack.startIndex..<haystack.endIndex, in: haystack)
    for match in detector.matches(in: haystack, options: [], range: range) {
        guard let url = match.url?.absoluteString else { continue }
        if conferenceHosts.contains(where: { url.contains($0) }) { return url }
    }
    return nil
}

func openUrlFor(_ event: EKEvent) -> String {
    let stamp = utcCompact.string(from: event.startDate ?? Date())
    let ident = event.calendarItemExternalIdentifier ?? event.eventIdentifier ?? ""
    return "ical://ekevent/\(stamp)/\(ident)?method=show&options=more"
}

func eventOut(_ e: EKEvent) -> EventOut {
    let start = e.startDate ?? Date()
    let end = e.endDate ?? start
    let alarms = (e.alarms ?? []).map { Int((-$0.relativeOffset) / 60) }
    let mine = (e.attendees ?? []).first(where: { $0.isCurrentUser })
    return EventOut(
        id: e.eventIdentifier ?? "",
        ref: "\(e.eventIdentifier ?? "")@\(isoOut.string(from: start))",
        title: e.title ?? "(untitled)",
        calendar: e.calendar?.title ?? "",
        calendarId: e.calendar?.calendarIdentifier ?? "",
        start: isoOut.string(from: start),
        end: isoOut.string(from: end),
        allDay: e.isAllDay,
        durationMinutes: Int(end.timeIntervalSince(start) / 60),
        timeZone: e.timeZone?.identifier,
        location: e.location,
        notes: e.notes,
        url: e.url?.absoluteString,
        conferenceUrl: findConferenceUrl(e),
        status: statusName(e.status),
        availability: availabilityName(e.availability),
        isRecurring: e.hasRecurrenceRules,
        recurrence: e.recurrenceRules?.first.map { describeRule($0) },
        isDetached: e.isDetached,
        organizer: e.organizer.map(participantOut),
        attendees: (e.attendees ?? []).map(participantOut),
        myStatus: mine.map { participantStatusName($0.participantStatus) },
        alarmsMinutesBefore: alarms,
        lastModified: e.lastModifiedDate.map { isoOut.string(from: $0) },
        openUrl: openUrlFor(e))
}

func availabilityName(_ a: EKEventAvailability) -> String {
    switch a {
    case .notSupported: return "not-supported"
    case .busy: return "busy"
    case .free: return "free"
    case .tentative: return "tentative"
    case .unavailable: return "unavailable"
    @unknown default: return "unknown"
    }
}

func describeRule(_ r: EKRecurrenceRule) -> String {
    var parts: [String] = []
    let unit: String
    switch r.frequency {
    case .daily: unit = "day"
    case .weekly: unit = "week"
    case .monthly: unit = "month"
    case .yearly: unit = "year"
    @unknown default: unit = "period"
    }
    parts.append(r.interval > 1 ? "every \(r.interval) \(unit)s" : "every \(unit)")
    if let days = r.daysOfTheWeek, !days.isEmpty {
        let names = ["", "sun", "mon", "tue", "wed", "thu", "fri", "sat"]
        parts.append("on " + days.map { names[$0.dayOfTheWeek.rawValue] }.joined(separator: ","))
    }
    if let end = r.recurrenceEnd {
        if let d = end.endDate { parts.append("until " + fixedFormatter("yyyy-MM-dd").string(from: d)) }
        else if end.occurrenceCount > 0 { parts.append("for \(end.occurrenceCount) occurrences") }
    }
    return parts.joined(separator: " ")
}

func emit<T: Encodable>(_ value: T, pretty: Bool) {
    let encoder = JSONEncoder()
    encoder.outputFormatting = pretty ? [.prettyPrinted, .sortedKeys, .withoutEscapingSlashes]
                                      : [.sortedKeys, .withoutEscapingSlashes]
    guard let data = try? encoder.encode(value) else { die(.rejected, "could not encode the result as JSON") }
    if envelopePath != nil {
        writeEnvelope(ok: true, code: 0, error: nil, data: data)
        return
    }
    FileHandle.standardOutput.write(data)
    FileHandle.standardOutput.write("\n".data(using: .utf8)!)
}

// MARK: - Selection helpers

/// Resolves `--calendar` values, which may be identifiers or titles (case-insensitive).
