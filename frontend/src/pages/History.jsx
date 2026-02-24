import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { getHistory } from '../api/scanService';

export default function History() {
    const [history, setHistory] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        getHistory().then((data) => {
            setHistory(data);
            setLoading(false);
        });
    }, []);

    return (
        <div className="pt-24 min-h-screen">
            <div className="max-w-[1200px] mx-auto px-6">
                <div className="text-center mb-10 animate-fade-in-up">
                    <h1 className="text-3xl md:text-4xl font-bold mb-2">
                        📊 Scan <span className="gradient-text">History</span>
                    </h1>
                    <p className="text-lg text-gray-400">Review past scan results and analysis records</p>
                </div>

                {loading ? (
                    <div className="text-center py-16 text-gray-500">
                        <span className="text-5xl block mb-4">⏳</span>
                        <p>Loading history...</p>
                    </div>
                ) : history.length === 0 ? (
                    <div className="text-center py-16 text-gray-500">
                        <span className="text-5xl block mb-4">📭</span>
                        <p>No scans yet. Start by scanning a screenshot.</p>
                        <Link
                            to="/scan"
                            className="inline-flex items-center gap-2 mt-4 px-6 py-3 text-base font-semibold rounded-full bg-gradient-to-br from-primary to-primary-light text-white btn-glow no-underline"
                        >
                            🔍 Go to Scan
                        </Link>
                    </div>
                ) : (
                    <div className="flex flex-col gap-3.5">
                        {history.map((item, i) => (
                            <div
                                key={item.id}
                                className="glass-card hover:glass-card-hover grid grid-cols-[auto_1fr_auto] max-md:grid-cols-[auto_1fr] gap-5 p-5 md:px-7 items-center animate-fade-in-up"
                                style={{ animationDelay: `${i * 0.1}s`, opacity: 0 }}
                            >
                                {/* Verdict icon */}
                                <div
                                    className={`w-[50px] h-[50px] rounded-full flex items-center justify-center text-2xl ${item.verdict === 'scam'
                                            ? 'bg-danger/12 border border-danger/30'
                                            : 'bg-safe/12 border border-safe/30'
                                        }`}
                                >
                                    {item.verdict === 'scam' ? '🚨' : '✅'}
                                </div>

                                {/* Content */}
                                <div>
                                    <h4 className={`text-base font-semibold mb-0.5 ${item.verdict === 'scam' ? 'text-danger' : 'text-safe'}`}>
                                        {item.verdict === 'scam' ? 'Scam Detected' : 'Safe Message'}
                                    </h4>
                                    <p className="text-sm text-gray-400 leading-relaxed">{item.summary}</p>
                                </div>

                                {/* Meta */}
                                <div className="flex flex-col items-end gap-1 max-md:flex-row max-md:items-center max-md:col-span-2 max-md:gap-4">
                                    <span className="text-sm text-gray-500">{item.date} · {item.time}</span>
                                    <span className="text-sm font-medium px-2.5 py-0.5 rounded-full bg-white/[0.04] border border-white/[0.08]">
                                        Confidence: {item.confidence}/5
                                    </span>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}
