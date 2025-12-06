import { getPool } from '../src/database/connection.js';
import { v4 as uuidv4 } from 'uuid';

const CITIES = [
  { name: 'New York City', lat: 40.7128, lng: -74.0060, region: 'North America' },
  { name: 'Los Angeles', lat: 34.0522, lng: -118.2437, region: 'North America' },
  { name: 'London', lat: 51.5074, lng: -0.1278, region: 'Europe' },
  { name: 'Tokyo', lat: 35.6762, lng: 139.6503, region: 'Asia' },
  { name: 'Johannesburg', lat: -26.2041, lng: 28.0473, region: 'Africa' },
  { name: 'Sao Paulo', lat: -23.5505, lng: -46.6333, region: 'South America' },
  { name: 'Sydney', lat: -33.8688, lng: 151.2093, region: 'Australia' },
  { name: 'Mumbai', lat: 19.0760, lng: 72.8777, region: 'Asia' },
  { name: 'Paris', lat: 48.8566, lng: 2.3522, region: 'Europe' },
  { name: 'Cairo', lat: 30.0444, lng: 31.2357, region: 'Africa' }
];

const DISEASES = [
  { type: 'covid-19', severity: 3, symptoms: ['fever', 'cough', 'fatigue', 'loss_of_taste'] },
  { type: 'influenza', severity: 2, symptoms: ['fever', 'body_aches', 'chills'] },
  { type: 'measles', severity: 4, symptoms: ['rash', 'fever', 'cough'] },
  { type: 'dengue', severity: 3, symptoms: ['high_fever', 'headache', 'joint_pain'] },
  { type: 'malaria', severity: 4, symptoms: ['fever', 'chills', 'sweating'] }
];

async function seedDatabase() {
  const pool = getPool();

  try {
    console.log('🌱 Seeding database with comprehensive historical data...');

    // Clear existing data
    await pool.query('TRUNCATE TABLE outbreak_reports CASCADE');
    await pool.query('TRUNCATE TABLE ml_predictions CASCADE');
    console.log('🧹 Cleared existing data');

    const reports = [];
    const today = new Date();
    const DAYS_OF_HISTORY = 90;

    for (const city of CITIES) {
      for (const disease of DISEASES) {
        // Create a trend for this city-disease pair
        // Random start phase for sine wave to make trends different
        const phase = Math.random() * Math.PI * 2;
        const baseCases = Math.floor(Math.random() * 50) + 10;

        for (let i = DAYS_OF_HISTORY; i >= 0; i--) {
          const date = new Date(today);
          date.setDate(date.getDate() - i);

          // Generate realistic-looking case count with seasonality/trend
          // Use a sine wave + random noise
          const trend = Math.sin((i / 30) * Math.PI + phase);
          const noise = (Math.random() - 0.5) * 10;
          let caseCount = Math.round(baseCases + (trend * 20) + noise);
          caseCount = Math.max(1, caseCount); // Ensure at least 1 case

          // Occasionally spike cases to simulate outbreak
          if (Math.random() < 0.05) {
            caseCount *= 2;
          }

          reports.push({
            id: uuidv4(),
            disease_type: disease.type,
            latitude: city.lat + (Math.random() - 0.5) * 0.1, // Slight jitter
            longitude: city.lng + (Math.random() - 0.5) * 0.1,
            case_count: caseCount,
            severity_level: disease.severity,
            confidence: 0.8 + (Math.random() * 0.2), // 0.8 - 1.0
            symptoms: disease.symptoms,
            location_name: city.name,
            data_source: 'simulation',
            created_at: date.toISOString()
          });
        }
      }
    }

    console.log(`📝 Generating ${reports.length} reports...`);

    // Batch insert
    const batchSize = 100;
    for (let i = 0; i < reports.length; i += batchSize) {
      const batch = reports.slice(i, i + batchSize);

      // Construct query
      // We need to handle the dynamic number of values
      // ($1, $2, ...), ($10, $11, ...)

      let query = `
        INSERT INTO outbreak_reports (
          disease_type, latitude, longitude, case_count, 
          severity_level, confidence, symptoms, location_name, data_source, created_at
        ) VALUES 
      `;

      const values: any[] = [];
      const placeholders: string[] = [];

      batch.forEach((report, idx) => {
        const offset = idx * 10;
        placeholders.push(`($${offset + 1}, $${offset + 2}, $${offset + 3}, $${offset + 4}, $${offset + 5}, $${offset + 6}, $${offset + 7}, $${offset + 8}, $${offset + 9}, $${offset + 10})`);
        values.push(
          report.disease_type,
          report.latitude,
          report.longitude,
          report.case_count,
          report.severity_level,
          report.confidence,
          report.symptoms,
          report.location_name,
          report.data_source,
          report.created_at
        );
      });

      query += placeholders.join(', ');

      await pool.query(query, values);
      process.stdout.write('.');
    }

    console.log('\n✅ Database seeded successfully!');

  } catch (error) {
    console.error('\n❌ Seeding failed:', error);
    process.exit(1);
  } finally {
    await pool.end();
  }
}

// Run seeding if this script is executed directly
if (import.meta.url === `file://${process.argv[1]}`) {
  seedDatabase();
}
