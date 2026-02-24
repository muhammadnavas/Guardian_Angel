import { useState, useCallback } from 'react';
import FileUpload from '../components/FileUpload';
import AgentPipeline from '../components/AgentPipeline';
import ResultCard from '../components/ResultCard';
import { analyzeScan } from '../api/scanService';

const EXAMPLE_LABELS = [
    'Gift Scam (EN)', 'Banking Scam (ES)', 'Billing SMS', 'MFA Email',
    'Twitter Scam', 'Landscape (Safe)', 'Opera Ticket (FR)',
];

export default function Scan() {
    const [selectedFile, setSelectedFile] = useState(null);
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [activeAgent, setActiveAgent] = useState(-1);
    const [completedAgents, setCompletedAgents] = useState([]);
    const [result, setResult] = useState(null);
    const [showResult, setShowResult] = useState(false);

    const handleFileSelect = useCallback((file) => {
        setSelectedFile(file);
        setResult(null);
        setShowResult(false);
        setActiveAgent(-1);
        setCompletedAgents([]);
    }, []);

    const handleScan = useCallback(async () => {
        if (!selectedFile) return;
        setIsAnalyzing(true);
        setResult(null);
        setShowResult(false);
        setCompletedAgents([]);
        setActiveAgent(0);

        try {
            const finalResult = await analyzeScan(selectedFile, (update) => {
                setCompletedAgents((prev) => [...prev, update.agentIndex]);
                setActiveAgent(update.agentIndex + 1);
            });
            setActiveAgent(-1);
            setResult(finalResult);
            setShowResult(true);
        } catch (error) {
            console.error('Scan error:', error);
        } finally {
            setIsAnalyzing(false);
        }
    }, [selectedFile]);

    const handleNewScan = useCallback(() => {
        setSelectedFile(null);
        setResult(null);
        setShowResult(false);
        setActiveAgent(-1);
        setCompletedAgents([]);
    }, []);

    return (
        <div className="pt-24 min-h-screen">
            <div className="max-w-[1200px] mx-auto px-6">
                {/* Header */}
                <div className="text-center mb-10 animate-fade-in-up">
                    <h1 className="text-3xl md:text-4xl font-bold mb-2">
                        🔍 Scan for <span className="gradient-text">Scams</span>
                    </h1>
                    <p className="text-lg text-gray-400">Upload a screenshot of any suspicious message to analyze it</p>
                </div>

                {showResult && result ? (
                    <ResultCard result={result} onNewScan={handleNewScan} />
                ) : (
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-10 items-start">
                        {/* Left: Upload */}
                        <div className="animate-fade-in-up" style={{ animationDelay: '0.1s', opacity: 0 }}>
                            <FileUpload onFileSelect={handleFileSelect} disabled={isAnalyzing} />

                            <div className="mt-6 text-center">
                                <button
                                    className={`w-full inline-flex items-center justify-center gap-2 px-6 py-4 text-lg font-semibold rounded-full transition-all duration-250 cursor-pointer ${!selectedFile || isAnalyzing
                                            ? 'bg-gray-700 text-gray-400 cursor-not-allowed'
                                            : 'bg-gradient-to-br from-primary to-primary-light text-white btn-glow hover:-translate-y-0.5'
                                        }`}
                                    onClick={handleScan}
                                    disabled={!selectedFile || isAnalyzing}
                                >
                                    {isAnalyzing ? '⏳ Analyzing...' : '🛡️ Analyze for Scams'}
                                </button>
                            </div>

                            {/* Examples */}
                            <div className="mt-10">
                                <h3 className="text-lg text-gray-400 font-medium mb-4">📁 Try an Example</h3>
                                <div className="grid grid-cols-3 sm:grid-cols-4 gap-2">
                                    {EXAMPLE_LABELS.map((label, i) => (
                                        <div
                                            key={i}
                                            className="aspect-square rounded-xl border-2 border-white/[0.08] bg-surface flex items-center justify-center text-xs text-gray-500 text-center p-1.5 cursor-pointer hover:border-primary-light hover:scale-105 transition-all duration-150"
                                        >
                                            {label}
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </div>

                        {/* Right: Pipeline */}
                        <div className="animate-fade-in-up" style={{ animationDelay: '0.2s', opacity: 0 }}>
                            <div className="glass-card p-7">
                                <h3 className="text-lg font-bold mb-5 flex items-center gap-2">⚙️ Agent Pipeline</h3>
                                {isAnalyzing || completedAgents.length > 0 ? (
                                    <AgentPipeline activeIndex={activeAgent} completedAgents={completedAgents} />
                                ) : (
                                    <div className="text-center py-12 text-gray-400">
                                        <span className="text-5xl block mb-4">🛡️</span>
                                        Upload an image and click <strong className="text-white">Analyze</strong> to start the multi-agent pipeline
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
