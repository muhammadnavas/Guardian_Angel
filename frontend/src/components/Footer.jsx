import { Link } from 'react-router-dom';

export default function Footer() {
    return (
        <footer className="border-t border-white/[0.08] mt-16 bg-[#0a0e1a]/50">
            <div className="max-w-[1200px] mx-auto px-6 pt-12 pb-8">
                <div className="grid grid-cols-1 md:grid-cols-[2fr_1fr_1fr] gap-10 mb-10">
                    {/* Brand */}
                    <div>
                        <div className="flex items-center gap-2 font-heading text-xl font-bold mb-4">
                            <span className="text-2xl">🛡️</span>
                            <span>Guardian Angel</span>
                        </div>
                        <p className="text-gray-400 text-[0.9375rem] leading-relaxed max-w-[340px]">
                            An autonomous AI agent system protecting senior citizens from digital scams using multi-agent collaboration and advanced threat detection.
                        </p>
                    </div>

                    {/* Navigation */}
                    <div>
                        <h4 className="text-base font-semibold mb-4">Navigation</h4>
                        <ul className="list-none space-y-2">
                            <li><Link to="/" className="text-gray-400 text-sm hover:text-primary-light transition-colors">Home</Link></li>
                            <li><Link to="/scan" className="text-gray-400 text-sm hover:text-primary-light transition-colors">Scan Message</Link></li>
                            <li><Link to="/history" className="text-gray-400 text-sm hover:text-primary-light transition-colors">Scan History</Link></li>
                            <li><Link to="/about" className="text-gray-400 text-sm hover:text-primary-light transition-colors">About</Link></li>
                        </ul>
                    </div>

                    {/* Resources */}
                    <div>
                        <h4 className="text-base font-semibold mb-4">Resources</h4>
                        <ul className="list-none space-y-2">
                            <li><a href="https://github.com/dcarpintero/minerva" target="_blank" rel="noreferrer" className="text-gray-400 text-sm hover:text-primary-light transition-colors">GitHub</a></li>
                            <li><a href="https://arxiv.org/abs/2308.08155" target="_blank" rel="noreferrer" className="text-gray-400 text-sm hover:text-primary-light transition-colors">AutoGen Paper</a></li>
                            <li><a href="https://www.ic3.gov/" target="_blank" rel="noreferrer" className="text-gray-400 text-sm hover:text-primary-light transition-colors">FBI IC3</a></li>
                        </ul>
                    </div>
                </div>

                <div className="flex flex-col sm:flex-row items-center justify-between pt-6 border-t border-white/[0.08] text-gray-500 text-sm gap-2">
                    <span>© {new Date().getFullYear()} Guardian Angel — AgentX Hackathon 2026</span>
                    <span>Built with AutoGen & Gemini</span>
                </div>
            </div>
        </footer>
    );
}
