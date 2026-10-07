# Debugging Patterns from Boom Project Session

## Pattern 1: Venv Path Mismatch

**Error**: `No Python at '"C:\\Users\\Fourt\\AppData\\Roaming\\uv\\python\\cpython-3.11-windows-x86_64-none\\python.exe"'`

**Investigation**:
1. Checked `.venv/pyvenv.cfg` - showed wrong `home` and `executable` paths
2. The venv was created from a different Python installation
3. Fixed by updating `pyvenv.cfg` to point to local venv paths

**Key Insight**: When a venv is moved or the system Python changes, `pyvenv.cfg` becomes stale. Always verify:
- `home` = venv directory
- `executable` = venv's python.exe
- `command` = how the venv was created

## Pattern 2: Model 404 on Provider

**Error**: `NotFoundError [HTTP 404]` from `https://integrate.api.nvidia.com/v1`

**Investigation**:
1. Config had `model.default: nvidia/nemotron-3-ultra-550b-a55b`
2. Queried provider's `/v1/models` endpoint with API key
3. Found actual available models: `nvidia/nemotron-3-super-120b-a12b`, `nvidia/nemotron-3-ultra-550b-a55b`, etc.
4. The model ID format matters - some providers want `nvidia/model-name`, others just `model-name`

**Key Insight**: Always verify model availability via provider's `/v1/models` endpoint before assuming a model ID works. Model IDs in config must exactly match what the API returns.

## Pattern 3: Skill Not Found (Router)

**Error**: `Skill 'boom-auto-workflow-router' not found`

**Investigation**:
1. Skill referenced in `TURBOZ.md`, `.hermes.md`, `opencode.json`
2. Found in `.claude/skills/boom-auto-workflow-router/SKILL.md`
3. But NOT in Hermes `skills/` directory
4. Two different skill systems: OpenCode (`.claude/skills/`) vs Hermes (`skills/`)

**Key Insight**: Project docs may reference skills in one system (OpenCode) that don't exist in the active system (Hermes). Always verify skill exists in the active system's skill directory.

## Pattern 4: Config Provider/Key Mismatch

**Error**: `No API key found for provider 'openrouter'` despite key in `.env`

**Investigation**:
1. Key was `OPENROUTER_API_KEY=` (empty)
2. NVIDIA key was `NVIDIA_API_KEY=***` (set)
3. Config had `model.provider: openrouter` but no OpenRouter key
4. Switching to `model.provider: nvidia` with NVIDIA key worked

**Key Insight**: The provider in `config.yaml` must match the API key in `.env`. Format: `{PROVIDER}_API_KEY` (uppercase).