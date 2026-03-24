"use client";
import { useState, useRef, useEffect } from 'react';
import { Send, User, Bot, Loader2 } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';

interface Message {
    role: 'user' | 'bot';
    content: string;
}

export default function Chat({ collectionId }: { collectionId: string }) {
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [suggestions, setSuggestions] = useState<string[]>([]);
    const scrollRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const fetchHistory = async () => {
            try {
                const res = await axios.get(`https://ai-learning-assistant-backend-lyhw.onrender.com/api/v1/chat/history/${collectionId}`);
                if (res.data.history && res.data.history.length > 0) {
                    setMessages(res.data.history.map((h: any) => ({
                        role: h.role === 'user' ? 'user' : 'bot',
                        content: h.content
                    })));
                } else {
                    setMessages([]);
                }
            } catch (err) {
                console.error("Failed to load history", err);
            }
        };
        fetchHistory();
    }, [collectionId]);

    useEffect(() => {
        const fetchSuggestions = async () => {
            try {
                const res = await axios.get(`https://ai-learning-assistant-backend-lyhw.onrender.com/api/v1/learning/metadata/${collectionId}`);
                if (res.data.suggested_questions) {
                    setSuggestions(res.data.suggested_questions);
                }
            } catch (err) {
                console.error("Failed to load suggestions", err);
            }
        };
        fetchSuggestions();
    }, [collectionId]);

    const scrollToBottom = () => {
        scrollRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(scrollToBottom, [messages]);

    const handleSend = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!input.trim() || isLoading) return;

        const userMessage = input.trim();
        setInput('');
        setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
        setIsLoading(true);

        try {
            const response = await axios.post('https://ai-learning-assistant-backend-lyhw.onrender.com/api/v1/chat/query', {
                query: userMessage,
                session_id: 'prod-session',
                collection_name: collectionId
            });

            setMessages(prev => [...prev, { role: 'bot', content: response.data.answer }]);
        } catch (error) {
            console.error('Chat error:', error);
            setMessages(prev => [...prev, { role: 'bot', content: 'Sorry, I encountered an error. Is the backend running?' }]);
        } finally {
            setIsLoading(false);
        }
    };

    const handleSuggestionClick = (suggestion: string) => {
        setInput(suggestion);
        // Optionally auto-submit
    };

    const exportChat = () => {
        if (messages.length === 0) return;
        const text = messages.map(m => `${m.role === 'user' ? 'Q' : 'A'}: ${m.content}`).join('\n\n');
        const element = document.createElement("a");
        const file = new Blob([text], { type: 'text/plain' });
        element.href = URL.createObjectURL(file);
        element.download = `qa_history_${new Date().toISOString().slice(0, 10)}.txt`;
        document.body.appendChild(element);
        element.click();
        document.body.removeChild(element);
    };

    return (
        <div className="flex-1 flex flex-col h-full bg-slate-50/30">
            {messages.length > 0 && (
                <div className="flex justify-end p-4 pb-0">
                    <button onClick={exportChat} className="text-xs bg-slate-200 hover:bg-slate-300 text-slate-700 font-semibold px-4 py-2 rounded-lg transition-colors">
                        Export QA History
                    </button>
                </div>
            )}
            <div className="flex-1 overflow-y-auto p-4 md:p-8 space-y-6">
                <AnimatePresence>
                    {messages.map((m, i) => (
                        <motion.div
                            key={i}
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}
                        >
                            <div className={`max-w-[85%] flex gap-4 p-4 rounded-2xl shadow-sm border ${m.role === 'user'
                                ? 'bg-primary-500 text-white border-primary-600'
                                : 'bg-white text-slate-800 border-slate-100'
                                }`}>
                                <div className="mt-1 shrink-0">
                                    {m.role === 'user' ? <User size={20} /> : <Bot size={20} className="text-primary-500" />}
                                </div>
                                <p className="leading-relaxed whitespace-pre-wrap">{m.content}</p>
                            </div>
                        </motion.div>
                    ))}
                    {isLoading && (
                        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex justify-start">
                            <div className="bg-white p-4 rounded-2xl border border-slate-100 shadow-sm flex items-center gap-2">
                                <Loader2 size={18} className="animate-spin text-primary-500" />
                                <span className="text-sm text-slate-400">Thinking...</span>
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>
                <div ref={scrollRef} />
            </div>

            <div className="p-4 md:p-8 pt-0">
                {suggestions.length > 0 && messages.length === 0 && (
                    <div className="mb-6">
                        <p className="text-xs text-slate-500 font-bold uppercase tracking-widest mb-3 text-center">Suggested Questions</p>
                        <div className="flex flex-wrap gap-2 justify-center">
                            {suggestions.map((q, i) => (
                                <button
                                    key={i}
                                    onClick={() => handleSuggestionClick(q)}
                                    className="text-xs bg-white border border-slate-200 hover:border-primary-500 hover:text-primary-600 text-slate-600 px-4 py-2 rounded-full transition-all shadow-sm max-w-sm truncate"
                                    title={q}
                                >
                                    {q}
                                </button>
                            ))}
                        </div>
                    </div>
                )}
                <form onSubmit={handleSend} className="relative max-w-4xl mx-auto">
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        placeholder="Ask a question about your lecture..."
                        className="w-full bg-white border border-slate-200 rounded-2xl px-6 py-4 pr-16 shadow-lg focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 transition-all text-slate-800"
                    />
                    <button
                        type="submit"
                        disabled={isLoading}
                        className="absolute right-3 top-1/2 -translate-y-1/2 p-2 bg-primary-500 hover:bg-primary-600 text-white rounded-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-md shadow-primary-500/20"
                    >
                        <Send size={20} />
                    </button>
                </form>
                <p className="text-center text-[10px] text-slate-400 mt-4 uppercase tracking-widest font-semibold">
                    Powered by Gemini 2.0 Flash & BM25 Lexical Search
                </p>
            </div>
        </div>
    );
}
