import axios from 'axios';

const ML_SERVICE_URL = process.env.ML_SERVICE_URL || 'http://localhost:8000';

export interface SEIRParams {
    population: number;
    initial_infected: number;
    initial_exposed?: number;
    initial_recovered?: number;
    beta: number;
    sigma: number;
    gamma: number;
    days: number;
}

export interface SEIRPredictionPoint {
    day: number;
    susceptible: number;
    exposed: number;
    infected: number;
    recovered: number;
}

export interface SEIRResponse {
    predictions: SEIRPredictionPoint[];
    peak_infected: number;
    peak_day: number;
}

export class MLServiceAdapter {
    private static instance: MLServiceAdapter;
    private baseUrl: string;

    private constructor() {
        this.baseUrl = ML_SERVICE_URL;
    }

    public static getInstance(): MLServiceAdapter {
        if (!MLServiceAdapter.instance) {
            MLServiceAdapter.instance = new MLServiceAdapter();
        }
        return MLServiceAdapter.instance;
    }

    async getSEIRPrediction(params: SEIRParams): Promise<SEIRResponse> {
        console.log(`[ML Adapter] Requesting SEIR prediction from: ${this.baseUrl}/predict/seir`);
        console.log(`[ML Adapter] Params:`, JSON.stringify(params));
        try {
            const response = await axios.post<SEIRResponse>(`${this.baseUrl}/predict/seir`, params);
            console.log(`[ML Adapter] Response received:`, response.status);
            return response.data;
        } catch (error) {
            console.error('[ML Adapter] Error calling ML service:', error);
            if (axios.isAxiosError(error)) {
                console.error('[ML Adapter] Axios error details:', {
                    message: error.message,
                    code: error.code,
                    response: error.response?.data
                });
            }
            throw new Error('Failed to get SEIR prediction from ML service');
        }
    }

    async getSpreadPrediction(params: any): Promise<any> {
        console.log(`[ML Adapter] Requesting spread prediction from: ${this.baseUrl}/predict/spread`);
        try {
            const response = await axios.post(`${this.baseUrl}/predict/spread`, params);
            console.log(`[ML Adapter] Spread prediction received`);
            return response.data;
        } catch (error) {
            console.error('[ML Adapter] Error calling spread prediction:', error);
            if (axios.isAxiosError(error)) {
                console.error('[ML Adapter] Axios error details:', {
                    message: error.message,
                    code: error.code,
                    response: error.response?.data
                });
            }
            throw new Error('Failed to get spread prediction from ML service');
        }
    }

    async checkHealth(): Promise<boolean> {
        try {
            const response = await axios.get(`${this.baseUrl}/health`);
            return response.status === 200 && response.data.status === 'healthy';
        } catch (error) {
            return false;
        }
    }
}

export const mlServiceAdapter = MLServiceAdapter.getInstance();
