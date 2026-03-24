"use client";
import { useState, useEffect } from 'react';
import axios from 'axios';
import { Loader2, Image as ImageIcon } from 'lucide-react';

interface ExtractedImage {
    url: string;
    caption: string;
    page: number;
}

export default function Gallery({ collectionId }: { collectionId: string }) {
    const [images, setImages] = useState<ExtractedImage[]>([]);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        const fetchImages = async () => {
            try {
                setIsLoading(true);
                const res = await axios.get(`http://localhost:8000/api/v1/learning/metadata/${collectionId}`);
                if (res.data.images) {
                    setImages(res.data.images.map((img: any) => ({
                        ...img,
                        url: `http://localhost:8000${img.url}`
                    })));
                }
            } catch (err) {
                console.error("Failed to load images", err);
            } finally {
                setIsLoading(false);
            }
        };
        fetchImages();
    }, [collectionId]);

    if (isLoading) {
        return (
            <div className="flex-1 flex items-center justify-center p-8 bg-slate-50/30 rounded-3xl h-[600px]">
                <Loader2 className="animate-spin text-primary-500 w-8 h-8" />
            </div>
        );
    }

    if (images.length === 0) {
        return (
            <div className="flex-1 flex flex-col items-center justify-center p-8 bg-slate-50/30 rounded-3xl h-[600px]">
                <ImageIcon className="w-16 h-16 text-slate-300 mb-4" />
                <h3 className="text-xl font-bold text-slate-700">No Figures Found</h3>
                <p className="text-slate-500 mt-2 text-center max-w-sm">
                    We couldn't extract any images or figures from this lecture transcript.
                </p>
            </div>
        );
    }

    return (
        <div className="bg-slate-50/30 rounded-3xl p-6 lg:p-10 min-h-[600px]">
            <div className="mb-8">
                <h2 className="text-2xl font-black text-slate-800 tracking-tight">Extracted Figures</h2>
                <p className="text-slate-500 mt-2">Visuals and diagrams found in your document.</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {images.map((img, idx) => (
                    <div key={idx} className="bg-white rounded-2xl overflow-hidden border border-slate-100 shadow-sm hover:shadow-lg hover:-translate-y-1 transition-all duration-300 group cursor-pointer">
                        <div className="aspect-[4/3] bg-slate-100 flex items-center justify-center overflow-hidden relative">
                            <img
                                src={img.url}
                                alt={img.caption}
                                className="w-full h-full object-contain p-2"
                                loading="lazy"
                            />
                            <div className="absolute inset-0 bg-slate-900/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                                <ImageIcon className="text-white w-8 h-8 opacity-75" />
                            </div>
                        </div>
                        <div className="p-4 bg-white border-t border-slate-50">
                            <span className="text-[10px] font-bold uppercase tracking-wider text-primary-500 mb-1 block">Page {img.page}</span>
                            <p className="text-sm font-medium text-slate-700 leading-snug line-clamp-2">{img.caption}</p>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}
