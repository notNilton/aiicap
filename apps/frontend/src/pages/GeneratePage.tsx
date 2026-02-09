import { useState } from 'react';
import api from '../services/api';

interface GenerationState {
    loading: boolean;
    error: string | null;
    generationId: number | null;
    status: string;
    imageUrl: string | null;
}

export default function GeneratePage() {
    const [prompt, setPrompt] = useState('');
    const [size, setSize] = useState('1024x1024');
    const [quality, setQuality] = useState('standard');
    const [state, setState] = useState<GenerationState>({
        loading: false,
        error: null,
        generationId: null,
        status: '',
        imageUrl: null,
    });

    const handleGenerate = async () => {
        if (!prompt.trim()) return;

        setState({ ...state, loading: true, error: null, imageUrl: null });

        try {
            const response = await api.generateImage({ prompt, size, quality });
            setState(prev => ({
                ...prev,
                generationId: response.id,
                status: 'pending',
            }));

            // Poll for status
            pollStatus(response.id);
        } catch (err) {
            setState(prev => ({
                ...prev,
                loading: false,
                error: err instanceof Error ? err.message : 'Unknown error',
            }));
        }
    };

    const pollStatus = async (id: number) => {
        const poll = async () => {
            try {
                const status = await api.getGenerationStatus(id);
                setState(prev => ({
                    ...prev,
                    status: status.status,
                    imageUrl: status.image_url || null,
                }));

                if (status.status === 'completed') {
                    setState(prev => ({ ...prev, loading: false }));
                } else if (status.status === 'failed') {
                    setState(prev => ({
                        ...prev,
                        loading: false,
                        error: status.error || 'Generation failed',
                    }));
                } else {
                    setTimeout(poll, 2000);
                }
            } catch {
                setTimeout(poll, 2000);
            }
        };
        poll();
    };

    return (
        <div className="page generate-page">
            <h1>🎨 Gerar Imagem</h1>

            <div className="form-section">
                <div className="form-group">
                    <label htmlFor="prompt">Prompt</label>
                    <textarea
                        id="prompt"
                        value={prompt}
                        onChange={(e) => setPrompt(e.target.value)}
                        placeholder="Descreva a imagem que você quer gerar..."
                        rows={4}
                    />
                </div>

                <div className="form-row">
                    <div className="form-group">
                        <label htmlFor="size">Tamanho</label>
                        <select id="size" value={size} onChange={(e) => setSize(e.target.value)}>
                            <option value="256x256">256x256</option>
                            <option value="512x512">512x512</option>
                            <option value="1024x1024">1024x1024</option>
                        </select>
                    </div>

                    <div className="form-group">
                        <label htmlFor="quality">Qualidade</label>
                        <select id="quality" value={quality} onChange={(e) => setQuality(e.target.value)}>
                            <option value="standard">Standard</option>
                            <option value="hd">HD</option>
                        </select>
                    </div>
                </div>

                <button
                    className="btn-primary"
                    onClick={handleGenerate}
                    disabled={state.loading || !prompt.trim()}
                >
                    {state.loading ? 'Gerando...' : 'Gerar Imagem'}
                </button>
            </div>

            {state.error && (
                <div className="error-message">
                    ❌ {state.error}
                </div>
            )}

            {state.status && (
                <div className="status-message">
                    Status: {state.status}
                </div>
            )}

            {state.imageUrl && (
                <div className="result-section">
                    <h2>Resultado</h2>
                    <img src={state.imageUrl} alt="Generated" className="generated-image" />
                </div>
            )}
        </div>
    );
}
