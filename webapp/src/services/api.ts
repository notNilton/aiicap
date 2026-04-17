const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

export interface GenerationRequest {
    prompt: string;
    size?: string;
    quality?: string;
    style?: string;
}

export interface GenerationResponse {
    id: number;
    status: string;
    prompt: string;
    message: string;
}

export interface CorrectionRequest {
    image_id: number;
    correction_type: string;
    parameters?: Record<string, unknown>;
}

export interface ApiImage {
    id: number;
    prompt?: string;
    model?: string;
    size?: string;
    created_at: string;
    is_corrected: boolean;
}

class ApiClient {
    private baseUrl: string;

    constructor(baseUrl: string = API_BASE_URL) {
        this.baseUrl = baseUrl;
    }

    private async request<T>(endpoint: string, options?: RequestInit): Promise<T> {
        const response = await fetch(`${this.baseUrl}${endpoint}`, {
            headers: {
                'Content-Type': 'application/json',
                ...options?.headers,
            },
            ...options,
        });

        if (!response.ok) {
            const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
            throw new Error(error.detail || `HTTP error ${response.status}`);
        }

        return response.json();
    }

    // Health check
    async healthCheck() {
        return this.request<{ status: string }>('/health');
    }

    // Images
    async listImages(page = 1, perPage = 20, type: 'all' | 'generated' | 'corrected' = 'all') {
        return this.request<{ images: ApiImage[]; total: number }>(
            `/images?page=${page}&per_page=${perPage}&type=${type}`
        );
    }

    async getImage(id: number) {
        return this.request<ApiImage>(`/images/${id}`);
    }

    async deleteImage(id: number) {
        return this.request(`/images/${id}`, { method: 'DELETE' });
    }

    // Generation
    async generateImage(request: GenerationRequest): Promise<GenerationResponse> {
        return this.request<GenerationResponse>('/generate', {
            method: 'POST',
            body: JSON.stringify(request),
        });
    }

    async getGenerationStatus(id: number) {
        return this.request<{ id: number; status: string; image_url?: string; error?: string }>(
            `/generate/status/${id}`
        );
    }

    async getGenerationHistory(limit = 20) {
        return this.request<{ generations: unknown[] }>(`/generate/history?limit=${limit}`);
    }

    // Correction
    async correctImage(request: CorrectionRequest) {
        return this.request(`/correct`, {
            method: 'POST',
            body: JSON.stringify(request),
        });
    }

    async getCorrectionTypes() {
        return this.request<{ types: unknown[] }>('/correct/types');
    }

    async uploadAndCorrect(file: File, correctionType: string, parameters?: Record<string, unknown>): Promise<Blob> {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('correction_type', correctionType);
        if (parameters) {
            formData.append('parameters', JSON.stringify(parameters));
        }

        const response = await fetch(`${this.baseUrl}/correct/upload`, {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) {
            throw new Error('Failed to process image');
        }

        return response.blob();
    }
}

export const api = new ApiClient();
export default api;
