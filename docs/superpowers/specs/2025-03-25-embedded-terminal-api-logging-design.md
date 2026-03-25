---
title: Embedded Terminal & API Request Viewer
status: drafting
authors: [claude]
created: 2025-03-25
---

# Embedded Terminal & API Request Viewer Design

## Overview

This feature adds two new capabilities to the Free Claude Code desktop application:
1. An **embedded terminal** that runs the Claude Code CLI directly within the desktop app
2. An **API Request Viewer** page that displays real-time logs and history of outgoing requests to LLM providers

Both features are implemented as separate pages in the sidebar navigation.

---

## 1. Embedded Terminal

### Goals
- Allow users to run Claude Code directly from the desktop app without switching to a separate terminal window
- Support image pasting and drag-and-drop (converts to file paths)
- Provide an interactive, fully functional terminal experience with proper ANSI color support

### Architecture

#### Components
- **TerminalPage**: New page class in `desktop/pages/terminal_page.py`
- **TerminalWidget**: CustomTkinter widget using `tkinter.Text` for display + `pyte` for terminal emulation
- **ProcessManager**: Handles `subprocess.Popen` with PTY on Unix, `CREATE_NEW_CONSOLE` on Windows
- **ImageHandler**: Detects clipboard images, handles drag-drop, saves to temp folder, inserts path at cursor

#### Dependencies
```python
# New dependencies to add to pyproject.toml
pyte >= 1.0.0  # Terminal emulator
Pillow >= 10.0.0  # Image handling (already likely present)
```

#### Terminal Implementation Details

**Process Spawning**:
```python
def start_claude_process(env: dict[str, str]) -> subprocess.Popen:
    """Start claude CLI with configured environment."""
    # On Unix: use pty for proper terminal behavior
    # On Windows: use subprocess with creationflags
    return subprocess.Popen(
        ["claude"],
        env=env,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        # Platform-specific flags for terminal mode
    )
```

**I/O Handling**:
- **stdout reading**: Async thread reads from subprocess stdout, feeds to `pyte` screen, updates Text widget
- **stdin writing**: Key presses from Text widget sent to subprocess stdin (with proper control sequences)
- **ANSI colors**: `pyte` parses ANSI escape codes and provides styled characters; render with CustomTkinter text tags

**Image Paste Support**:
- Bind `<Control-v>` and `<Shift-Insert>` to paste handler
- Check clipboard for image (`PIL.ImageGrab.clipboard_get()`)
- If image: save to `temp/claude_images/` with timestamp, insert `path/to/file.png` at cursor
- If text: normal paste

**Drag-and-Drop Support**:
- Register drop target on Text widget (`widget.drop_target_register()`)
- On drop: check if file is image (extension or PIL verify), copy to `temp/claude_images/`, insert path
- Show visual feedback during drag (highlight widget border)

**Signal Handling**:
- Ctrl+C: Send SIGINT to subprocess (Unix: `signal.SIGINT`, Windows: `GenerateConsoleCtrlEvent`)
- Ctrl+Z: Suspend (if desired)
- Proper cleanup on page close/exit

---

## 2. API Request Viewer

### Goals
- Provide visibility into what requests are being sent to API providers
- Show both real-time stream of requests and historical data
- Allow inspection of full request/response payloads for debugging

### Architecture

#### New FastAPI Endpoints
Add to `api/routes_request_logging.py` (new module):

```python
router = APIRouter()

@router.get("/requests")
async def list_requests(limit: int = 100) -> list[RequestLogSummary]:
    """Return recent request summaries."""

@router.get("/requests/{request_id}")
async def get_request(request_id: str) -> RequestLogDetail:
    """Return full request/response details."""

@router.websocket("/requests/ws")
async def websocket_requests(websocket: WebSocket):
    """Stream new requests in real-time."""
```

#### Request Logging Middleware

Create `api/middleware/request_logging.py`:

```python
class RequestLoggingMiddleware:
    """Intercepts /v1/messages requests, logs, and stores in memory."""

    def __init__(self, ring_buffer: RequestRingBuffer):
        self.ring_buffer = ring_buffer

    async def __call__(self, request: Request, call_next):
        if request.url.path == "/v1/messages":
            # Capture request body
            body = await request.body()
            request_data = json.loads(body)

            # Generate request_id if not present
            request_id = extract_or_generate_id(request_data)

            # Log request start
            log_entry = RequestLog(
                id=request_id,
                timestamp=datetime.utcnow(),
                model=request_data.get("model"),
                request_payload=request_data,
                status="in_progress",
            )
            self.ring_buffer.add(log_entry)

            # Intercept response to capture provider reply
            response = await call_next(request)

            # Read streaming response, capture full body
            response_body = await self._capture_stream(response)

            # Update log entry with response
            log_entry.response_payload = response_body
            log_entry.status = "success" if response.status_code == 200 else "error"
            log_entry.duration_ms = (datetime.utcnow() - log_entry.timestamp).total_seconds() * 1000
            log_entry.output_tokens = extract_output_tokens(response_body)

            return response
        return await call_next(request)
```

