"use client";
import { useState } from 'react';
import { AlignLeft, ChevronRight, Loader2 } from 'lucide-react';
import axios from 'axios';

export default function Summary({ collectionId }: { collectionId: string }) {
    const [summary, setSummary] = useState<string | null>(null);
    const [level, setLevel] = useState<'brief' | 'detailed' | 'comprehensive'>('detailed');
    const [isLoading, setIsLoading] = useState(false);

    const fetchSummary = async () => {
        setIsLoading(true);
        try {
            const response = await axios.get(`https://ai-learning-assistant-backend-lyhw.onrender.com/api/v1/learning/summary/${collectionId}?level=${level}`);
            setSummary(response.data.summary);
        } catch (err) {
            console.error(err);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="bg-white rounded-3xl border border-slate-100 shadow-xl shadow-slate-200/50 p-6 md:p-8">
            <div className="flex items-center justify-between mb-8">
                <div className="flex items-center gap-3">
                    <div className="p-2 bg-emerald-50 rounded-xl text-emerald-600">
                        <AlignLeft size={20} />
                    </div>
                    <h3 className="font-bold text-slate-800">Smart Summary</h3>
                </div>
                <div className="flex gap-2 p-1 bg-slate-50 rounded-xl border border-slate-100">
                    {(['brief', 'detailed', 'comprehensive'] as const).map(l => (
                        <button
                            key={l}
                            onClick={() => setLevel(l)}
                            className={`px-4 py-2 rounded-lg text-xs font-bold transition-all ${level === l ? 'bg-white text-primary-500 shadow-sm' : 'text-slate-400 hover:text-slate-600'
                                }`}
                        >
                            {l.charAt(0).toUpperCase() + l.slice(1)}
                        </button>
                    ))}
                </div>
            </div>

            {!summary ? (
                <div className="text-center py-12">
                    <button
                        onClick={fetchSummary}
                        disabled={isLoading}
                        className="btn-primary flex items-center gap-2 mx-auto"
                    >
                        {isLoading ? <Loader2 size={18} className="animate-spin" /> : <ChevronRight size={18} />}
                        Generate {level} summary
                    </button>
                </div>
            ) : (
                <div className="prose prose-slate max-w-none text-slate-600 leading-relaxed animate-in fade-in duration-700">
                    {summary.split('\n').map((para, i) => (
                        <p key={i} className="mb-4">{para}</p>
                    ))}
                    <button
                        onClick={() => setSummary(null)}
                        className="text-xs text-primary-500 font-bold hover:underline mt-6"
                    >
                        Regenerate summary
                    </button>
                </div>
            )}
        </div>
    );
}
