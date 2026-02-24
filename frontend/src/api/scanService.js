// Mock API service — ready to swap with real FastAPI backend
const API_BASE = 'http://localhost:8000/api';

const AGENTS = [
    { id: 1, name: 'OCR Specialist', icon: '📝', description: 'Extracting text from image...' },
    { id: 2, name: 'Link Checker', icon: '🔗', description: 'Verifying URLs for safety...' },
    { id: 3, name: 'Content Analyst', icon: '🔍', description: 'Analyzing scam patterns...' },
    { id: 4, name: 'Decision Maker', icon: '⚖️', description: 'Making final determination...' },
    { id: 5, name: 'Summary Agent', icon: '📋', description: 'Generating summary...' },
    { id: 6, name: 'Translation Agent', icon: '🌐', description: 'Translating to user language...' },
    { id: 7, name: 'Data Storage Agent', icon: '💾', description: 'Archiving results...' },
];

// Simulate streaming agent updates
export async function analyzeScan(imageFile, onAgentUpdate) {
    // In production, this would be:
    // const formData = new FormData();
    // formData.append('image', imageFile);
    // const response = await fetch(`${API_BASE}/analyze`, { method: 'POST', body: formData });

    // Mock streaming updates
    for (let i = 0; i < AGENTS.length; i++) {
        await new Promise(resolve => setTimeout(resolve, 1200 + Math.random() * 800));
        onAgentUpdate({
            agentIndex: i,
            agent: AGENTS[i],
            status: 'completed',
            output: getMockOutput(i),
        });
    }

    // Return final result
    const isScam = Math.random() > 0.35;
    return {
        verdict: isScam ? 'scam' : 'safe',
        confidence: isScam ? Math.floor(Math.random() * 2) + 4 : Math.floor(Math.random() * 2) + 4,
        summary: isScam
            ? 'This message contains several red flags typically associated with phishing scams, including urgency tactics, suspicious links, and impersonation of a legitimate organization. We strongly recommend not clicking any links and reporting this message.'
            : 'This message appears to be legitimate. No suspicious links, scam patterns, or deceptive content was detected. The content is consistent with genuine communications.',
        extractedText: 'Sample extracted text from the image...',
        linksFound: isScam ? ['http://suspicious-link.example.com'] : [],
        linksVerdict: isScam ? 'Flagged' : 'Not Flagged',
        scamPatterns: isScam ? ['Urgency tactics', 'Suspicious sender', 'Phishing link'] : [],
    };
}

function getMockOutput(agentIndex) {
    const outputs = [
        'Text successfully extracted from image. Found 3 paragraphs of content.',
        'Found 1 URL. Checking against Google SafeBrowsing database...',
        'Identified urgency indicators and impersonation patterns in message content.',
        'Based on combined analysis: High probability of scam detected.',
        'Summary: This message exhibits phishing characteristics with deceptive urgency tactics.',
        'Language detected: English. No translation needed.',
        'Results archived to database successfully.',
    ];
    return outputs[agentIndex];
}

export function getAgentsList() {
    return AGENTS;
}

// Mock history data
export async function getHistory() {
    return [
        {
            id: 1,
            date: '2026-02-24',
            time: '14:32',
            verdict: 'scam',
            confidence: 5,
            summary: 'Phishing attempt impersonating a banking institution with suspicious redirect links.',
            extractedText: 'Dear valued customer, your account has been compromised...',
        },
        {
            id: 2,
            date: '2026-02-23',
            time: '09:15',
            verdict: 'safe',
            confidence: 4,
            summary: 'Legitimate opera ticket confirmation from a verified ticketing platform.',
            extractedText: 'Your opera ticket has been confirmed for March 15...',
        },
        {
            id: 3,
            date: '2026-02-22',
            time: '18:45',
            verdict: 'scam',
            confidence: 4,
            summary: 'Social engineering attempt using fake gift card reward to collect personal information.',
            extractedText: 'Congratulations! You have won a $500 gift card...',
        },
        {
            id: 4,
            date: '2026-02-21',
            time: '11:20',
            verdict: 'scam',
            confidence: 5,
            summary: 'SMS billing scam with urgent payment demand and suspicious shortened URL.',
            extractedText: 'URGENT: Your bill of $299.99 is overdue...',
        },
        {
            id: 5,
            date: '2026-02-20',
            time: '16:00',
            verdict: 'safe',
            confidence: 5,
            summary: 'Landscape photograph with no text content detected.',
            extractedText: 'No text found in image.',
        },
    ];
}
