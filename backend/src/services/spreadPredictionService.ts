import { mlServiceAdapter } from './mlServiceAdapter.js';
import { getPool } from '../database/connection.js';

interface GeographicBounds {
    north: number;
    south: number;
    east: number;
    west: number;
}

interface OutbreakData {
    lat: number;
    lng: number;
    cases: number;
    disease: string;
    severity: number;
}

interface RiskArea {
    name: string;
    lat: number;
    lng: number;
    risk_score: number;
    probability: number;
    estimated_cases: number;
    days_until_spread: number;
}

interface SpreadPredictionResult {
    current_outbreaks: OutbreakData[];
    high_risk_areas: RiskArea[];
    medium_risk_areas: RiskArea[];
    low_risk_areas: RiskArea[];
    risk_grid: Array<{ lat: number; lng: number; risk: number }>;
    generated_at: string;
    alert_summary: string[];
}

export class SpreadPredictionService {
    private static instance: SpreadPredictionService;

    private constructor() { }

    public static getInstance(): SpreadPredictionService {
        if (!SpreadPredictionService.instance) {
            SpreadPredictionService.instance = new SpreadPredictionService();
        }
        return SpreadPredictionService.instance;
    }

    /**
     * Get active outbreaks in a region from the database (or Mock DB)
     */
    async getActiveOutbreaks(bounds: GeographicBounds, diseaseType?: string): Promise<OutbreakData[]> {
        const pool = getPool();

        // Query for outbreaks in the last 14 days within bounds
        let query = `
      SELECT 
        latitude as lat,
        longitude as lng,
        case_count as cases,
        disease_type as disease,
        severity_level as severity
      FROM outbreak_reports
      WHERE latitude BETWEEN $1 AND $2
        AND longitude BETWEEN $3 AND $4
        AND created_at >= NOW() - INTERVAL '14 days'
    `;

        const params: any[] = [bounds.south, bounds.north, bounds.west, bounds.east];

        if (diseaseType) {
            query += ` AND disease_type = $5`;
            params.push(diseaseType);
        }

        query += ` ORDER BY created_at DESC LIMIT 50`;

        const result = await pool.query(query, params);
        return result.rows;
    }

    /**
     * Generate alert messages from prediction results
     */
    generateAlerts(outbreaks: OutbreakData[], highRiskAreas: RiskArea[]): string[] {
        const alerts: string[] = [];

        // Group outbreaks by disease
        const diseaseGroups = new Map<string, OutbreakData[]>();
        outbreaks.forEach(outbreak => {
            if (!diseaseGroups.has(outbreak.disease)) {
                diseaseGroups.set(outbreak.disease, []);
            }
            diseaseGroups.get(outbreak.disease)!.push(outbreak);
        });

        // Generate alerts for each disease
        diseaseGroups.forEach((outbreakList, disease) => {
            const totalCases = outbreakList.reduce((sum, o) => sum + o.cases, 0);

            // Find high-risk areas for this disease
            const affectedAreas = highRiskAreas.filter(area =>
                outbreakList.some(o =>
                    Math.abs(o.lat - area.lat) < 0.5 && Math.abs(o.lng - area.lng) < 0.5
                )
            ).slice(0, 3);

            if (affectedAreas.length > 0) {
                const areaNames = affectedAreas.map(a => a.name).join(', ');
                const minDays = Math.min(...affectedAreas.map(a => a.days_until_spread));
                const avgProbability = (affectedAreas.reduce((sum, a) => sum + a.probability, 0) / affectedAreas.length * 100).toFixed(0);

                alerts.push(
                    `${disease} detected (${totalCases} cases). High risk of spread to ${areaNames} in next ${minDays} days (${avgProbability}% probability)`
                );
            }
        });

        // If no specific alerts, generate general warning
        if (alerts.length === 0 && highRiskAreas.length > 0) {
            alerts.push(`${highRiskAreas.length} areas identified at high risk for disease spread. Enhanced monitoring recommended.`);
        }

        return alerts;
    }

    /**
     * Main method: Predict geographic spread
     */
    async predictSpread(
        bounds: GeographicBounds,
        diseaseType?: string
    ): Promise<SpreadPredictionResult> {
        // Step 1: Get active outbreaks
        const outbreaks = await this.getActiveOutbreaks(bounds, diseaseType);

        if (outbreaks.length === 0) {
            return {
                current_outbreaks: [],
                high_risk_areas: [],
                medium_risk_areas: [],
                low_risk_areas: [],
                risk_grid: [],
                generated_at: new Date().toISOString(),
                alert_summary: ['No active outbreaks detected in the region'],
            };
        }

        // Step 2: Call ML Service for spread prediction
        const spreadResult = await mlServiceAdapter.getSpreadPrediction({
            outbreaks: outbreaks.map(o => ({
                lat: o.lat,
                lng: o.lng,
                cases: o.cases,
                disease: o.disease,
                severity: o.severity,
            })),
            bounds: {
                north: bounds.north,
                south: bounds.south,
                east: bounds.east,
                west: bounds.west,
            },
        });

        // Step 3: Generate alerts
        const alerts = this.generateAlerts(outbreaks, spreadResult.high_risk_areas);

        return {
            current_outbreaks: outbreaks,
            ...spreadResult,
            generated_at: new Date().toISOString(),
            alert_summary: alerts,
        };
    }
}

export const spreadPredictionService = SpreadPredictionService.getInstance();
