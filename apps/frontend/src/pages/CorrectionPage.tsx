import { useState, useRef } from 'react';
import api from '../services/api';

type CorrectionType = 'pixelation' | 'dithering' | 'palette_reduction' | 'color_correction';

const CORRECTION_OPTIONS: Record<CorrectionType, { label: string; params: Record<string, { label: string; type: string; default: number; min?: number; max?: number }> }> = {
    pixelation: {
        label: 'Pixelação',
        params: { pixel_size: { label: 'Tamanho do pixel', type: 'number', default: 128, min: 2, max: 512 } },
    },
    dithering: {
        label: 'Dithering',
        params: { levels: { label: 'Níveis', type: 'number', default: 10, min: 2, max: 256 } },
    },
    palette_reduction: {
        label: 'Redução de Paleta',
        params: { num_colors: { label: 'Número de cores', type: 'number', default: 16, min: 2, max: 256 } },
    },
    color_correction: {
        label: 'Correção de Cor',
        params: {
            block_width: { label: 'Largura do bloco', type: 'number', default: 4, min: 1, max: 16 },
            block_height: { label: 'Altura do bloco', type: 'number', default: 4, min: 1, max: 16 },
        },
    },
};

export default function CorrectionPage() {
    const [file, setFile] = useState<File | null>(null);
    const [preview, setPreview] = useState<string | null>(null);
    const [result, setResult] = useState<string | null>(null);
    const [correctionType, setCorrectionType] = useState<CorrectionType>('pixelation');
    const [params, setParams] = useState<Record<string, number>>({});
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);

    const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
        const selectedFile = e.target.files?.[0];
        if (selectedFile) {
            setFile(selectedFile);
            setPreview(URL.createObjectURL(selectedFile));
            setResult(null);
        }
    };

    const handleCorrect = async () => {
        if (!file) return;

        setLoading(true);
        setError(null);

        try {
            const correctionParams = { ...CORRECTION_OPTIONS[correctionType].params };
            const finalParams: Record<string, number> = {};

            for (const [key, config] of Object.entries(correctionParams)) {
                finalParams[key] = params[key] ?? config.default;
            }

            const blob = await api.uploadAndCorrect(file, correctionType, finalParams);
            setResult(URL.createObjectURL(blob));
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Erro ao processar imagem');
        } finally {
            setLoading(false);
        }
    };

    const handleDownload = () => {
        if (!result) return;
        const a = document.createElement('a');
        a.href = result;
        a.download = `corrected_${file?.name || 'image.png'}`;
        a.click();
    };

    return (
        <div className="page correction-page">
            <h1>🔧 Correção de Imagem</h1>

            <div className="upload-section">
                <input
                    ref={fileInputRef}
                    type="file"
                    accept="image/*"
                    onChange={handleFileSelect}
                    style={{ display: 'none' }}
                />
                <button className="btn-upload" onClick={() => fileInputRef.current?.click()}>
                    📁 Selecionar Imagem
                </button>
                {file && <span className="file-name">{file.name}</span>}
            </div>

            {preview && (
                <div className="preview-section">
                    <div className="image-compare">
                        <div>
                            <h3>Original</h3>
                            <img src={preview} alt="Preview" />
                        </div>
                        {result && (
                            <div>
                                <h3>Resultado</h3>
                                <img src={result} alt="Result" />
                            </div>
                        )}
                    </div>
                </div>
            )}

            <div className="controls-section">
                <div className="form-group">
                    <label>Tipo de Correção</label>
                    <select
                        value={correctionType}
                        onChange={(e) => {
                            setCorrectionType(e.target.value as CorrectionType);
                            setParams({});
                        }}
                    >
                        {Object.entries(CORRECTION_OPTIONS).map(([key, opt]) => (
                            <option key={key} value={key}>{opt.label}</option>
                        ))}
                    </select>
                </div>

                {Object.entries(CORRECTION_OPTIONS[correctionType].params).map(([key, config]) => (
                    <div key={key} className="form-group">
                        <label>{config.label}</label>
                        <input
                            type="number"
                            value={params[key] ?? config.default}
                            min={config.min}
                            max={config.max}
                            onChange={(e) => setParams({ ...params, [key]: parseInt(e.target.value) })}
                        />
                    </div>
                ))}

                <div className="button-group">
                    <button
                        className="btn-primary"
                        onClick={handleCorrect}
                        disabled={!file || loading}
                    >
                        {loading ? 'Processando...' : 'Aplicar Correção'}
                    </button>

                    {result && (
                        <button className="btn-secondary" onClick={handleDownload}>
                            💾 Baixar Resultado
                        </button>
                    )}
                </div>
            </div>

            {error && <div className="error-message">❌ {error}</div>}
        </div>
    );
}
