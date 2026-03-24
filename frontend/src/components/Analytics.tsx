"use client";
import { useState, useEffect } from 'react';
import axios from 'axios';
import { Loader2, TrendingUp, Target, BrainCircuit } from 'lucide-react';
import {
    Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
    ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip,
    CartesianGrid, LineChart, Line
} from 'recharts';

interface AnalyticsData {
    topics: string[];
    progress: Record<string, number>;
    quiz_scores: { score: number, correct: number, total: number, topic: string }[];
}

export default function Analytics({ collectionId }: { collectionId: string }) {
    const [data, setData] = useState<AnalyticsData | null>(null);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        const fetchAnalytics = async () => {
            try {
                const res = await axios.get(`https://ai-learning-assistant-backend-lyhw.onrender.com/api/v1/learning/analytics/${collectionId}`);
                setData(res.data);
            } catch (err) {
                console.error("Failed to load analytics", err);
            } finally {
                setIsLoading(false);
            }
        };
        fetchAnalytics();
    }, [collectionId]);

    if (isLoading) {
        return (
            <div className="flex-1 flex items-center justify-center p-8 bg-slate-50/30 rounded-3xl h-[600px]">
                <Loader2 className="animate-spin text-primary-500 w-8 h-8" />
            </div>
        );
    }

    if (!data) return null;

    // Format data for Recharts
    const radarData = data.topics.map(t => ({
        topic: t.substring(0, 15) + (t.length > 15 ? '...' : ''),
        progress: data.progress[t] || 0
    }));

    const quizData = data.quiz_scores.map((q, i) => ({
        quiz: `Quiz ${i + 1}`,
        score: q.score,
        topic: q.topic
    }));

    const hasProgress = Object.values(data.progress).some(v => v > 0);
    const hasQuizzes = data.quiz_scores.length > 0;

    return (
        <div className="bg-slate-50/30 rounded-3xl p-6 lg:p-10 flex flex-col h-full overflow-y-auto">
            <div className="mb-8">
                <h2 className="text-2xl font-black text-slate-800 tracking-tight">Learning Dashboard</h2>
                <p className="text-slate-500 mt-2">Track your subject mastery, topic coverage, and quiz performance.</p>
            </div>

            {(!hasProgress && !hasQuizzes) && (
                <div className="bg-white rounded-2xl p-10 text-center border border-slate-100 shadow-sm mt-8">
                    <Target className="w-12 h-12 text-slate-300 mx-auto mb-4" />
                    <h3 className="text-lg font-bold text-slate-700">No Data Yet</h3>
                    <p className="text-slate-500 mt-2">Interact with the AI Chat or take Quizzes to start building your analytics profile.</p>
                </div>
            )}

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 pb-10">
                {/* Topic Radar */}
                {data.topics.length > 0 && (
                    <div className="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm flex flex-col h-[400px]">
                        <div className="flex items-center gap-3 mb-6">
                            <div className="p-2 bg-indigo-50 rounded-lg text-indigo-500"><BrainCircuit size={20} /></div>
                            <h3 className="font-bold text-slate-800">Topic Coverage Radar</h3>
                        </div>
                        <div className="flex-1 min-h-0">
                            <ResponsiveContainer width="100%" height="100%">
                                <RadarChart cx="50%" cy="50%" outerRadius="70%" data={radarData}>
                                    <PolarGrid stroke="#e2e8f0" />
                                    <PolarAngleAxis dataKey="topic" tick={{ fill: '#64748b', fontSize: 12 }} />
                                    <PolarRadiusAxis angle={30} domain={[0, 100]} tick={{ fill: '#94a3b8' }} />
                                    <Radar name="Progress" dataKey="progress" stroke="#6366f1" fill="#6366f1" fillOpacity={0.2} />
                                    <Tooltip contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }} />
                                </RadarChart>
                            </ResponsiveContainer>
                        </div>
                    </div>
                )}

                {/* Progress Bar Chart */}
                {hasProgress && (
                    <div className="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm flex flex-col h-[400px]">
                        <div className="flex items-center gap-3 mb-6">
                            <div className="p-2 bg-emerald-50 rounded-lg text-emerald-500"><Target size={20} /></div>
                            <h3 className="font-bold text-slate-800">Mastery by Topic</h3>
                        </div>
                        <div className="flex-1 min-h-0">
                            <ResponsiveContainer width="100%" height="100%">
                                <BarChart data={radarData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                                    <XAxis dataKey="topic" tick={{ fill: '#64748b', fontSize: 11 }} axisLine={false} tickLine={false} />
                                    <YAxis domain={[0, 100]} tick={{ fill: '#94a3b8', fontSize: 11 }} axisLine={false} tickLine={false} />
                                    <Tooltip cursor={{ fill: '#f8fafc' }} contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }} />
                                    <Bar dataKey="progress" fill="#10b981" radius={[4, 4, 0, 0]} maxBarSize={50} />
                                </BarChart>
                            </ResponsiveContainer>
                        </div>
                    </div>
                )}

                {/* Quiz Scores Line Chart */}
                {hasQuizzes && (
                    <div className="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm flex flex-col h-[400px] lg:col-span-2">
                        <div className="flex items-center gap-3 mb-6">
                            <div className="p-2 bg-blue-50 rounded-lg text-blue-500"><TrendingUp size={20} /></div>
                            <h3 className="font-bold text-slate-800">Quiz Performance Over Time</h3>
                        </div>
                        <div className="flex-1 min-h-0">
                            <ResponsiveContainer width="100%" height="100%">
                                <LineChart data={quizData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                                    <XAxis dataKey="quiz" tick={{ fill: '#64748b', fontSize: 12 }} axisLine={false} tickLine={false} />
                                    <YAxis domain={[0, 100]} tick={{ fill: '#94a3b8', fontSize: 12 }} axisLine={false} tickLine={false} />
                                    <Tooltip contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }} />
                                    <Line type="monotone" dataKey="score" stroke="#3b82f6" strokeWidth={3} dot={{ r: 6, fill: '#3b82f6', strokeWidth: 2, stroke: '#fff' }} activeDot={{ r: 8 }} />
                                </LineChart>
                            </ResponsiveContainer>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
