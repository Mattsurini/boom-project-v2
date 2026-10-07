# PR Contribution Workflow

How to contribute pull requests to pollinations/pollinations for the "Contribute a pull request" quest (5 pollen).

## Repository Structure
```
pollinations/
├── apps/                    # Deployed agents & applications
│   ├── agent-catgpt-comic/   # Example prompt agent
│   ├── agent-sirius-elevator/
│   └── ...
├── packages/
│   └── polli-cli/           # CLI tool (polli)
│       ├── src/
│       │   ├── commands/     # CLI commands
│       │   └── harnesses/    # Coding agent integrations
│       └── bin/polli.js
├── enter.pollinations.ai/    # Enter dashboard frontend
├── gen.pollinations.ai/      # Gen API frontend
├── pollinations.ai/          # Main website
└── *.md                      # Root documentation
```

## Finding Work

### High Reward: POLLEN-QUEST Issues
| Issue | Title | Reward |
|-------|-------|--------|
| #15014 | Install Pollinations MCP servers into coding agents from Polli CLI | ~10-15 pollen |
| #15017 | Build a model router as a code agent | ~10-15 pollen |
| #15054 | Build an agent that uses collective memory | ~10-15 pollen |

### Quick Wins (Documentation/Bug Fixes)
- Check `DEV-BUG` label: https://github.com/pollinations/pollinations/issues?q=is%3Aissue+is%3Aopen+label%3ADEV-BUG
- Documentation in `enter.pollinations.ai/`, `gen.pollinations.ai/`, `pollinations.ai/`
- Root markdown files: `README.md`, `AGENTS.md`, `CLAUDE.md`, `CONTRIBUTING.md`
- Typos, broken links, outdated examples

## PR Submission Process

### 1. Fork & Clone
```bash
# Fork at: https://github.com/pollinations/pollinations/fork
git clone https://github.com/<YOUR_USERNAME>/pollinations.git
cd pollinations
npm install  # or pnpm install
```

### 2. Create Branch & Make Changes
```bash
git checkout -b fix/descriptive-name
# Edit files...
git add .
git commit -m "docs: fix typo in README.md"
git push origin fix/descriptive-name
```

### 3. Open PR
- Go to your fork on GitHub
- Click **Compare & pull request**
- Title: Clear description (e.g., "docs: fix typo in README.md")
- Description: Link issue if applicable (`Fixes #1234`)
- Submit

### 4. Wait for Merge
- Maintainers review (usually fast for docs/typos)
- Once merged → Claim quest at enter.pollinations.ai/quests
- **Bonus**: If first PR, also claim "Senior dev" (2 pollen) if GitHub account ≥2 years old

## Repo-Specific Patterns

### Adding a New Agent (for POLLEN-QUEST)
```bash
# Create agent folder
mkdir -p apps/agent-<name>
# Add agent.json (see references/agent-creation.md)
# Add README.md with usage examples
# Test locally if possible
```

### Polli CLI Commands
- Location: `packages/polli-cli/src/commands/`
- Harnesses: `packages/polli-cli/src/harnesses/`
- Add new command: Create `commands/<name>.ts` + register in `commands/index.ts`
- Add new harness: Create `harnesses/<name>.ts` + export in `harnesses/index.ts`

### Running Tests
```bash
cd packages/polli-cli
npm test  # vitest
```

### Linting
```bash
npm run lint  # biome check --write src/
```

## Commit Message Convention
```
docs: fix typo in README.md
fix: resolve 5xx error in agent endpoints
feat: add new harness for <client>
refactor: simplify MCP config in opencode harness
```

## Verification Checklist
- [ ] Fork created and cloned
- [ ] Changes are minimal and focused
- [ ] Tests pass (if applicable)
- [ ] Lint passes
- [ ] PR description clear
- [ ] PR merged by maintainers
- [ ] Quest claimed at enter.pollinations.ai/quests

## Common PR Types for Quick Merge
1. **Typo fixes** in any `.md` file
2. **Broken link fixes** in documentation
3. **Outdated example updates** in `README.md`, `AGENTS.md`
4. **Missing alt text** for images in docs
5. **Clarification comments** in complex config files
6. **Test additions** for existing functionality in `polli-cli`

## Pollinations-Specific Notes
- Monorepo with multiple packages
- Uses `npm`/`pnpm` workspaces
- TypeScript throughout
- Biome for linting/formatting
- Vitest for testing
- Agents deployed via `apps/agent-<name>/` with `agent.json`