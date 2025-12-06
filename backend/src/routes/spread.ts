import { Router } from 'express';
import { z } from 'zod';
import { validate } from '../middleware/validation.js';
import { spreadPredictionService } from '../services/spreadPredictionService.js';

const router = Router();

// Validation schemas
const spreadPredictionSchema = z.object({
    bounds_north: z.number().min(-90).max(90),
    bounds_south: z.number().min(-90).max(90),
    bounds_east: z.number().min(-180).max(180),
    bounds_west: z.number().min(-180).max(180),
    disease_type: z.string().optional(),
});

// POST /api/v1/spread/predict - Get geographic spread prediction
router.post('/predict', validate(spreadPredictionSchema), async (req, res, next) => {
    try {
        const { bounds_north, bounds_south, bounds_east, bounds_west, disease_type } = req.body;

        const bounds = {
            north: bounds_north,
            south: bounds_south,
            east: bounds_east,
            west: bounds_west,
        };

        // Get spread prediction
        const prediction = await spreadPredictionService.predictSpread(bounds, disease_type);

        res.status(200).json({
            data: prediction,
            message: 'Spread prediction generated successfully',
        });
    } catch (error) {
        next(error);
    }
});

export { router as spreadRoutes };
