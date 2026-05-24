import { useEffect, useRef, useState } from "react";

export function useVoiceCapture() {
  const [isRecording, setIsRecording] = useState(false);
  const [levels, setLevels] = useState<number[]>(Array.from({ length: 32 }, () => 0.18));
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const chunksRef = useRef<BlobPart[]>([]);
  const rafRef = useRef<number>();

  useEffect(
    () => () => {
      if (rafRef.current) cancelAnimationFrame(rafRef.current);
      audioContextRef.current?.close();
      streamRef.current?.getTracks().forEach((track) => track.stop());
    },
    [],
  );

  async function startRecording() {
    let stream: MediaStream;
    try {
      stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    } catch {
      return;
    }
    const audioContext = new AudioContext();
    const analyser = audioContext.createAnalyser();
    analyser.fftSize = 64;
    const source = audioContext.createMediaStreamSource(stream);
    source.connect(analyser);

    const mediaRecorder = new MediaRecorder(stream);
    chunksRef.current = [];
    mediaRecorder.ondataavailable = (event) => {
      if (event.data.size > 0) chunksRef.current.push(event.data);
    };
    mediaRecorder.start();

    streamRef.current = stream;
    mediaRecorderRef.current = mediaRecorder;
    analyserRef.current = analyser;
    audioContextRef.current = audioContext;
    setIsRecording(true);
    animateWaveform();
  }

  async function stopRecording() {
    const mediaRecorder = mediaRecorderRef.current;
    if (!mediaRecorder) return null;
    return new Promise<Blob | null>((resolve) => {
      mediaRecorder.onstop = () => {
        if (rafRef.current) {
          cancelAnimationFrame(rafRef.current);
          rafRef.current = undefined;
        }
        const blob = new Blob(chunksRef.current, { type: "audio/webm" });
        setIsRecording(false);
        setLevels(Array.from({ length: 32 }, () => 0.18));
        resolve(blob);
        streamRef.current?.getTracks().forEach((track) => track.stop());
        audioContextRef.current?.close();
      };
      mediaRecorder.stop();
    });
  }

  function animateWaveform() {
    const analyser = analyserRef.current;
    if (!analyser) return;
    const data = new Uint8Array(analyser.frequencyBinCount);
    const frame = () => {
      analyser.getByteFrequencyData(data);
      setLevels(Array.from(data).map((value) => Math.max(value / 255, 0.12)));
      rafRef.current = requestAnimationFrame(frame);
    };
    frame();
  }

  return { isRecording, levels, startRecording, stopRecording };
}

