import type {
  ChatResponse,
  DatasetIngestResponse,
  HomeAssistantResponse,
  PlannerPreviewResponse,
  ProviderType,
  QRResponse,
  SystemResponse,
  VisionAnalysisResponse,
  VoiceResponse,
} from "@/types/api";

const API_BASE = import.meta.env.VITE_API_BASE ?? "http://localhost:8000";

async function assertOk(response: Response): Promise<void> {
  if (!response.ok) {
    const text = await response.text().catch(() => "");
    throw new Error(`API error ${response.status}: ${text}`);
  }
}

export async function fetchSystem(): Promise<SystemResponse["data"]> {
  const response = await fetch(`${API_BASE}/system`);
  await assertOk(response);
  const payload: SystemResponse = await response.json();
  return payload.data;
}

export async function sendChat(prompt: string, provider: ProviderType, sessionId?: string) {
  const response = await fetch(`${API_BASE}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      prompt,
      provider,
      session_id: sessionId,
    }),
  });
  await assertOk(response);
  const payload: ChatResponse = await response.json();
  return payload.data;
}

export async function sendVoice(file: Blob, provider: ProviderType, sessionId?: string) {
  const formData = new FormData();
  formData.append("file", file, "jarvis-recording.webm");
  formData.append("provider", provider);
  if (sessionId) {
    formData.append("session_id", sessionId);
  }
  const response = await fetch(`${API_BASE}/voice`, {
    method: "POST",
    body: formData,
  });
  await assertOk(response);
  const payload: VoiceResponse = await response.json();
  return payload.data;
}

export async function ingestDataset(options: {
  datasetName: string;
  kind: string;
  content?: string;
  file?: File | null;
}) {
  const formData = new FormData();
  formData.append("dataset_name", options.datasetName);
  formData.append("kind", options.kind);
  if (options.content) {
    formData.append("content", options.content);
  }
  if (options.file) {
    formData.append("file", options.file, options.file.name);
  }
  const response = await fetch(`${API_BASE}/ingest/data`, {
    method: "POST",
    body: formData,
  });
  await assertOk(response);
  const payload: DatasetIngestResponse = await response.json();
  return payload.data;
}

export async function analyzeVision(file: File) {
  const formData = new FormData();
  formData.append("file", file, file.name);
  const response = await fetch(`${API_BASE}/vision/analyze`, {
    method: "POST",
    body: formData,
  });
  await assertOk(response);
  const payload: VisionAnalysisResponse = await response.json();
  return payload.data;
}

export async function previewPlanner(kind: string, objective: string, sessionId?: string, context: Record<string, unknown> = {}) {
  const response = await fetch(`${API_BASE}/planner/preview`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      kind,
      objective,
      session_id: sessionId,
      context,
    }),
  });
  await assertOk(response);
  const payload: PlannerPreviewResponse = await response.json();
  return payload.data;
}

export async function runQr(mode: "generate" | "scan", payloadText?: string, file?: File | null) {
  const formData = new FormData();
  formData.append("mode", mode);
  if (payloadText) {
    formData.append("payload_text", payloadText);
  }
  if (file) {
    formData.append("file", file, file.name);
  }
  const response = await fetch(`${API_BASE}/qr`, {
    method: "POST",
    body: formData,
  });
  await assertOk(response);
  const payload: QRResponse = await response.json();
  return payload.data;
}

export async function fetchHomeAssistantStatus() {
  const response = await fetch(`${API_BASE}/integrations/home-assistant/status`);
  await assertOk(response);
  const payload: HomeAssistantResponse = await response.json();
  return payload.data;
}

export function chatSocketUrl() {
  const base = API_BASE.replace(/^http/, "ws");
  return `${base}/ws/chat`;
}

export function systemSocketUrl() {
  const base = API_BASE.replace(/^http/, "ws");
  return `${base}/ws/system`;
}
