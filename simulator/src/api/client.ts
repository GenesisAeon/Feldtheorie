export interface LiveAnalyzePayload {
  samples?: number;
  runId?: string;
}

export interface LiveAnalyzeResponse {
  run_id: string;
  status: string;
  samples: number;
}

export type TelemetryMessageType =
  | 'start'
  | 'log'
  | 'progress'
  | 'beta_estimate'
  | 'complete'
  | 'error';

export interface TelemetryMessage {
  type: TelemetryMessageType;
  run_id: string;
  message?: string;
  source?: 'stdout' | 'stderr';
  beta?: number;
  current?: number;
  total?: number;
  return_code?: number;
  samples?: number;
  script?: string;
}

const normalizeBaseUrl = (baseUrl?: string): string => {
  if (!baseUrl) {
    return '';
  }
  return baseUrl.endsWith('/') ? baseUrl.slice(0, -1) : baseUrl;
};

const buildWebSocketUrl = (baseUrl?: string): string => {
  const base = normalizeBaseUrl(baseUrl || (typeof window !== 'undefined' ? window.location.origin : ''));
  const wsBase = base.startsWith('ws') ? base : base.replace(/^http/, 'ws');
  return `${wsBase}/ws/telemetry`;
};

export const startLiveAnalysis = async (
  payload: LiveAnalyzePayload = {},
  baseUrl?: string,
): Promise<LiveAnalyzeResponse> => {
  const body = {
    samples: payload.samples ?? 1,
    ...(payload.runId ? { run_id: payload.runId } : {}),
  };

  const response = await fetch(`${normalizeBaseUrl(baseUrl)}/api/analyze/live`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    const message = await response.text();
    throw new Error(`Failed to start live analysis: ${response.status} ${message}`);
  }

  return response.json();
};

export const openTelemetryStream = (
  onMessage: (message: TelemetryMessage) => void,
  baseUrl?: string,
): WebSocket => {
  const ws = new WebSocket(buildWebSocketUrl(baseUrl));

  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data) as TelemetryMessage;
      onMessage(data);
    } catch (error) {
      console.error('Telemetry parse error', error);
    }
  };

  return ws;
};
