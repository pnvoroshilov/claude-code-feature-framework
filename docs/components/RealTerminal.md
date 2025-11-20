# RealTerminal Component

React component providing an embedded terminal interface with xterm.js and WebSocket-based communication to Claude Code sessions.

## Location

`claudetask/frontend/src/components/RealTerminal.tsx`

## Purpose

Provides a real terminal interface that:
- Connects to embedded Claude Code sessions via WebSocket
- Displays session output in real-time with proper buffering
- Handles user input and command execution
- Manages scroll behavior intelligently
- Supports session history replay on reconnection

## Recent Updates (v2.1 - WebSocket Buffering & Scroll Improvements)

### Terminal Auto-Scroll Fix
**Problem Solved**: Terminal previously jumped back to bottom even when user scrolled up to review output.

**Solution Implemented**:
- **User Scroll Detection**: Tracks when user manually scrolls up from bottom
- **Conditional Auto-Scroll**: Only auto-scrolls when user is at bottom
- **Smooth Buffer Flushing**: Batches writes to prevent scroll jumping

### WebSocket Output Buffering
**Problem Solved**: Rapid output caused performance issues and scroll jumping.

**Solution Implemented**:
- **Write Buffering**: Accumulates output data before writing to terminal
- **Batch Flushing**: Writes buffered content in controlled batches
- **Increased Scrollback**: Extended from 1000 to 10000 lines for better history

### Key Improvements
```typescript
// User scroll tracking
const isUserScrollingRef = useRef(false);
const lastScrollPositionRef = useRef(0);
const writeBufferRef = useRef<string[]>([]);
const flushTimeoutRef = useRef<NodeJS.Timeout | null>(null);

// Flush buffer to terminal
const flushBuffer = useCallback(() => {
  if (writeBufferRef.current.length === 0) return;
  if (!terminal.current) return;

  // Write all buffered content at once
  const content = writeBufferRef.current.join('');
  terminal.current.write(content);

  // Clear buffer
  writeBufferRef.current = [];

  // Scroll to bottom only if user hasn't scrolled up
  if (!isUserScrollingRef.current) {
    terminal.current.scrollToBottom();
  }
}, []);

// Track user scroll position
terminal.current.onScroll(() => {
  if (!terminal.current) return;

  const viewport = terminal.current.buffer.active.viewportY;
  const baseY = terminal.current.buffer.active.baseY;

  // User scrolled up from bottom
  if (viewport < baseY - 1) {
    isUserScrollingRef.current = true;
  } else {
    // User scrolled back to bottom - re-enable auto-scroll
    isUserScrollingRef.current = false;
  }

  lastScrollPositionRef.current = viewport;
});
```

## Features

### 1. Terminal Interface
- Full xterm.js terminal emulation
- Syntax highlighting and colors support
- Cursor blinking and proper rendering
- Extended scrollback buffer (10,000 lines)

### 2. WebSocket Connection
- Real-time bidirectional communication
- Automatic reconnection on disconnect
- Session history replay on reconnection
- Ping/pong keepalive mechanism

### 3. Smart Scroll Management
- **User-Controlled Scrolling**: Detects and respects manual scroll position
- **Auto-Scroll When Appropriate**: Only scrolls to bottom when user is at bottom
- **Buffered Output**: Prevents scroll jumping from rapid output
- **Smooth Experience**: No interruptions when reviewing previous output

### 4. Session Management
- Auto-checks for active sessions on mount
- Graceful session startup and shutdown
- Session history preservation
- Multiple session support

## Props

```typescript
interface RealTerminalProps {
  taskId: number;  // Task ID for the Claude session
}
```

## State Management

```typescript
const [isConnecting, setIsConnecting] = useState(false);
const terminal = useRef<Terminal | null>(null);
const fitAddon = useRef<FitAddon | null>(null);
const wsRef = useRef<WebSocket | null>(null);
const sessionCheckDoneRef = useRef(false);
const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
const userStoppedRef = useRef(false);
const isUserScrollingRef = useRef(false);
const lastScrollPositionRef = useRef(0);
const writeBufferRef = useRef<string[]>([]);
const flushTimeoutRef = useRef<NodeJS.Timeout | null>(null);
```

