export type ProviderType = "openrouter";

export type ChatMessage = {
  role: "user" | "assistant" | "tool";
  content: string;
  pending?: boolean;
};

export type ToolResult = {
  tool_name: string;
  success: boolean;
  output: string;
  structured_output?: Record<string, unknown>;
  result_type?: string;
  category?: string;
};

export type ProcessEntry = {
  type: string;
  label: string;
  detail: string;
};

export type TemplateSuggestion = {
  title: string;
  tone: string;
  content: string;
};

export type PlannerItem = {
  title: string;
  notes?: string;
  time_slot?: string | null;
  completed?: boolean;
};

export type PlannerPreview = {
  kind: string;
  title: string;
  summary: string;
  items: PlannerItem[];
  templates: TemplateSuggestion[];
  recipe: Record<string, unknown>;
};

export type AnalyticsSummary = {
  dataset_name: string;
  row_count: number;
  column_count: number;
  numeric_columns: string[];
  metrics: Record<string, { min: number; max: number; mean: number }>;
  sample_rows: Record<string, unknown>[];
  insights: string[];
};

export type VisionAnalysis = {
  filename: string;
  width: number;
  height: number;
  dominant_colors: string[];
  tags: string[];
  summary: string;
  similar_assets: string[];
};

export type QRResult = {
  mode: string;
  payload_text?: string | null;
  decoded_text?: string | null;
  image_base64?: string | null;
};

export type HomeDeviceStatus = {
  entity_id: string;
  state: string;
  area?: string | null;
  attributes: Record<string, unknown>;
};

export type HomeAssistantSummary = {
  status: string;
  endpoint?: string | null;
  devices: HomeDeviceStatus[];
  alerts: string[];
};

export type SocketEvent =
  | { type: "session.started"; payload: { session_id: string } }
  | { type: "assistant.delta"; payload: { session_id: string; delta: string } }
  | {
      type: "assistant.done";
      payload: {
        session_id: string;
        message: string;
        process_entries?: ProcessEntry[];
        structured_results?: Record<string, unknown>;
        tool_results?: ToolResult[];
      };
    }
  | { type: "intent.detected"; payload: { session_id: string; intent: string; confidence: number; labels: string[] } }
  | { type: "model.selected"; payload: { session_id: string; provider: ProviderType; model_name: string; reason: string } }
  | { type: "planner.updated"; payload: Record<string, unknown> }
  | { type: "analytics.ready"; payload: Record<string, unknown> }
  | { type: "vision.ready"; payload: Record<string, unknown> }
  | { type: "integration.status"; payload: Record<string, unknown> }
  | { type: "tool.started"; payload: { session_id: string; tool_name: string } }
  | { type: "tool.output"; payload: { session_id: string; tool_name: string; output: string } }
  | { type: "tool.done"; payload: { session_id: string; tool_name: string; success: boolean } }
  | {
      type: "system.snapshot";
      payload: {
        cpu_percent: number;
        memory_percent: number;
        available_memory_mb: number;
        running_tools: string[];
        recent_logs: string[];
      };
    }
  | { type: "error"; payload: { message: string } };

export type ChatResponse = {
  data: {
    session_id: string;
    provider: ProviderType;
    message: { role: "assistant"; content: string };
    tool_results: ToolResult[];
    memory_hits: string[];
    process_entries: ProcessEntry[];
    structured_results: Record<string, unknown>;
  };
};

export type VoiceResponse = {
  data: {
    session_id: string;
    transcript: string;
    provider: ProviderType;
    response_text: string;
    audio_base64?: string | null;
    mime_type: string;
    tool_results: ToolResult[];
    process_entries: ProcessEntry[];
    structured_results: Record<string, unknown>;
  };
};

export type SystemResponse = {
  data: {
    cpu_percent: number;
    memory_percent: number;
    available_memory_mb: number;
    running_tools: string[];
    recent_logs: string[];
  };
};

export type DatasetIngestResponse = {
  data: {
    dataset_id: number;
    dataset_name: string;
    summary: AnalyticsSummary;
  };
};

export type VisionAnalysisResponse = {
  data: VisionAnalysis;
};

export type PlannerPreviewResponse = {
  data: PlannerPreview;
};

export type QRResponse = {
  data: QRResult;
};

export type HomeAssistantResponse = {
  data: HomeAssistantSummary;
};
