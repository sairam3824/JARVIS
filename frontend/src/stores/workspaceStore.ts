import { create } from "zustand";
import type { AnalyticsSummary, HomeAssistantSummary, PlannerPreview, ProcessEntry, QRResult, TemplateSuggestion, VisionAnalysis } from "@/types/api";

type WorkspaceState = {
  processEntries: ProcessEntry[];
  analyticsSummary?: AnalyticsSummary;
  visionAnalysis?: VisionAnalysis;
  plannerPreview?: PlannerPreview;
  qrResult?: QRResult;
  homeStatus?: HomeAssistantSummary;
  templates: TemplateSuggestion[];
  pushProcessEntry: (entry: ProcessEntry) => void;
  setAnalyticsSummary: (summary: AnalyticsSummary) => void;
  setVisionAnalysis: (analysis: VisionAnalysis) => void;
  setPlannerPreview: (preview: PlannerPreview) => void;
  setQrResult: (result: QRResult) => void;
  setHomeStatus: (status: HomeAssistantSummary) => void;
  appendTemplates: (templates: TemplateSuggestion[]) => void;
};

export const useWorkspaceStore = create<WorkspaceState>((set) => ({
  processEntries: [],
  templates: [],
  pushProcessEntry: (entry) =>
    set((state) => ({
      processEntries: [entry, ...state.processEntries].slice(0, 14),
    })),
  setAnalyticsSummary: (summary) => set({ analyticsSummary: summary }),
  setVisionAnalysis: (analysis) => set({ visionAnalysis: analysis }),
  setPlannerPreview: (preview) =>
    set((state) => ({
      plannerPreview: preview,
      templates: preview.templates.length ? [...preview.templates, ...state.templates].slice(0, 8) : state.templates,
    })),
  setQrResult: (result) => set({ qrResult: result }),
  setHomeStatus: (status) => set({ homeStatus: status }),
  appendTemplates: (templates) =>
    set((state) => ({
      templates: [...templates, ...state.templates].slice(0, 8),
    })),
}));