#### Storage
- **In-memory ring buffer**: `collections.deque` with maxlen=1000 for recent requests
- **SQLite persistence** (optional): Store complete history in `request_logs.db` for long-term storage
- **Schema**:
  ```sql
  CREATE TABLE request_logs (
      id TEXT PRIMARY KEY,
      timestamp DATETIME,
      model TEXT,
      input_tokens INTEGER,
      output_tokens INTEGER,
      duration_ms REAL,
      status TEXT,
      request_payload JSON,
      response_payload JSON
  );
  ```

#### Desktop Page: RequestsPage

Located in `desktop/pages/request_viewer.py`:

**UI Components**:
- **Toolbar**: Refresh button, filter input, clear button (if admin mode)
- **Live Feed Panel**: Scrollable list of recent requests (last 20) with colored status badges
- **History Table**: Full table with sortable columns (timestamp, model, tokens, duration, status)
- **Detail Panel**: On row select, shows formatted JSON of request/response in tabs

**Polling**:
- Every 2 seconds, `GET /api/requests?limit=100` to refresh table
- Optional WebSocket connection for instant updates (future enhancement)

---

## Data Flow Diagrams

### Terminal Data Flow
```
User keystroke → Text widget → ProcessManager.stdin → Claude CLI
Claude output → stdout → ProcessManager → pyte → Text widget (ANSI styled)
Image drop → Drop handler → PIL verify → save temp → insert path
```

### Request Logging Data Flow
```
Claude → /v1/messages → Middleware → capture request → call_next
           ↓
    Provider response → capture body → update ring buffer
           ↓
     Desktop /requests poll → JSON response → update table
```

---

## Implementation Phases

### Phase 1: Backend Request Logging
1. Create `RequestLog` dataclass
2. Implement ring buffer storage
3. Create middleware and add to FastAPI app (before router)
4. Add new `/requests` endpoints
5. Wire middleware into `api/app.py` lifespan

### Phase 2: Desktop Request Viewer Page
1. Create `RequestViewerPage` class
2. Build UI (table + detail panel)
3. Implement polling mechanism
4. Add navigation button in sidebar

### Phase 3: Embedded Terminal
1. Create `TerminalPage` class
2. Implement `TerminalWidget` with pyte integration
3. Add process spawning with environment from settings
4. Add I/O handling (stdout reading, stdin writing)
5. Implement ANSI color rendering in Text widget
6. Add image paste (clipboard) and drag-drop handlers
7. Add terminal control (start/stop from server control page integration)

### Phase 4: Polish
1. Error handling (process crashes, broken pipes)
2. Terminal resize handling
3. Scrollback buffer limits
4. Copy/paste text selection
5. Status indicators (connected/disconnected)
6. Configuration options (font size, colors)

---

## Error Handling

### Terminal
- **Process fails to start**: Show error in terminal widget, allow retry
- **Pipe broken**: Detect EOF, attempt restart if user configured
- **Unicode errors**: Fallback encoding handling
- **OOM from scrollback**: Limit buffer to 10k lines

### Request Logging
- **Middleware errors**: Log but don't break request flow
- **Ring buffer full**: Auto-rotate (deque handles this)
- **DB errors**: Fall back to in-memory only, log warning
- **JSON parse errors**: Store raw bytes as base64

---

## Testing Strategy

### Request Logging
- Unit test middleware: mock requests, verify logs written
- Integration test: make API call, assert entry in ring buffer
- Endpoint tests: `GET /requests` returns expected structure

### Terminal
- Unit test image handler: verify path insertion on paste
- Mock process I/O: test that output displays correctly
- Manual E2E: start terminal, run `claude "hello"`, verify responses

---

## Configuration

No new configuration needed for basic functionality.

Optional settings:
- `REQUEST_LOG_MAX_ENTRIES`: Size of ring buffer (default 1000)
- `REQUEST_LOG_PERSIST`: Enable SQLite storage (default false)
- `TERMINAL_SCROLLBACK_LINES`: Max lines in terminal (default 10000)

---

## Success Criteria

1. Embedded terminal starts `claude` process when page opened
2. Terminal accepts keyboard input and displays output with colors
3. Ctrl+V pastes image file paths, drag-drop images inserts paths
4. Request viewer shows real-time updates within 2 seconds
5. Clicking a request shows full JSON payload (request + response)
6. All existing tests pass; new tests added for core functionality

---

## Open Questions

1. Should the terminal auto-start when the desktop app opens? (Initial: no, user clicks "Terminal" tab)
2. Should request history persist across app restarts? (Initial: no, in-memory only; SQLite optional)
3. Terminal font family/size: use system default or configurable? (Initial: system default)

---

## Trade-offs Considered

| Decision | Option A (chosen) | Option B | Reason |
|----------|-------------------|----------|--------|
| Terminal embed | pyte + tkinter | webview (HTML/JS) | Simpler integration, no web dependencies |
| Request logging | Middleware + ring buffer | Log file tailing | Structured, reliable, no parsing fragility |
| Real-time updates | Polling 2s | WebSocket | Simpler, adequate for low-frequency |
| Storage | In-memory ring buffer | Full SQLite by default | Avoid bloat, opt-in for persistence |
