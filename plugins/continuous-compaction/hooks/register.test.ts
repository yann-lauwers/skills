import { expect, test } from 'claude-code/testing'

test('/compaction answers when the session has no /config row and no question dialog', async ($, on) => {
  on('command.register', () => ({ value: { command: 'compaction' } }))
  on('session.start', (_, e) => ({ cwd: e.cwd }))
  on('clock.now', () => ({ value: 0 }))
  await $.session.start({ cwd: '/', surface: 'desktop', isInteractive: true })

  const all = await $.command.run({ command: 'compaction', args: 'all 60' })
  expect(all.text).toContain('options.pct_floor to 60')

  const bare = await $.command.run({ command: 'compaction', args: '' })
  expect(bare.text).toContain('/compaction all <1-100>')
})
