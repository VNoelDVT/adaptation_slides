import React, { useState, useRef, useEffect } from 'react';

const ChatInterface = () => {
    const [message, setMessage] = useState('');
    const [history, setHistory] = useState([]);
    const [logs, setLogs] = useState([]);
    const [isLoading, setIsLoading] = useState(false);  // loader flag
    const bottomRef = useRef(null);

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!message.trim()) return;

        // Ajoute le message utilisateur
        setHistory(prev => [...prev, { role: 'user', content: message }]);
        setIsLoading(true);  // Active le loader

        try {
            const res = await fetch('http://127.0.0.1:8000/agent-run', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: message,
                    hisotry: history,
                    project_id: "string",
                    document_text: "",
                    strategy: "recursive",
                    n_results: 3
                })
            });

            const data = await res.json();
            setHistory(prev => [...prev, { role: 'agent', content: data.agent_response }]);
            setLogs(data.history || []);

        } catch (error) {
            const errorMsg = 'Erreur lors de la requête.';
            setHistory(prev => [...prev, { role: 'agent', content: errorMsg }]);
        } finally {
            setIsLoading(false);  // Désactive le loader
        }

        setMessage('');
    };

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [history, isLoading]);

    return (
        <div className="flex flex-col h-screen w-screen bg-gray-900 text-white">
            {/* Header */}
            <header className="p-4 bg-gray-800 shadow text-3xl font-bold flex items-center gap-2 w-full">
                <span role="img" aria-label="brain">🧠</span> Slides Maker
            </header>

            {/* Chat History */}
            <div className="flex-1 overflow-y-auto p-4 flex flex-col w-full">
                {history.length === 0 ? (
                    <div className="text-gray-400 text-center mt-10">Aucune conversation encore.</div>
                ) : (
                    history.map((entry, idx) => (
                        <div
                            key={idx}
                            className={`my-2 p-3 rounded-lg max-w-[80%] ${
                                entry.role === 'user'
                                    ? 'bg-blue-500 text-white self-end text-right'
                                    : 'bg-gray-700 text-white self-start text-left'
                            }`}
                        >
                            <span className="block text-sm mb-1 font-semibold">
                                {entry.role === 'user' ? '🗣️ Vous :' : '🤖 Agent :'}
                            </span>
                            {entry.content}
                        </div>
                    ))
                )}

                {/* Loader de saisie */}
                {isLoading && (
                    <div className="my-2 p-3 rounded-lg max-w-[80%] bg-gray-700 text-white self-start text-left animate-pulse">
                        <span className="block text-sm mb-1 font-semibold">🤖 Agent :</span>
                        L'agent réfléchit<span className="dot-anim"></span>
                    </div>
                )}
                <div ref={bottomRef} />
            </div>

            {/* Chat Input */}
            <form onSubmit={handleSubmit} className="p-4 bg-gray-800 flex gap-2 w-full">
                <input
                    type="text"
                    className="flex-1 border rounded-lg p-3 text-black focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Entrez votre message..."
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                />
                <button
                    type="submit"
                    className="bg-blue-600 text-white px-5 py-3 rounded-lg hover:bg-blue-700 transition-colors"
                    disabled={isLoading}
                >
                    {isLoading ? 'En cours...' : 'Envoyer'}
                </button>
            </form>

            {/* Logs */}
            {logs.length > 0 && (
                <div className="p-4 bg-gray-800 overflow-y-auto max-h-64 w-full">
                    <h2 className="text-xl font-semibold mb-4">📋 Logs des Agents :</h2>
                    {logs.map((log, idx) => (
                        <div key={idx} className="mb-6">
                            <pre className="bg-gray-700 p-3 rounded text-sm overflow-x-auto whitespace-pre-wrap">
{`Agent: ${log.agent}

Prompt: ${log.prompt}

Décision: ${log.decision || "N/A"}

Mémoire (extrait) :
${log.updated_memory ? JSON.stringify(log.updated_memory, null, 2) : "Pas de mémoire enregistrée"}

Historique (extrait) :
${log.full_chat_history ? JSON.stringify(log.full_chat_history, null, 2) : "Pas d'historique"}

Sortie:
${log.output}`}
                            </pre>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default ChatInterface;
