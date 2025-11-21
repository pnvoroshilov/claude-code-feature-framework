# Advanced Pattern 3: WebSocket Integration

Real-time bidirectional communication with React.

## Implementation

```typescript
// src/hooks/useWebSocket.ts
import { useEffect, useRef, useState } from 'react';

export function useWebSocket(url: string) {
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<any>(null);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    const ws = new WebSocket(url);

    ws.onopen = () => setIsConnected(true);
    ws.onmessage = (event) => setLastMessage(JSON.parse(event.data));
    ws.onclose = () => setIsConnected(false);

    wsRef.current = ws;

    return () => ws.close();
  }, [url]);

  const send = (data: any) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(data));
    }
  };

  return { isConnected, lastMessage, send };
}

// Usage
function Chat() {
  const { isConnected, lastMessage, send } = useWebSocket('ws://localhost:8000/ws');

  return (
    <div>
      Status: {isConnected ? 'Connected' : 'Disconnected'}
      <button onClick={() => send({ text: 'Hello' })}>Send</button>
    </div>
  );
}
```

FastAPI Backend:
```python
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Echo: {data}")
```

See: [docs/advanced-topics.md](../../docs/advanced-topics.md#websocket-integration)