## API Integration

### WebSocket Endpoint
```
ws://localhost:3333/api/sessions/embedded/{sessionId}/ws
```

### REST Endpoints Used

1. **GET /api/sessions/embedded/active/{taskId}**
   - Check for active session
   - Returns session metadata if exists

2. **POST /api/sessions/embedded**
   - Create new embedded session
   - Request body: `{ task_id: number, auto_start: boolean }`

## Terminal Configuration

```typescript
const terminal = new Terminal({
  theme: {
    background: '#1e1e1e',
    foreground: '#d4d4d4',
    cursor: '#ffffff',
    // ... other theme colors
  },
  fontFamily: 'Menlo, Monaco, "Courier New", monospace',
  fontSize: 14,
  cursorBlink: true,
  convertEol: true,
  scrollback: 10000,  // Extended for better history
});
```

## Usage Example

```tsx
import RealTerminal from '../components/RealTerminal';

const TaskDetailPage: React.FC = () => {
  const { taskId } = useParams();

  return (
    <Box>
      <Typography variant="h4">Task #{taskId}</Typography>
      <RealTerminal taskId={parseInt(taskId)} />
    </Box>
  );
};
```

## WebSocket Message Format

### Outgoing Messages (Client → Server)
```typescript
// User input
{ type: 'input', data: string }

// Ping
{ type: 'ping' }

// Request history on reconnect
{ type: 'request_history' }
```

### Incoming Messages (Server → Client)
```typescript
// Session output
{ type: 'output', content: string }

// History replay
{ type: 'history', content: Array<{ type: string, content: string }> }

// Pong response
{ type: 'pong' }
```

## Scroll Behavior Details

### Auto-Scroll Conditions
```typescript
// Auto-scroll ENABLED when:
- User is at the bottom of terminal (viewport === baseY)
- New content arrives from WebSocket
- Buffer is flushed

// Auto-scroll DISABLED when:
- User scrolls up manually (viewport < baseY - 1)
- User is reviewing previous output
```

### Manual Scroll Detection
```typescript
terminal.onScroll(() => {
  const viewport = terminal.buffer.active.viewportY;
  const baseY = terminal.buffer.active.baseY;

  if (viewport < baseY - 1) {
    // User scrolled up - disable auto-scroll
    isUserScrollingRef.current = true;
  } else {
    // User scrolled back down - enable auto-scroll
    isUserScrollingRef.current = false;
  }
});
```

## Buffering Strategy

### Write Buffer Management
```typescript
// Add to buffer instead of immediate write
writeBufferRef.current.push(newContent);

// Flush buffer after short delay
if (flushTimeoutRef.current) {
  clearTimeout(flushTimeoutRef.current);
}

flushTimeoutRef.current = setTimeout(() => {
  flushBuffer();
}, 100); // Batch writes every 100ms
```

### Benefits
- Reduces terminal write operations
- Prevents scroll jumping from rapid output
- Improves performance with high-frequency updates
- Maintains smooth user experience

## Session Lifecycle

### 1. Component Mount
```typescript
useEffect(() => {
  // Initialize terminal
  terminal.current = new Terminal(config);
  terminal.current.open(terminalRef.current);

  // Setup fit addon for responsive sizing
  fitAddon.current = new FitAddon();
  terminal.current.loadAddon(fitAddon.current);
  fitAddon.current.fit();

  // Check for active session
  checkActiveSession();

  return () => {
    // Cleanup on unmount
    if (flushTimeoutRef.current) {
      clearTimeout(flushTimeoutRef.current);
    }
    // Flush remaining buffer
    if (writeBufferRef.current.length > 0) {
      flushBuffer();
    }
    terminal.current?.dispose();
  };
}, [taskId]);
```

