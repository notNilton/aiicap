import { useState, useEffect } from 'react';
import api, { ImageData } from '../services/api';

export default function GalleryPage() {
    const [images, setImages] = useState<ImageData[]>([]);
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

    const handleDelete = async (id: number) => {
        if (!confirm('Deseja realmente excluir esta imagem?')) return;

        try {
            await api.deleteImage(id);
            setImages(images.filter(img => img.id !== id));
        } catch (err) {
            console.error('Failed to delete image:', err);
        }
    };

    return (
        <div className="page gallery-page">
            <h1>🖼️ Galeria</h1>

            <div className="filter-section">
                <button
                    className={filter === 'all' ? 'active' : ''}
                    onClick={() => setFilter('all')}
                >
                    Todas
                </button>
                <button
                    className={filter === 'generated' ? 'active' : ''}
                    onClick={() => setFilter('generated')}
                >
                    Geradas
                </button>
                <button
                    className={filter === 'corrected' ? 'active' : ''}
                    onClick={() => setFilter('corrected')}
                >
                    Corrigidas
                </button>
            </div>

            {loading ? (
                <div className="loading">Carregando...</div>
            ) : images.length === 0 ? (
                <div className="empty-state">
                    <p>Nenhuma imagem encontrada.</p>
                    <p>Gere sua primeira imagem na aba "Gerar"!</p>
                </div>
            ) : (
                <div className="image-grid">
                    {images.map(image => (
                        <div key={image.id} className="image-card">
                            <img
                                src={`/uploads/${image.is_corrected ? 'corrected' : 'generated'}_${image.id}.png`}
                                alt={image.prompt || 'Image'}
                            />
                            <div className="image-info">
                                <p className="prompt">{image.prompt}</p>
                                <p className="meta">
                                    {image.size} • {new Date(image.created_at).toLocaleDateString('pt-BR')}
                                </p>
                            </div>
                            <div className="image-actions">
                                <button onClick={() => handleDelete(image.id)}>🗑️</button>
                            </div>
                        </div>
                    ))}
                </div>
            )}

            <div className="pagination">
                <button disabled={page === 1} onClick={() => setPage(p => p - 1)}>
                    ← Anterior
                </button>
                <span>Página {page}</span>
                <button onClick={() => setPage(p => p + 1)}>
                    Próxima →
                </button>
            </div>
        </div>
    );
}
