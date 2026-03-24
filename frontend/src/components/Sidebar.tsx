"use client";
import { useState, useEffect } from 'react';
import { Upload, FileText, CheckCircle2, AlertCircle, Loader2, AlignLeft, Brain, Sparkles, Image as ImageIcon, BarChart3 } from 'lucide-react';
import axios from 'axios';

interface SidebarProps {
    onUploadComplete: (id: string) => void;
    activeCollectionId: string | null;
    activeTab: 'chat' | 'summary' | 'quiz' | 'images' | 'analytics';
    setActiveTab: (tab: 'chat' | 'summary' | 'quiz' | 'images' | 'analytics') => void;
}

export default function Sidebar({ onUploadComplete, activeCollectionId, activeTab, setActiveTab }: SidebarProps) {
    const [isUploading, setIsUploading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [files, setFiles] = useState<{ name: string, id: string }[]>([]);
    const [topics, setTopics] = useState<string[]>([]);
    const [isLoadingTopics, setIsLoadingTopics] = useState(false);

    // Fetch topics whenever the active collection changes
    useEffect(() => {
        const fetchTopics = async () => {
            if (!activeCollectionId) return;
            setIsLoadingTopics(true);
            try {
                const res = await axios.get(`https://ai-learning-assistant-backend-lyhw.onrender.com/api/v1/learning/metadata/${activeCollectionId}`);
                if (res.data.topics) {
                    setTopics(res.data.topics);
                }
            } catch (err) {
                console.error("Failed to fetch topics for sidebar", err);
            } finally {
                setIsLoadingTopics(false);
            }
        };
        fetchTopics();
    }, [activeCollectionId]);

    const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (!file || isUploading) return;

        setIsUploading(true);
        setError(null);

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await axios.post('https://ai-learning-assistant-backend-lyhw.onrender.com/api/v1/ingestion/upload', formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });

            const newFile = { name: file.name, id: response.data.collection_id };
            setFiles(prev => [newFile, ...prev]);
            onUploadComplete(newFile.id);
        } catch (err) {
            setError('Upload failed. Check backend connection.');
            console.error(err);
        } finally {
            setIsUploading(false);
        }
    };

    const navItems = [
        { id: 'chat', label: 'AI Chat', icon: FileText },
        { id: 'summary', label: 'Summary', icon: AlignLeft },
        { id: 'quiz', label: 'Quiz', icon: Brain },
        { id: 'images', label: 'Figures', icon: ImageIcon },
        { id: 'analytics', label: 'Analytics', icon: BarChart3 },
    ] as const;

    return (
        <div className="w-80 h-full bg-slate-900 text-white flex flex-col p-6 overflow-hidden border-r border-slate-800">
            <div className="flex items-center gap-3 mb-10 px-2">
                <div className="w-10 h-10 bg-primary-500 rounded-xl flex items-center justify-center shadow-lg shadow-primary-500/20">
                    <Sparkles size={24} strokeWidth={2.5} />
                </div>
                <div>
                    <h1 className="font-bold text-lg leading-tight tracking-tight">AI Master</h1>
                    <p className="text-xs text-slate-500 font-medium">Production Release v1.0</p>
                </div>
            </div>

            <div className="space-y-6 flex-1 overflow-y-auto custom-scrollbar">
                {/* Navigation Tabs */}
                {files.length > 0 && (
                    <nav className="space-y-1">
                        <h3 className="text-[10px] text-slate-500 font-bold uppercase tracking-[0.2em] mb-3 px-2">Mode</h3>
                        {navItems.map((item) => (
                            <button
                                key={item.id}
                                onClick={() => setActiveTab(item.id)}
                                className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${activeTab === item.id
                                    ? 'bg-primary-500 text-white shadow-lg shadow-primary-500/20'
                                    : 'text-slate-400 hover:text-white hover:bg-slate-800'
                                    }`}
                            >
                                <item.icon size={18} />
                                <span className="text-sm font-bold">{item.label}</span>
                            </button>
                        ))}
                    </nav>
                )}

                <div className="h-px bg-slate-800/50 mx-2" />

                {/* Topics Section */}
                {activeCollectionId && (
                    <div className="space-y-3 px-2">
                        <h3 className="text-[10px] text-slate-500 font-bold uppercase tracking-[0.2em] mb-2">Key Topics</h3>
                        {isLoadingTopics ? (
                            <div className="flex items-center gap-2 text-xs text-slate-500">
                                <Loader2 size={14} className="animate-spin text-primary-500" /> Generating...
                            </div>
                        ) : topics.length > 0 ? (
                            <div className="flex flex-wrap gap-2">
                                {topics.map((t, idx) => (
                                    <span key={idx} className="text-[10px] font-bold bg-slate-800 text-slate-300 border border-slate-700 px-3 py-1.5 rounded-full">
                                        {t.length > 25 ? t.substring(0, 25) + '...' : t}
                                    </span>
                                ))}
                            </div>
                        ) : (
                            <p className="text-xs text-slate-500 italic">No topics found.</p>
                        )}
                    </div>
                )}
                <div className="h-px bg-slate-800/50 mx-2" />

                <label className="group relative flex flex-col items-center justify-center p-8 border-2 border-dashed border-slate-700 hover:border-primary-500/50 hover:bg-primary-500/5 rounded-2xl cursor-pointer transition-all duration-300">
                    <input type="file" className="hidden" accept=".pdf" onChange={handleFileUpload} />
                    {isUploading ? (
                        <Loader2 size={32} className="animate-spin text-primary-500 mb-2" />
                    ) : (
                        <Upload size={32} className="text-slate-500 group-hover:text-primary-500 transition-colors mb-2" />
                    )}
                    <span className="text-sm font-semibold text-slate-300 group-hover:text-white transition-colors">
                        {isUploading ? 'Processing...' : 'Upload Lecture PDF'}
                    </span>
                    <span className="text-[10px] text-slate-500 mt-1 uppercase tracking-wider">Drag & drop here</span>
                </label>

                {error && (
                    <div className="bg-red-500/10 border border-red-500/20 p-4 rounded-xl flex gap-3 items-start animate-in fade-in slide-in-from-top-2">
                        <AlertCircle size={18} className="text-red-500 shrink-0 mt-0.5" />
                        <p className="text-xs text-red-400 font-medium leading-relaxed">{error}</p>
                    </div>
                )}

                <div className="space-y-3">
                    <h3 className="text-[10px] text-slate-500 font-bold uppercase tracking-[0.2em] mb-4 px-2">Your Documents</h3>
                    {files.map((f, i) => (
                        <div
                            key={i}
                            onClick={() => onUploadComplete(f.id)}
                            className={`group p-4 rounded-xl flex gap-3 items-center transition-all cursor-pointer border ${activeCollectionId === f.id
                                ? 'bg-slate-800 border-primary-500/30'
                                : 'bg-slate-800/50 border-slate-700/50 hover:border-primary-500/30'
                                }`}
                        >

                            <CheckCircle2 size={18} className="text-emerald-500" />
                            <p className="text-sm font-medium text-slate-300 truncate transition-colors group-hover:text-white">{f.name}</p>
                        </div>
                    ))}
                    {files.length === 0 && (
                        <div className="text-center py-10 opacity-30 select-none">
                            <p className="text-xs font-medium">No documents yet</p>
                        </div>
                    )}
                </div>
            </div>

            <div className="mt-auto px-2 pt-6 border-t border-slate-800/50">
                <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center">
                        <span className="text-[10px] font-bold text-slate-500">VP</span>
                    </div>
                    <p className="text-xs font-semibold text-slate-400">Vishnu • Project 6</p>
                </div>
            </div>
        </div>
    );
}
