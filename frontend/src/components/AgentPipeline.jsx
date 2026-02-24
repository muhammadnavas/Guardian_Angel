import { getAgentsList } from '../api/scanService';

export default function AgentPipeline({ activeIndex, completedAgents }) {
    const agents = getAgentsList();

    const getStatus = (index) => {
        if (completedAgents.includes(index)) return 'completed';
        if (index === activeIndex) return 'active';
        return 'pending';
    };

    return (
        <div className="flex flex-col">
            {agents.map((agent, idx) => {
                const status = getStatus(idx);
                return (
                    <div key={agent.id} className="flex items-start gap-4 px-5 py-3.5 relative">
                        {/* Connector line */}
                        {idx < agents.length - 1 && (
                            <div
                                className={`absolute left-[38px] top-[46px] w-0.5 h-[calc(100%-20px)] transition-all duration-250 ${status === 'completed' ? 'bg-primary-light' :
                                        status === 'active' ? 'bg-gradient-to-b from-primary-light to-white/[0.08]' :
                                            'bg-white/[0.08]'
                                    }`}
                            />
                        )}

                        {/* Step indicator */}
                        <div
                            className={`w-[38px] h-[38px] min-w-[38px] rounded-full flex items-center justify-center text-lg border-2 relative z-10 transition-all duration-250 ${status === 'completed'
                                    ? 'border-primary-light bg-primary-light/15 shadow-[0_0_12px_rgba(99,102,241,0.25)]'
                                    : status === 'active'
                                        ? 'border-accent bg-accent/15 animate-pulse-glow shadow-[0_0_15px_rgba(245,158,11,0.3)]'
                                        : 'border-white/[0.08] bg-surface opacity-40'
                                }`}
                        >
                            {status === 'completed' ? '✓' : agent.icon}
                        </div>

                        {/* Content */}
                        <div className={`flex-1 pt-0.5 ${status === 'pending' ? 'opacity-40' : ''}`}>
                            <div className="font-heading font-semibold text-base">{agent.name}</div>
                            <div className="text-sm text-gray-400">{agent.description}</div>
                        </div>

                        {/* Status badge */}
                        <div
                            className={`text-sm font-medium px-2.5 py-0.5 rounded-full whitespace-nowrap ${status === 'completed'
                                    ? 'text-safe bg-safe/12'
                                    : status === 'active'
                                        ? 'text-accent bg-accent/12'
                                        : 'text-gray-500 opacity-40'
                                }`}
                        >
                            {status === 'active' && (
                                <span className="inline-block w-4 h-4 border-2 border-accent border-t-transparent rounded-full animate-spin-fast align-middle mr-1" />
                            )}
                            {status === 'completed' ? '✓ Done' : status === 'active' ? 'Running' : 'Pending'}
                        </div>
                    </div>
                );
            })}
        </div>
    );
}
