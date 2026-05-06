# CLAUDE.md Addendum — TypeScript Stack

Paste this block into your project's `CLAUDE.md` under a `## TypeScript` section. Fill in the bracketed placeholders.

---

## TypeScript

### Toolchain

| Tool | Version | Purpose |
|---|---|---|
| Node.js | [e.g., 22.x] | Runtime |
| Package manager | [npm / pnpm / yarn] | |
| TypeScript | [e.g., 5.x] | Type checker + compiler |
| Linter | [ESLint + typescript-eslint] | |
| Formatter | [Prettier] | |
| Test runner | [Vitest / Jest] | |
| Build tool | [tsc / esbuild / tsup / vite] | |

**Run checks:**
```bash
# Type check (no emit)
[npx tsc --noEmit / pnpm typecheck]

# Lint
[npx eslint . --max-warnings 0 / pnpm lint]

# Format check (non-destructive)
[npx prettier --check . / pnpm format:check]

# Tests
[npx vitest run / pnpm test --run]

# Dependency audit
[npm audit / pnpm audit]
```

### Project structure

```
[project_name]/
├── src/                   ← source root
│   └── [module]/
├── tests/                 ← or co-located *.test.ts
├── tsconfig.json          ← strict: true required
├── package.json
└── [vitest.config.ts / jest.config.ts]
```

### Conventions

- **`tsconfig.json`:** `"strict": true` always enabled — no exceptions
- **Types:** explicit return types on all exported functions; avoid `any`; use `unknown` + type guard instead
- **Null handling:** `strictNullChecks` on; use `??` and optional chaining `?.` over non-null assertions `!`
- **Imports:** absolute paths via `paths` in tsconfig; no `../../../` chains
- **Test naming:** `describe('<target>') > it('<scenario>')` — readable without opening the file
- **Async:** always `await` async calls in tests; never `void` an unhandled promise in production code

### Things to avoid

- Don't use `as any` — use `unknown` + type guard or fix the type
- Don't use `// @ts-ignore` without a comment explaining why it's a false positive
- Don't use `!` (non-null assertion) unless you can explain why null is impossible at that point
- Don't import `*` from large libraries — use named imports for tree-shaking
- Don't use `require()` in TypeScript source — use `import`
- Don't leave `console.log` in non-script production code — use a structured logger

### Slash commands (TypeScript)

- `/test-gen` — generate Vitest/Jest tests (happy path, edge, error, contract)
- `/type-fix` — explain and fix tsc/eslint type errors with minimal changes
- `/deps-audit` — CVE scan + outdated package check + upgrade recommendations
