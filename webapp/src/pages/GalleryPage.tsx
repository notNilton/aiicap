import { useState, useEffect } from 'react';
import api, { type ApiImage } from '../services/api';
import './GalleryPage.style.css';

export default function GalleryPage() {
    const [images, setImages] = useState<ApiImage[]>([]);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState<'all' | 'generated' | 'corrected'>('all');
    const [page, setPage] = useState(1);

    useEffect(() => {
        loadImages();
    }, [filter, page]);

    const loadImages = async () => {
        setLoading(true);
        try {
            const result = await api.listImages(page, 20, filter);
            setImages(result.images);
        } catch (err) {
            console.error('Failed to load images:', err);
        } finally {
            setLoading(false);
        }
    };

    const handleDelete = async (id: number, e: React.MouseEvent) => {
        e.stopPropagation();
        if (!confirm('Delete this image?')) return;

        try {
            await api.deleteImage(id);
            setImages(images.filter(img => img.id !== id));
        } catch (err) {
            console.error('Failed to delete image:', err);
        }
    };

    return (
        <div className="gallery-page">
            <header className="gallery-header">
                <h1 className="gallery-title">Gallery</h1>

                <div className="filter-group">
                    {(['all', 'generated', 'corrected'] as const).map((TYPE) => (
                        <button
                            key={TYPE}
                            className={`filter-btn ${filter === TYPE ? 'active' : ''}`}
                            onClick={() => setFilter(TYPE)}
                        >
                            {TYPE.charAt(0).toUpperCase() + TYPE.slice(1)}
                        </button>
                    ))}
                </div>
            </header>

            {loading && images.length === 0 ? (
                <div className="loading-spinner">Loading...</div>
            ) : images.length === 0 ? (
                <div className="empty-state">
                    <p>No images found</p>
                </div>
            ) : (
                <div className="gallery-grid">
                    {images.map(image => {
                        const imageUrl = `/uploads/${image.is_corrected ? 'corrected' : 'generated'}_${image.id}.png`;
                        return (
                            <div
                                key={image.id}
                                className="image-card"
                                onClick={() => window.open(imageUrl, '_blank')}
                                role="button"
                                tabIndex={0}
                                onKeyDown={(e) => {
                                    if (e.key === 'Enter' || e.key === ' ') {
                                        window.open(imageUrl, '_blank');
                                    }
                                }}
                            >
                                <img
                                    src={imageUrl}
                                    alt={image.prompt || 'Untitled'}
                                    loading="lazy"
                                />
                                <div className="card-overlay">
                                    <p className="card-prompt">{image.prompt}</p>
                                    <div className="card-meta">
                                        <span>{image.size}</span>
                                        <button
                                            className="delete-btn"
                                            onClick={(e) => handleDelete(image.id, e)}
                                            title="Delete"
                                        >
                                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                                <polyline points="3 6 5 6 21 6"></polyline>
                                                <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                                            </svg>
                                        </button>
                                    </div>
                                </div>
                            </div>
                        );
                    })}
                </div>
            )}

            <div className="pagination">
                <button
                    className="page-btn"
                    disabled={page === 1}
                    onClick={() => setPage(p => p - 1)}
                >
                    Prev
                </button>
                <span style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>{page}</span>
                <button
                    className="page-btn"
                    onClick={() => setPage(p => p + 1)}
                >
                    Next
                </button>
            </div>
        </div>
    );
}
