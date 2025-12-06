import { describe, it, expect, vi, beforeEach } from 'vitest';
import { predictionService } from '../src/services/predictionService';
import { getPool, getRedisClient } from '../src/database/connection';

// Mock dependencies
vi.mock('../src/database/connection', () => ({
    getPool: vi.fn(),
    getRedisClient: vi.fn(),
}));

describe('PredictionService', () => {
    let mockPool: any;
    let mockRedis: any;

    beforeEach(() => {
        mockPool = {
            query: vi.fn(),
        };
        mockRedis = {
            get: vi.fn(),
            setex: vi.fn(),
            keys: vi.fn(),
            del: vi.fn(),
        };
        (getPool as any).mockReturnValue(mockPool);
        (getRedisClient as any).mockReturnValue(mockRedis);

        // Reset singleton instance's dependencies if possible or just rely on mocks
        // Since predictionService is instantiated at module level, we might need to rely on the mocks being active when it runs
        // or we can try to re-instantiate it if we exported the class. 
        // For this test, we assume the mocks work because vitest hoists them.
    });

    it('should generate predictions using linear regression when enough data exists', async () => {
        // Mock historical data
        const mockHistoricalData = [
            { date: '2023-01-01', total_cases: 10, avg_severity: 2, outbreak_count: 1 },
            { date: '2023-01-02', total_cases: 12, avg_severity: 2, outbreak_count: 1 },
            { date: '2023-01-03', total_cases: 15, avg_severity: 2.5, outbreak_count: 1 },
            { date: '2023-01-04', total_cases: 18, avg_severity: 3, outbreak_count: 1 },
            { date: '2023-01-05', total_cases: 22, avg_severity: 3, outbreak_count: 1 },
        ];

        mockPool.query
            .mockResolvedValueOnce({ rows: mockHistoricalData }) // getHistoricalData
            .mockResolvedValueOnce({ rows: [{ id: 'pred-123', created_at: new Date() }] }); // insert

        const result = await predictionService.generatePrediction({
            region: { north: 10, south: 0, east: 10, west: 0 },
            horizonDays: 3,
        });

        expect(result).toBeDefined();
        expect(result.predictions).toHaveLength(3);
        // 10, 12, 15, 18, 22 -> increasing trend
        expect(result.predictions[0].predictedCases).toBeGreaterThan(22);
    });

    it('should return conservative predictions when not enough data', async () => {
        mockPool.query.mockResolvedValueOnce({ rows: [] }); // No data
        mockPool.query.mockResolvedValueOnce({ rows: [{ id: 'pred-empty', created_at: new Date() }] });

        const result = await predictionService.generatePrediction({
            region: { north: 10, south: 0, east: 10, west: 0 },
            horizonDays: 3,
        });

        expect(result.predictions).toHaveLength(3);
        expect(result.predictions[0].predictedCases).toBe(0);
    });

    it('should list models correctly', async () => {
        const models = await predictionService.listModels();
        expect(models).toHaveLength(1);
        expect(models[0].id).toBe('stat-linear-v1');
    });
});
