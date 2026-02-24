import { Link } from 'react-router-dom';
import { getAgentsList } from '../api/scanService';

export default function About() {
  const agents = getAgentsList();

  return (
    <div className="pt-24 min-h-screen">
      <div className="max-w-[1200px] mx-auto px-6">
        {/* Header */}
        <div className="text-center mb-16 animate-fade-in-up">
          <h1 className="text-3xl md:text-4xl font-bold mb-3">
            About <span className="gradient-text">Guardian Angel</span>
          </h1>
          <p className="text-lg text-gray-400 max-w-[600px] mx-auto">
            An autonomous multi-agent AI system designed to protect senior citizens from digital scams
          </p>
        </div>

        {/* Problem */}
        <div className="mb-16">
          <div className="glass-card p-10">
            <h2 className="text-2xl font-bold mb-4">🎯 The Problem</h2>
            <p className="text-gray-400 leading-relaxed mb-4">
              Digital scams inflict devastating impacts on our society, with senior citizens being
              disproportionately targeted. According to the FBI IC3, <strong className="text-white">$37.4 billion</strong> was
              lost in the United States alone over the past five years due to Internet scams.
            </p>
            <p className="text-gray-400 leading-relaxed mb-6">
              Beyond direct financial losses, victims face psychological disruptions and diminished
              trust in emerging technologies. Guardian Angel addresses this challenge with an
              autonomous AI-powered scam detection system.
            </p>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-5 mt-8">
              {[
                { value: '$37.4B', label: 'Lost to Internet scams (5 years)' },
                { value: '4M+', label: 'Complaints processed' },
                { value: '88.3%', label: 'Detection accuracy' },
              ].map((stat) => (
                <div key={stat.label} className="text-center p-6 rounded-xl bg-white/[0.04] border border-white/[0.08]">
                  <div className="font-heading text-2xl font-extrabold text-danger mb-1">{stat.value}</div>
                  <div className="text-sm text-gray-400">{stat.label}</div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Architecture */}
        <div className="mb-16">
          <h2 className="text-center text-2xl font-bold mb-10">⚙️ Architecture <span className="gradient-text">Flow</span></h2>
          <div className="flex items-center justify-center gap-3 flex-wrap">
            {agents.map((agent, idx) => (
              <div key={agent.id} className="flex items-center gap-3">
                <div className="glass-card hover:glass-card-hover p-5 text-center min-w-[120px]">
                  <span className="text-2xl block mb-1.5">{agent.icon}</span>
                  <span className="font-heading font-semibold text-xs">{agent.name}</span>
                </div>
                {idx < agents.length - 1 && (
                  <span className="text-xl text-primary-light max-md:rotate-90">→</span>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Tech Stack */}
        <div className="mb-16">
          <h2 className="text-center text-2xl font-bold mb-10">🧰 Tech <span className="gradient-text">Stack</span></h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
            {[
              { icon: '🤖', title: 'Microsoft AutoGen', desc: 'Multi-agent orchestration framework enabling round-robin collaboration between 7 specialized AI agents.' },
              { icon: '💎', title: 'Gemini 2.5 Flash', desc: "Google's advanced LLM powering vision, reasoning, and tool-calling via the OpenAI-compatible endpoint." },
              { icon: '🔐', title: 'Google SafeBrowsing', desc: 'Real-time URL verification against malware, phishing, social engineering, and harmful application databases.' },
              { icon: '🗄️', title: 'SQLite Database', desc: 'Lightweight persistent storage for archiving analysis results with SHA-256 deduplication.' },
              { icon: '⚛️', title: 'React + Vite', desc: 'Modern frontend built with React and Tailwind CSS for a responsive, senior-friendly interface.' },
              { icon: '🐍', title: 'Python Backend', desc: 'Async Python backend powering the agent orchestration and tool execution layer.' },
            ].map((tech, i) => (
              <div
                key={tech.title}
                className="glass-card hover:glass-card-hover p-7 animate-fade-in-up"
                style={{ animationDelay: `${i * 0.1}s`, opacity: 0 }}
              >
                <span className="text-3xl block mb-3">{tech.icon}</span>
                <h3 className="text-lg font-bold mb-2">{tech.title}</h3>
                <p className="text-sm text-gray-400 leading-relaxed">{tech.desc}</p>
              </div>
            ))}
          </div>
        </div>

        {/* CTA */}
        <div className="text-center py-10">
          <Link
            to="/scan"
            className="inline-flex items-center gap-2 px-8 py-4 text-lg font-semibold rounded-full bg-gradient-to-br from-primary to-primary-light text-white btn-glow hover:-translate-y-0.5 transition-all duration-250 no-underline"
          >
            🔍 Try Guardian Angel Now
          </Link>
        </div>
      </div>
    </div>
  );
}
