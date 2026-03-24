"use client";
import { useState, useMemo } from 'react';
import { Brain, CheckCircle2, XCircle, AlertCircle, Loader2, Sparkles } from 'lucide-react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';

interface Question {
    question: string;
    options: string[];
    correctAnswerIndex: number;
    explanation: string;
}

export default function Quiz({ collectionId }: { collectionId: string }) {
    const [questions, setQuestions] = useState<Question[]>([]);
    const [answers, setAnswers] = useState<Record<number, number>>({});
    const [submitted, setSubmitted] = useState(false);
    const [isLoading, setIsLoading] = useState(false);

    const generateQuiz = async () => {
        setIsLoading(true);
        setSubmitted(false);
        setAnswers({});
        try {
            const resp = await axios.post('https://ai-learning-assistant-backend-lyhw.onrender.com/api/v1/learning/quiz', { collection_id: collectionId });
            setQuestions(resp.data.questions);
        } catch (err) {
            console.error(err);
        } finally {
            setIsLoading(false);
        }
    };

    const score = useMemo(() => questions.filter((q, i) => answers[i] === q.correctAnswerIndex).length, [questions, answers]);

    const handleSubmit = async () => {
        setSubmitted(true);
        try {
            await axios.post(`https://ai-learning-assistant-backend-lyhw.onrender.com/api/v1/learning/analytics/${collectionId}/score`, {
                score: (score / questions.length) * 100,
                correct: score,
                total: questions.length,
                topic: "General Quiz" // Simplified for now
            });
        } catch (err) {
            console.error("Failed to save quiz score", err);
        }
    };

    return (
        <div className="bg-white rounded-3xl border border-slate-100 shadow-xl shadow-slate-200/50 p-6 md:p-8">
            <div className="flex items-center justify-between mb-8">
                <div className="flex items-center gap-3">
                    <div className="p-2 bg-purple-50 rounded-xl text-purple-600">
                        <Brain size={20} />
                    </div>
                    <h3 className="font-bold text-slate-800">Knowledge Check</h3>
                </div>
                {!isLoading && (
                    <button onClick={generateQuiz} className="text-xs font-bold text-primary-500 hover:text-primary-600 transition-colors flex items-center gap-1">
                        <Sparkles size={14} /> New Quiz
                    </button>
                )}
            </div>

            {isLoading ? (
                <div className="flex flex-col items-center justify-center py-20 gap-4">
                    <Loader2 size={40} className="animate-spin text-primary-500/20" />
                    <p className="text-sm font-medium text-slate-400">Crafting personalized questions...</p>
                </div>
            ) : questions.length === 0 ? (
                <div className="text-center py-12 bg-slate-50 rounded-2xl border border-slate-100">
                    <p className="text-sm text-slate-500 mb-6">Test your mastery of this lecture transcript.</p>
                    <button onClick={generateQuiz} className="btn-primary">Start Quiz</button>
                </div>
            ) : (
                <div className="space-y-8">
                    {questions.map((q, i) => (
                        <div key={i} className="p-6 bg-slate-50 rounded-2xl border border-slate-100 relative">
                            <span className="absolute -top-3 -left-3 w-8 h-8 bg-white border border-slate-100 shadow-sm rounded-full flex items-center justify-center text-xs font-bold text-slate-400">
                                {i + 1}
                            </span>
                            <h4 className="font-bold text-slate-800 mb-4">{q.question}</h4>
                            <div className="grid md:grid-cols-2 gap-3">
                                {q.options.map((opt, optIdx) => {
                                    const isSelected = answers[i] === optIdx;
                                    const isCorrect = q.correctAnswerIndex === optIdx;
                                    const showResult = submitted;

                                    let style = "bg-white border-slate-200 text-slate-600 hover:border-primary-500/30";
                                    if (isSelected && !showResult) style = "bg-primary-50 border-primary-500 text-primary-700 shadow-sm";
                                    if (showResult) {
                                        if (isCorrect) style = "bg-emerald-50 border-emerald-500 text-emerald-700 font-medium";
                                        else if (isSelected) style = "bg-red-50 border-red-500 text-red-700 font-medium";
                                        else style = "bg-white border-slate-100 text-slate-400 opacity-60";
                                    }

                                    return (
                                        <button
                                            key={optIdx}
                                            disabled={submitted}
                                            onClick={() => setAnswers(prev => ({ ...prev, [i]: optIdx }))}
                                            className={`p-4 rounded-xl border text-sm text-left transition-all flex justify-between items-center ${style}`}
                                        >
                                            {opt}
                                            {showResult && isCorrect && <CheckCircle2 size={16} />}
                                            {showResult && isSelected && !isCorrect && <XCircle size={16} />}
                                        </button>
                                    );
                                })}
                            </div>
                            {submitted && (
                                <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }} className="mt-4 pt-4 border-t border-slate-200/50 flex gap-3 text-xs leading-relaxed">
                                    <AlertCircle size={16} className="text-primary-500 shrink-0" />
                                    <p className="text-slate-500"><span className="font-bold text-slate-700">Explanation:</span> {q.explanation}</p>
                                </motion.div>
                            )}
                        </div>
                    ))}

                    {!submitted ? (
                        <button
                            onClick={handleSubmit}
                            disabled={Object.keys(answers).length < questions.length}
                            className="w-full btn-primary py-4 disabled:opacity-50"
                        >
                            Complete Quiz
                        </button>
                    ) : (
                        <div className="flex flex-col items-center gap-4 py-6 text-center">
                            <div className="text-4xl font-black text-slate-800">
                                {score} <span className="text-slate-300">/</span> {questions.length}
                            </div>
                            <p className="text-sm font-bold text-slate-500 uppercase tracking-widest">
                                {score === questions.length ? 'Perfect Score!' : 'Great effort!'}
                            </p>
                            <button onClick={generateQuiz} className="text-primary-500 text-xs font-bold hover:underline">Try Another Quiz</button>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}
