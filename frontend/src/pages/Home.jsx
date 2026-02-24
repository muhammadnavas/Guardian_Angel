import { Link } from 'react-router-dom';
import { getAgentsList } from '../api/scanService';

export default function Home() {
    const agents = getAgentsList();

    return (
        <div>
            {/* Hero */}
            <section className="min-h-[90vh] flex items-center pt-20 relative overflow-hidden">
                {/* Background glow */}
                <div className="absolute -top-[20%] -right-[10%] w-[600px] h-[600px] bg-[radial-gradient(circle,rgba(99,102,241,0.25),transparent_70%)] rounded-full pointer-events-none animate-float" />

                <div className="max-w-[1200px] mx-auto px-6">
                    <div className="max-w-[700px] animate-fade-in-up">
                        <div className="inline-flex items-center gap-2 px-4 py-1.5 text-sm font-medium rounded-full bg-primary-light/10 border border-primary-light/20 text-primary-light mb-6">
                            🤖 Powered by 7 AI Agents — AgentX Hackathon 2026
                        </div>

                        <h1 className="text-5xl md:text-6xl font-extrabold leading-[1.1] mb-6">
                            Your <span className="gradient-text">Guardian Angel</span> Against Digital Scams
                        </h1>

                        <p className="text-xl text-gray-400 leading-relaxed mb-8 max-w-[560px]">
                            Protecting senior citizens from phishing, fraud, and social engineering attacks with an autonomous multi-agent AI system.
                        </p>

                        <div className="flex gap-4 flex-wrap">
                            <Link
                                to="/scan"
                                className="inline-flex items-center gap-2 px-8 py-4 text-lg font-semibold rounded-full bg-gradient-to-br from-primary to-primary-light text-white btn-glow hover:-translate-y-0.5 transition-all duration-250 no-underline"
                            >
                                🔍 Scan a Screenshot
                            </Link>
                            <Link
                                to="/about"
                                className="inline-flex items-center gap-2 px-8 py-4 text-lg font-semibold rounded-full bg-transparent text-white border-[1.5px] border-white/15 hover:border-primary-light hover:text-primary-light transition-all duration-250 no-underline"
                            >
                                Learn More
                            </Link>
                        </div>
                    </div>
                </div>
            </section>

            {/* Stats */}
            <section className="py-10">
                <div className="max-w-[1200px] mx-auto px-6">
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-5">
                        {[
                            { value: '88.3%', label: 'Detection Accuracy', color: 'text-primary-light' },
                            { value: '7', label: 'Specialized Agents', color: 'text-accent' },
                            { value: 'Multi', label: 'Language Support', color: 'text-safe' },
                            { value: 'Real-time', label: 'Streaming Analysis', color: 'text-primary-light' },
                        ].map((stat) => (
                            <div key={stat.label} className="glass-card hover:glass-card-hover p-7 text-center">
                                <div className={`font-heading text-3xl font-extrabold mb-1 ${stat.color}`}>{stat.value}</div>
                                <div className="text-sm text-gray-400">{stat.label}</div>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* How it Works */}
            <section className="py-16">
                <div className="max-w-[1200px] mx-auto px-6">
                    <h2 className="text-center text-3xl font-bold mb-2">How It <span className="gradient-text">Works</span></h2>
                    <p className="text-center text-lg text-gray-400 mb-10">Three simple steps to protect yourself from digital scams</p>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
                        {[
                            { icon: '📸', title: '1. Upload Screenshot', desc: 'Take a screenshot of the suspicious message — email, SMS, social media, or any digital communication.' },
                            { icon: '🤖', title: '2. AI Agents Analyze', desc: 'Seven specialized AI agents work together — extracting text, checking links, analyzing content, and making a determination.' },
                            { icon: '🛡️', title: '3. Get Protection', desc: 'Receive a clear verdict with confidence level, detailed summary, and actionable recommendations in your language.' },
                        ].map((step, i) => (
                            <div
                                key={i}
                                className="glass-card hover:glass-card-hover p-8 animate-fade-in-up"
                                style={{ animationDelay: `${i * 0.15}s`, opacity: 0 }}
                            >
                                <span className="text-4xl block mb-4">{step.icon}</span>
                                <h3 className="text-lg font-bold mb-2">{step.title}</h3>
                                <p className="text-gray-400 leading-relaxed">{step.desc}</p>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* Agent Showcase */}
            <section className="py-16">
                <div className="max-w-[1200px] mx-auto px-6">
                    <h2 className="text-center text-3xl font-bold mb-2">Meet the <span className="gradient-text">AI Team</span></h2>
                    <p className="text-center text-lg text-gray-400 mb-10">Seven specialized agents working in coordination to protect you</p>

                    <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-7 gap-3.5">
                        {agents.map((agent, i) => (
                            <div
                                key={agent.id}
                                className="glass-card hover:glass-card-hover p-5 text-center animate-fade-in-up"
                                style={{ animationDelay: `${i * 0.1}s`, opacity: 0 }}
                            >
                                <span className="text-3xl block mb-2">{agent.icon}</span>
                                <span className="font-heading font-semibold text-sm">{agent.name}</span>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* CTA */}
            <section className="py-16">
                <div className="max-w-[1200px] mx-auto px-6">
                    <div className="text-center p-12 md:p-16 bg-gradient-to-br from-primary/12 to-accent/[0.06] border border-primary-light/20 rounded-3xl">
                        <h2 className="text-3xl font-bold mb-4">Ready to Stay <span className="gradient-text">Safe</span>?</h2>
                        <p className="text-lg text-gray-400 mb-8 max-w-[500px] mx-auto">
                            Upload a screenshot of any suspicious message and let our AI agents protect you.
                        </p>
                        <Link
                            to="/scan"
                            className="inline-flex items-center gap-2 px-8 py-4 text-lg font-semibold rounded-full bg-gradient-to-br from-primary to-primary-light text-white btn-glow hover:-translate-y-0.5 transition-all duration-250 no-underline"
                        >
                            🔍 Start Scanning Now
                        </Link>
                    </div>
                </div>
            </section>
        </div>
    );
}
