"use client";
import { useState } from 'react';
import { Menu } from 'lucide-react';
import Chat from '@/components/Chat';
import Sidebar from '@/components/Sidebar';
import Summary from '@/components/Summary';
import Quiz from '@/components/Quiz';
import Gallery from '@/components/Gallery';
import Analytics from '@/components/Analytics';

export default function Home() {
    const [collectionId, setCollectionId] = useState<string | null>(null);
    const [activeTab, setActiveTab] = useState<'chat' | 'summary' | 'quiz' | 'images' | 'analytics'>('chat');
    const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

    return (
        <main className="flex h-screen overflow-hidden">
            {/* Mobile Sidebar Overlay */}
            {isMobileMenuOpen && (
                <div
                    className="fixed inset-0 bg-slate-900/50 backdrop-blur-sm z-40 md:hidden"
                    onClick={() => setIsMobileMenuOpen(false)}
                />
            )}

            <Sidebar
                onUploadComplete={setCollectionId}
                activeCollectionId={collectionId}
                activeTab={activeTab}
                setActiveTab={setActiveTab}
                isMobileMenuOpen={isMobileMenuOpen}
                setIsMobileMenuOpen={setIsMobileMenuOpen}
            />
            <div className="flex-1 flex flex-col relative bg-white overflow-hidden w-full">
                {!collectionId ? (
                    <div className="flex-1 flex items-center justify-center p-8 text-center bg-slate-50/30">
                        <div className="max-w-md animate-in fade-in zoom-in duration-1000">
                            <h2 className="text-4xl font-black text-slate-800 mb-6 tracking-tight">Master Your Lectures</h2>
                            <p className="text-slate-500 mb-10 leading-relaxed font-medium">
                                The ultimate AI-powered study companion. Upload your transcripts to unlock chat-driven insights, smart summaries, and interactive quizzes.
                            </p>
                            <div className="bg-white/50 backdrop-blur-sm p-8 rounded-[2rem] border border-slate-200/50 shadow-2xl shadow-primary-500/5">
                                <p className="text-sm text-primary-500 font-bold uppercase tracking-widest">Ready to begin?</p>
                                <p className="text-xs text-slate-400 mt-2">Upload a PDF transcript in the sidebar</p>
                            </div>
                        </div>
                    </div>
                ) : (
                    <div className="flex-1 flex flex-col h-full overflow-hidden w-full">
                        <header className="h-16 border-b border-slate-100 flex items-center justify-between px-4 md:px-8 bg-white/80 backdrop-blur-md sticky top-0 z-10 w-full shrink-0">
                            <div className="flex items-center gap-2 md:gap-3 cursor-pointer">
                                <button
                                    onClick={() => setIsMobileMenuOpen(true)}
                                    className="md:hidden p-2 -ml-2 text-slate-500 hover:text-slate-800 transition-colors"
                                >
                                    <Menu size={24} />
                                </button>
                                <span className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse" />
                                <span className="text-[10px] md:text-xs font-bold text-slate-400 uppercase tracking-widest">Active Session</span>
                            </div>
                            <div className="text-xs md:text-sm font-bold text-slate-800 truncate max-w-[150px] md:max-w-xs">{activeTab.toUpperCase()} MODE</div>
                        </header>

                        <div className="flex-1 overflow-y-auto custom-scrollbar">
                            <div className="max-w-5xl mx-auto w-full h-full">
                                {activeTab === 'chat' && <Chat collectionId={collectionId} />}
                                {activeTab === 'summary' && (
                                    <div className="p-8"><Summary collectionId={collectionId} /></div>
                                )}
                                {activeTab === 'quiz' && (
                                    <div className="p-8"><Quiz collectionId={collectionId} /></div>
                                )}
                                {activeTab === 'images' && (
                                    <div className="p-8"><Gallery collectionId={collectionId} /></div>
                                )}
                                {activeTab === 'analytics' && (
                                    <div className="p-8 h-full"><Analytics collectionId={collectionId} /></div>
                                )}
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </main>
    );
}