### 2. Session Connection
```typescript
const connectWebSocket = (sessionId: string) => {
  const ws = new WebSocket(`ws://localhost:3333/api/sessions/embedded/${sessionId}/ws`);

  ws.onopen = () => {
    terminal.current?.writeln('\r\nConnected to Claude');
    ws.send(JSON.stringify({ type: 'ping' }));
  };

  ws.onmessage = (event) => {
    const message = JSON.parse(event.data);

    if (message.type === 'history') {
      // Replay session history
      terminal.current?.clear();
      terminal.current?.writeln('=== Session History ===');
      message.content.forEach((msg: any) => {
        // Write each historical message
      });
    } else if (message.type === 'output') {
      // Add to buffer instead of immediate write
      writeBufferRef.current.push(message.content);

      // Schedule flush
      if (!flushTimeoutRef.current) {
        flushTimeoutRef.current = setTimeout(flushBuffer, 100);
      }
    }
  };

  ws.onerror = (error) => {
    console.error('WebSocket error:', error);
  };

  ws.onclose = () => {
    terminal.current?.writeln('\r\nDisconnected from Claude');
  };
};
```

## Performance Optimizations

### 1. Buffered Writes
- Batch multiple write operations
- Reduce terminal rendering overhead
- Prevent scroll position jumping

### 2. Extended Scrollback
- 10,000 lines vs previous 1,000
- Better session history preservation
- Minimal performance impact

### 3. Smart Auto-Scroll
- Only scroll when user is at bottom
- Respects manual scroll position
- Prevents interruption during review

### 4. Cleanup on Unmount
- Clear all timeouts
- Flush remaining buffer
- Dispose terminal properly
- Prevent memory leaks

## Styling

```tsx
<Box
  ref={terminalRef}
  sx={{
    height: '100%',
    width: '100%',
    bgcolor: '#1e1e1e',
    '& .xterm': {
      height: '100%',
      padding: 1,
    },
    '& .xterm-viewport': {
      overflow: 'auto',
    },
  }}
/>
```

## Troubleshooting

### Terminal Not Displaying
**Issue**: Terminal container is empty or not visible.

**Solution**:
- Ensure `terminalRef` is attached to a visible DOM element
- Check that container has non-zero height
- Verify xterm.css is loaded

### Auto-Scroll Not Working
**Issue**: Terminal doesn't scroll to bottom on new output.

**Solution**:
- Check `isUserScrollingRef.current` - should be `false` for auto-scroll
- Verify `flushBuffer` is being called
- Ensure buffer is not empty when flushing

### WebSocket Connection Failed
**Issue**: Cannot connect to Claude session.

**Solution**:
- Verify backend server is running on port 3333
- Check session ID is valid and active
- Review browser console for WebSocket errors

### High Memory Usage
**Issue**: Browser uses excessive memory with terminal.

**Solution**:
- Reduce scrollback from 10,000 if not needed
- Clear terminal periodically with `terminal.current.clear()`
- Dispose old terminal instances properly

## Best Practices

### 1. Cleanup Resources
Always cleanup on unmount:
```typescript
useEffect(() => {
  // ... initialization

  return () => {
    if (flushTimeoutRef.current) {
      clearTimeout(flushTimeoutRef.current);
    }
    if (writeBufferRef.current.length > 0) {
      flushBuffer();
    }
    terminal.current?.dispose();
  };
}, []);
```

### 2. Handle Reconnection
Implement automatic reconnection:
```typescript
ws.onclose = () => {
  if (!userStoppedRef.current) {
    reconnectTimeoutRef.current = setTimeout(() => {
      connectWebSocket(sessionId);
    }, 3000);
  }
};
```

### 3. Buffer Management
Always flush buffer before cleanup:
```typescript
// Flush any remaining buffered content before cleanup
if (writeBufferRef.current.length > 0) {
  flushBuffer();
}
```

## Related Components

- **ClaudeSessions** - Session management interface
- **TaskBoard** - Task management with embedded terminals
- **ClaudeTerminal** - Alternative terminal implementation

## Future Enhancements

- [ ] Terminal theme customization
- [ ] Copy/paste improvements
- [ ] Search within terminal output
- [ ] Export terminal history
- [ ] Multiple terminal tabs
- [ ] Terminal replay feature
- [ ] Performance metrics display

---

**Version**: 2.1 (WebSocket Buffering & Scroll Improvements)
**Last Updated**: 2025-11-20
**Status**: Production Ready
