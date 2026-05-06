# CLAUDE.md Addendum — Go Stack

Paste this block into your project's `CLAUDE.md` under a `## Go` section. Fill in the bracketed placeholders.

---

## Go

### Toolchain

| Tool | Version | Purpose |
|---|---|---|
| Go | [e.g., 1.23] | Runtime + compiler |
| Linter | [golangci-lint / staticcheck] | |
| Formatter | [gofmt / goimports] | |
| Test runner | [go test] | |
| Vulnerability scanner | [govulncheck] | |
| Build tool | [go build / Makefile] | |

**Run checks:**
```bash
# Build
go build ./...

# Vet
go vet ./...

# Lint
[golangci-lint run ./... / staticcheck ./...]

# Format check (non-destructive)
gofmt -l .    # lists files that would change

# Tests
go test ./...

# Tests with race detector
go test -race ./...

# Vulnerability scan
govulncheck ./...
```

### Project structure

```
[module_name]/
├── cmd/
│   └── [app]/
│       └── main.go        ← entry point(s)
├── internal/              ← private packages (not importable externally)
│   └── [package]/
├── pkg/                   ← public packages (importable externally)
│   └── [package]/
├── go.mod
└── go.sum
```

### Conventions

- **Errors:** always return `error` as the last return value; wrap with `fmt.Errorf("context: %w", err)`; never discard errors with `_`
- **Interfaces:** define interfaces in the consuming package, not the implementing package; keep them small (1–3 methods)
- **Naming:** exported names are PascalCase; unexported are camelCase; acronyms all-caps (`HTTPClient`, `userID`)
- **Goroutines:** never start a goroutine without a clear ownership and shutdown path
- **Context:** always accept `context.Context` as the first parameter for I/O-bound functions; never store context in a struct
- **Tests:** table-driven with `t.Run`; use `t.Parallel()` in subtests where safe

### Things to avoid

- Don't use `interface{}` / `any` to bypass type checks — define a proper interface or use generics
- Don't ignore returned errors — wrap and return, or handle explicitly
- Don't use `init()` for application logic — use explicit initialization
- Don't use global mutable state — pass dependencies explicitly
- Don't use `panic` for expected error conditions — reserve for truly unrecoverable states
- Don't use `time.Sleep` in tests — use channels or `sync.WaitGroup` for synchronization

### Slash commands (Go)

- `/test-gen` — generate table-driven Go tests (happy path, edge, error, contract)
- `/type-fix` — explain and fix `go build` / `go vet` / `staticcheck` errors with minimal changes
- `/deps-audit` — CVE scan with `govulncheck` + outdated module check + upgrade recommendations
