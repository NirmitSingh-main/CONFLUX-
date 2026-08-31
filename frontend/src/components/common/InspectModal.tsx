import { useState } from "react";
import { X, Copy, Check, Terminal, ExternalLink } from "lucide-react";
import { useMission } from "../../context/MissionContext";

export function InspectModal() {
  const { inspectPayload, setInspectPayload } = useMission();
  const [copied, setCopied] = useState(false);

  if (!inspectPayload) return null;

  const jsonString = JSON.stringify(inspectPayload.data, null, 2);

  const handleCopy = () => {
    navigator.clipboard.writeText(jsonString);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-md animate-in fade-in duration-200">
      <div className="relative w-full max-w-3xl max-h-[85vh] flex flex-col bg-theme-card border border-theme-subtle rounded-2xl shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-3.5 border-b border-theme-subtle bg-theme-card-sub">
          <div className="flex items-center gap-2.5">
            <div className="p-1.5 rounded-lg bg-theme-cyan-subtle border border-theme-cyan text-[#00D1FF]">
              <Terminal className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-sm font-mono font-semibold text-theme-primary uppercase tracking-wider">
                {inspectPayload.title}
              </h3>
              <p className="text-[11px] text-theme-muted font-mono">
                Level 3 Raw API JSON Response Output
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              id="copy-json-payload-btn"
              onClick={handleCopy}
              className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-mono rounded-xl bg-theme-card hover:bg-theme-card-hover text-theme-primary border border-theme-subtle transition-colors"
            >
              {copied ? (
                <>
                  <Check className="w-3.5 h-3.5 text-emerald-500" />
                  <span className="text-emerald-500">Copied</span>
                </>
              ) : (
                <>
                  <Copy className="w-3.5 h-3.5 text-theme-muted" />
                  <span>Copy JSON</span>
                </>
              )}
            </button>
            <button
              id="close-inspect-modal-btn"
              onClick={() => setInspectPayload(null)}
              className="p-1.5 text-theme-muted hover:text-theme-primary hover:bg-theme-card-hover rounded-lg transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* JSON Content */}
        <div className="p-5 overflow-auto flex-1 font-mono text-xs text-theme-primary bg-theme-input leading-relaxed selection:bg-cyan-500/20">
          <pre className="font-mono">{jsonString}</pre>
        </div>

        {/* Footer */}
        <div className="px-5 py-2.5 border-t border-theme-subtle bg-theme-card-sub flex items-center justify-between text-[11px] text-theme-muted font-mono">
          <div className="flex items-center gap-1.5">
            <ExternalLink className="w-3 h-3 text-[#00D1FF]" />
            <span>FastAPI Direct Endpoint Output</span>
          </div>
          <span>Stored in DB: {String(inspectPayload.data?.stored_in_database ?? "N/A")}</span>
        </div>
      </div>
    </div>
  );
}
