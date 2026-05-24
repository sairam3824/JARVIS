import { create } from "zustand";
import type { ProviderType } from "@/types/api";

type SettingsState = {
  autoPlayVoice: boolean;
  provider: ProviderType;
  setAutoPlayVoice: (value: boolean) => void;
  setProvider: (provider: ProviderType) => void;
};

export const useSettingsStore = create<SettingsState>((set) => ({
  autoPlayVoice: true,
  provider: "openrouter",
  setAutoPlayVoice: (value) => set({ autoPlayVoice: value }),
  setProvider: (provider) => set({ provider }),
}));
