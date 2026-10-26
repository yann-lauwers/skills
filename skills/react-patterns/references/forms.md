# Forms

The React 19 action path for new forms, when a controlled input earns its keystroke cost, and where a form library takes over. Read before wiring a submit handler or reaching for local form state.

## React 19 form actions — the default for new code

```tsx
"use client";
import { useActionState } from "react";

const initial = { error: null as string | null };

async function updateUserAction(_prev: typeof initial, formData: FormData) {
  "use server";
  const parsed = UserSchema.safeParse(Object.fromEntries(formData));
  if (!parsed.success) return { error: "Invalid input" };
  await db.user.update({ where: { id: parsed.data.id }, data: parsed.data });
  return { error: null };
}

export function UserForm() {
  const [state, formAction, isPending] = useActionState(updateUserAction, initial);
  return (
    <form action={formAction}>
      <input name="name" required />
      <button type="submit" disabled={isPending}>Save</button>
      {state.error !== null && <p role="alert">{state.error}</p>}
    </form>
  );
}
```

## Controlled inputs

Control an input when its value drives other UI, formats on every keystroke, or feeds real-time validation. Otherwise leave it uncontrolled and read it off `FormData`.

## Complex forms

Multi-step flows, dynamic field arrays and cross-field validation go to a library — React Hook Form or TanStack Form. Hand-rolled form state past trivial complexity is a maintenance trap.

A schema decides whether a form is valid — the action's `safeParse` or the library's resolver — never hand-rolled checks.

## Optimistic UI with `useOptimistic`

```tsx
"use client";
import { useOptimistic } from "react";

export function MessageList({ messages }: { messages: Message[] }) {
  const [optimistic, addOptimistic] = useOptimistic(
    messages,
    (state, newMessage: Message) => [...state, newMessage],
  );

  async function send(formData: FormData) {
    const text = String(formData.get("text"));
    addOptimistic({ id: "pending", text, sender: "me" });
    await saveMessage(text);
  }

  return (
    <>
      <ul>{optimistic.map((m) => <li key={m.id}>{m.text}</li>)}</ul>
      <form action={send}>
        <input name="text" />
        <button type="submit">Send</button>
      </form>
    </>
  );
}
```
