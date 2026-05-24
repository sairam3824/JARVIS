import { useState } from "react";
import { QrCode, ScanLine } from "lucide-react";
import { runQr } from "@/services/api";
import { useWorkspaceStore } from "@/stores/workspaceStore";
import { GlowingButton } from "@/components/ui/GlowingButton";

export function QrLab() {
  const [payloadText, setPayloadText] = useState("https://openai.com");
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const qrResult = useWorkspaceStore((state) => state.qrResult);
  const setQrResult = useWorkspaceStore((state) => state.setQrResult);
  const pushProcessEntry = useWorkspaceStore((state) => state.pushProcessEntry);

  async function handleGenerate() {
    setLoading(true);
    try {
      const result = await runQr("generate", payloadText);
      setQrResult(result);
      pushProcessEntry({ type: "qr.generate", label: "QR generated", detail: payloadText });
    } catch (error) {
      pushProcessEntry({ type: "error", label: "QR Generate", detail: String(error) });
    } finally {
      setLoading(false);
    }
  }

  async function handleScan() {
    if (!file) return;
    setLoading(true);
    try {
      const result = await runQr("scan", undefined, file);
      setQrResult(result);
      pushProcessEntry({ type: "qr.scan", label: "QR scanned", detail: result.decoded_text || "No QR detected" });
    } catch (error) {
      pushProcessEntry({ type: "error", label: "QR Scan", detail: String(error) });
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-4">
      <input
        value={payloadText}
        onChange={(event) => setPayloadText(event.target.value)}
        className="rounded-[18px] border border-white/10 bg-white/5 px-4 py-3 font-body text-slate-100"
        placeholder="Text or link for QR generation"
      />
      <div className="grid gap-3 md:grid-cols-2">
        <GlowingButton onClick={handleGenerate} disabled={loading}>
          <QrCode className="mr-2 inline h-4 w-4" />
          Generate
        </GlowingButton>
        <label className="flex cursor-pointer items-center justify-center gap-2 rounded-full border border-white/10 bg-white/5 px-5 py-3 font-body text-sm uppercase tracking-[0.2em] text-slate-300">
          <ScanLine className="h-4 w-4" />
          {file ? file.name : "Upload to Scan"}
          <input type="file" accept="image/*" className="hidden" onChange={(event) => setFile(event.target.files?.[0] ?? null)} />
        </label>
      </div>
      <GlowingButton onClick={handleScan} disabled={!file || loading} className="w-full">
        Scan Uploaded QR
      </GlowingButton>
      {qrResult ? (
        <div className="rounded-[20px] border border-white/10 bg-black/20 p-4">
          {qrResult.image_base64 ? (
            <img alt="Generated QR" className="mx-auto h-40 w-40 rounded-[18px] border border-white/10 bg-white p-3" src={`data:image/png;base64,${qrResult.image_base64}`} />
          ) : null}
          <p className="mt-3 font-body text-sm text-slate-300">{qrResult.decoded_text || qrResult.payload_text || "QR result ready."}</p>
        </div>
      ) : null}
    </div>
  );
}

