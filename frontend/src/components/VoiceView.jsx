import { useState, useEffect, useRef, useCallback } from "react";
import { Mic, MicOff, Volume2 } from "lucide-react";

const API = "http://localhost:8000";

const emotionEmoji = {
  angry: "😠", frustrated: "😤", neutral: "😐",
  happy: "😊", grateful: "🙏", curious: "🤔", uninterested: "😑"
};

function scoreColor(s) {
  if (s < 0.3) return "#E5484D";
  if (s > 0.7) return "#30A46C";
  return "#F5A623";
}

/* TTS Helper */
function speakText(text, lang = "en") {
  if (!window.speechSynthesis) return null;
  window.speechSynthesis.cancel();
  const utter = new SpeechSynthesisUtterance(text);
  utter.lang = lang === "hi" ? "hi-IN" : "en-US";
  utter.rate = 0.95;
  const voices = window.speechSynthesis.getVoices();
  const match = voices.find(v => v.lang.startsWith(lang === "hi" ? "hi" : "en"));
  if (match) utter.voice = match;
  window.speechSynthesis.speak(utter);
  return utter;
}

export default function VoiceView() {
  const [state, setState] = useState("idle"); // idle | listening | processing | speaking
  const [transcript, setTranscript] = useState("");
  const [botReply, setBotReply] = useState("");
  const [sentiment, setSentiment] = useState(null);
  const [history, setHistory] = useState([]);
  const [error, setError] = useState(null);
  const [recordTime, setRecordTime] = useState(0);
  const [waveData, setWaveData] = useState(new Array(32).fill(4));

  const mediaRecRef = useRef(null);
  const chunksRef = useRef([]);
  const timerRef = useRef(null);
  const analyserRef = useRef(null);
  const animFrameRef = useRef(null);
  const streamRef = useRef(null);

  // Cleanup
  useEffect(() => {
    window.speechSynthesis?.getVoices();
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
      if (animFrameRef.current) cancelAnimationFrame(animFrameRef.current);
      streamRef.current?.getTracks().forEach(t => t.stop());
    };
  }, []);

  /* ── Waveform animation using Web Audio API ── */
  const startWaveform = (stream) => {
    try {
      const ctx = new (window.AudioContext || window.webkitAudioContext)();
      const src = ctx.createMediaStreamSource(stream);
      const analyser = ctx.createAnalyser();
      analyser.fftSize = 64;
      src.connect(analyser);
      analyserRef.current = analyser;

      const draw = () => {
        const data = new Uint8Array(analyser.frequencyBinCount);
        analyser.getByteFrequencyData(data);
        const bars = Array.from(data).slice(0, 32).map(v => Math.max(4, v / 255 * 60));
        setWaveData(bars);
        animFrameRef.current = requestAnimationFrame(draw);
      };
      draw();
    } catch (e) {
      console.error("Waveform error:", e);
    }
  };

  const stopWaveform = () => {
    if (animFrameRef.current) cancelAnimationFrame(animFrameRef.current);
    setWaveData(new Array(32).fill(4));
  };

  /* ── Recording ── */
  const toggleRecording = async () => {
    if (state === "listening") {
      // Stop
      if (mediaRecRef.current && mediaRecRef.current.state !== "inactive") {
        mediaRecRef.current.stop();
      }
      setState("processing");
      if (timerRef.current) { clearInterval(timerRef.current); timerRef.current = null; }
      stopWaveform();
      return;
    }

    // Start recording
    setError(null);
    setTranscript("");
    setBotReply("");
    setSentiment(null);

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;
      startWaveform(stream);

      const mr = new MediaRecorder(stream, { mimeType: "audio/webm" });
      chunksRef.current = [];
      mr.ondataavailable = (e) => { if (e.data.size > 0) chunksRef.current.push(e.data); };
      mr.onstop = async () => {
        stream.getTracks().forEach(t => t.stop());
        const blob = new Blob(chunksRef.current, { type: "audio/webm" });
        await processVoice(blob);
      };
      mr.start();
      mediaRecRef.current = mr;
      setState("listening");
      setRecordTime(0);
      timerRef.current = setInterval(() => setRecordTime(t => t + 1), 1000);
    } catch (err) {
      console.error("Mic error:", err);
      setError("Microphone access denied. Please allow mic permission in your browser settings.");
      setState("idle");
    }
  };

  /* ── Full voice pipeline ── */
  const processVoice = async (blob) => {
    try {
      const formData = new FormData();
      formData.append("file", blob, "recording.webm");

      const res = await fetch(`${API}/voice/process`, { method: "POST", body: formData });
      const data = await res.json();

      if (data.error && !data.transcript) {
        setError(data.error || "Voice processing failed.");
        setState("idle");
        return;
      }

      setTranscript(data.transcript);
      setSentiment(data.sentiment);
      setBotReply(data.bot_reply);

      // Add to history
      setHistory(prev => [...prev, {
        user: data.transcript,
        bot: data.bot_reply,
        sentiment: data.sentiment,
        language: data.language,
        timestamp: new Date().toLocaleTimeString()
      }]);

      // Speak bot reply
      setState("speaking");
      const utter = speakText(data.bot_reply, data.language);
      if (utter) {
        utter.onend = () => setState("idle");
      } else {
        setTimeout(() => setState("idle"), 1000);
      }
    } catch (err) {
      console.error("Process error:", err);
      setError("Voice processing failed. Please try again.");
      setState("idle");
    }
  };

  const fmtTime = (s) => `${Math.floor(s / 60).toString().padStart(2, "0")}:${(s % 60).toString().padStart(2, "0")}`;

  const stateLabel = {
    idle: "Tap to speak",
    listening: "Listening...",
    processing: "Processing...",
    speaking: "Speaking..."
  };

  return (
    <div className="voice-view">

      {/* Main Voice Area */}
      <div className="voice-main">
        <h2 className="voice-title">Voice Assistant</h2>
        <p className="voice-subtitle">Tap the microphone and speak — I'll analyze your sentiment and respond</p>

        {/* Big Mic Button */}
        <div className="voice-mic-area">
          {/* Waveform */}
          <div className={`voice-waveform ${state === "listening" ? "active" : ""}`}>
            {waveData.map((h, i) => (
              <div key={i} className="wave-bar" style={{ height: `${h}px`, animationDelay: `${i * 20}ms` }} />
            ))}
          </div>

          <button
            className={`voice-mic-btn ${state}`}
            onClick={toggleRecording}
            disabled={state === "processing"}
          >
            {state === "listening" ? <MicOff size={36} /> : state === "speaking" ? <Volume2 size={36} /> : <Mic size={36} />}
            {state === "listening" && <span className="voice-pulse-ring" />}
            {state === "listening" && <span className="voice-pulse-ring delay" />}
          </button>

          <div className="voice-state-label">{stateLabel[state]}</div>
          {state === "listening" && <div className="voice-rec-time">{fmtTime(recordTime)}</div>}
        </div>

        {/* Processing Skeleton */}
        {state === "processing" && (
          <div className="voice-processing">
            <div className="voice-processing-bars">
              <span /><span /><span /><span /><span />
            </div>
            <p>Transcribing and analyzing...</p>
          </div>
        )}

        {/* Transcript */}
        {transcript && (
          <div className="voice-transcript fade-in">
            <div className="voice-transcript-label">You said:</div>
            <div className="voice-transcript-text">"{transcript}"</div>
            {sentiment && (
              <div className="voice-sentiment-badges">
                <span className="voice-badge" style={{ color: scoreColor(sentiment.score) }}>
                  Score: {sentiment.score?.toFixed(2)}
                </span>
                <span className="voice-badge">
                  {emotionEmoji[sentiment.emotion]} {sentiment.emotion}
                </span>
                <span className="voice-badge" style={{
                  color: sentiment.action === "ESCALATE" ? "#E5484D" : sentiment.action === "UPSELL" ? "#30A46C" : "#A0A0A0"
                }}>
                  {sentiment.action}
                </span>
              </div>
            )}
          </div>
        )}

        {/* Bot Reply */}
        {botReply && (
          <div className="voice-reply fade-in">
            <div className="voice-reply-label">
              {state === "speaking" && (
                <span className="speaking-bars-sm"><span /><span /><span /><span /></span>
              )}
              Bot replied:
            </div>
            <div className="voice-reply-text">{botReply}</div>
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="voice-error fade-in">
            ⚠️ {error}
            <button onClick={() => setError(null)}>✕</button>
          </div>
        )}
      </div>

      {/* History Panel */}
      <div className="voice-history">
        <h3 className="voice-history-title">Conversation History</h3>
        {history.length === 0 ? (
          <div className="voice-history-empty">No conversations yet. Tap the mic to begin!</div>
        ) : (
          <div className="voice-history-list">
            {[...history].reverse().map((h, i) => (
              <div key={i} className="voice-history-item fade-in">
                <div className="voice-history-time">{h.timestamp}</div>
                <div className="voice-history-user">
                  <span className="voice-history-role">You:</span> {h.user}
                </div>
                <div className="voice-history-bot">
                  <span className="voice-history-role">Bot:</span> {h.bot}
                </div>
                {h.sentiment && (
                  <div className="voice-history-meta">
                    <span style={{ color: scoreColor(h.sentiment.score) }}>{h.sentiment.score?.toFixed(2)}</span>
                    <span>{emotionEmoji[h.sentiment.emotion]} {h.sentiment.emotion}</span>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
