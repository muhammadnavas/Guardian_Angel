export default function ResultCard({ result, onNewScan }) {
    if (!result) return null;
    const { verdict, confidence, summary, scamPatterns } = result;
    const isScam = verdict === 'scam';

    return (
        <div
            className={`rounded-2xl p-10 text-center animate-fade-in-up border ${isScam
                    ? 'bg-gradient-to-br from-danger/[0.08] to-danger/[0.02] border-danger/30 shadow-[0_0_40px_rgba(239,68,68,0.08)]'
                    : 'bg-gradient-to-br from-safe/[0.08] to-safe/[0.02] border-safe/30 shadow-[0_0_40px_rgba(16,185,129,0.08)]'
                }`}
        >
            <span className="text-6xl block mb-4">{isScam ? '🚨' : '✅'}</span>
            <div className={`font-heading text-4xl font-extrabold mb-2 ${isScam ? 'text-danger' : 'text-safe'}`}>
                {isScam ? 'Scam Detected' : 'Looks Safe'}
            </div>

            {/* Confidence bar */}
            <div className="mx-auto max-w-[320px] my-6">
                <div className="flex justify-between mb-2 text-sm text-gray-400">
                    <span>Confidence Level</span>
                    <span>{confidence}/5</span>
                </div>
                <div className="h-2.5 bg-white/[0.08] rounded-full overflow-hidden">
                    <div
                        className={`h-full rounded-full transition-[width] duration-1000 ${isScam
                                ? 'bg-gradient-to-r from-danger to-orange-500'
                                : 'bg-gradient-to-r from-safe to-emerald-400'
                            }`}
                        style={{ width: `${(confidence / 5) * 100}%` }}
                    />
                </div>
            </div>

            {/* Summary */}
            <div className="mt-8 p-6 bg-white/[0.04] rounded-xl border border-white/[0.08] text-left">
                <h4 className="text-base text-gray-400 font-medium mb-2">📋 Analysis Summary</h4>
                <p className="text-lg leading-relaxed">{summary}</p>
            </div>

            {/* Scam patterns */}
            {isScam && scamPatterns?.length > 0 && (
                <div className="mt-6 text-left">
                    <h4 className="text-base text-gray-400 font-medium mb-3">⚠️ Detected Patterns</h4>
                    <ul className="flex flex-wrap gap-2 list-none">
                        {scamPatterns.map((pattern, i) => (
                            <li
                                key={i}
                                className="px-3.5 py-1.5 text-sm font-medium rounded-full text-danger bg-danger/12 border border-danger/20"
                            >
                                {pattern}
                            </li>
                        ))}
                    </ul>
                </div>
            )}

            {/* Actions */}
            <div className="mt-8 flex gap-4 justify-center flex-wrap">
                <button
                    className="inline-flex items-center gap-2 px-8 py-3.5 text-base font-semibold rounded-full bg-gradient-to-br from-primary to-primary-light text-white btn-glow hover:-translate-y-0.5 transition-all duration-250 cursor-pointer"
                    onClick={onNewScan}
                >
                    🔍 Scan Another
                </button>
                <button
                    className="inline-flex items-center gap-2 px-8 py-3.5 text-base font-semibold rounded-full bg-transparent text-white border-[1.5px] border-white/15 hover:border-primary-light hover:text-primary-light hover:bg-primary-light/5 transition-all duration-250 cursor-pointer"
                    onClick={() => window.print()}
                >
                    🖨️ Print Report
                </button>
            </div>
        </div>
    );
}
