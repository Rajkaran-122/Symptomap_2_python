import { Pool, PoolClient } from 'pg';
import { createClient } from 'redis';

// Database connection pool
let pool: Pool | null = null;
let redisClient: ReturnType<typeof createClient> | null = null;
let initPromise: Promise<void> | null = null;

export const initDatabase = async (): Promise<void> => {
  // If initialization is already in progress, wait for it
  if (initPromise) {
    return initPromise;
  }

  // Create the initialization promise
  initPromise = (async () => {
    try {
      // Initialize PostgreSQL connection pool
      pool = new Pool({
        connectionString: process.env.DATABASE_URL || 'postgresql://symptomap:password@localhost:5432/symptomap',
        max: 20,
        idleTimeoutMillis: 30000,
        connectionTimeoutMillis: 2000,
      });

      // Test PostgreSQL connection
      const client = await pool.connect();
      await client.query('SELECT NOW()');
      client.release();
      console.log('✅ PostgreSQL connected');

    } catch (error) {
      console.error('❌ PostgreSQL connection failed:', error);
      console.log('⚠️  Continuing without database connection...');
    }

    // Initialize Redis connection separately
    try {
      redisClient = createClient({
        url: process.env.REDIS_URL || 'redis://localhost:6379',
        socket: {
          reconnectStrategy: (retries) => {
            if (retries > 10) {
              console.error('Redis reconnection failed after 10 attempts');
              return new Error('Redis reconnection failed');
            }
            return retries * 50;
          },
        },
      });

      redisClient.on('error', (err) => {
        console.error('Redis Client Error:', err);
      });

      redisClient.on('connect', () => {
        console.log('✅ Redis connected');
      });

      redisClient.on('ready', () => {
        console.log('✅ Redis ready');
      });

      await redisClient.connect();

    } catch (error) {
      console.error('❌ Redis connection failed:', error);
      console.log('⚠️  Continuing without Redis connection...');
      redisClient = null;
    }
  })();

  return initPromise;
};

// Mock Pool for offline mode
class MockPool {
  async connect() {
    return {
      query: async (text: string, params: any[]) => {
        console.log('⚠️  [MOCK DB] Query:', text.substring(0, 50) + '...');
        return { rows: [], rowCount: 0 };
      },
      release: () => { },
    };
  }

  async query(text: string, params?: any[]) {
    console.log('⚠️  [MOCK DB] Query:', text.substring(0, 50) + '...');

    // Return dummy data for specific queries if needed
    if (text.includes('SELECT NOW()')) {
      return { rows: [{ now: new Date() }], rowCount: 1 };
    }

    // Return dummy prediction ID for inserts
    if (text.includes('INSERT INTO ml_predictions')) {
      return { rows: [{ id: 'mock-id-' + Date.now(), created_at: new Date() }], rowCount: 1 };
    }

    // Return dummy historical data for outbreak reports
    if (text.includes('FROM outbreak_reports')) {
      console.log('⚠️  [MOCK DB] Generating dummy outbreak data...');
      const dummyRows = [];
      const today = new Date();

      // If this is a SELECT with location columns (outbreak data)
      if (text.includes('latitude') || text.includes('lat')) {
        // Generate mock outbreak locations (simulating hospitals reporting outbreaks)
        const outbreaks = [
          { lat: 28.6139, lng: 77.2090, disease: 'Viral Fever', cases: 45, severity: 3 },
          { lat: 28.5355, lng: 77.3910, disease: 'Viral Fever', cases: 32, severity: 2 },
          { lat: 28.7041, lng: 77.1025, disease: 'Dengue', cases: 18, severity: 2 },
          { lat: 28.4595, lng: 77.0266, disease: 'COVID-19', cases: 67, severity: 4 },
          { lat: 28.6692, lng: 77.4538, disease: 'Influenza', cases: 25, severity: 1 },
        ];

        outbreaks.forEach(outbreak => {
          dummyRows.push({
            latitude: outbreak.lat,
            longitude: outbreak.lng,
            lat: outbreak.lat,
            lng: outbreak.lng,
            case_count: outbreak.cases,
            cases: outbreak.cases,
            disease_type: outbreak.disease,
            disease: outbreak.disease,
            severity_level: outbreak.severity,
            severity: outbreak.severity,
            created_at: new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000) // Random time in last 7 days
          });
        });

        return { rows: dummyRows, rowCount: dummyRows.length };
      }

      // Otherwise, return time-series data (for analytics)
      for (let i = 0; i < 90; i++) {
        const date = new Date(today);
        date.setDate(today.getDate() - (90 - i));

        // Generate a simple curve: 10 + 5 * sin(i/10) + random noise
        const cases = Math.max(0, Math.round(100 + 50 * Math.sin(i / 10) + Math.random() * 20));

        dummyRows.push({
          date: date.toISOString().split('T')[0],
          total_cases: cases,
          avg_severity: 2.5,
          outbreak_count: 1
        });
      }
      return { rows: dummyRows, rowCount: dummyRows.length };
    }

    return { rows: [], rowCount: 0 };
  }

  async end() {
    console.log('⚠️  [MOCK DB] Pool ended');
  }
}

export const getPool = (): Pool => {
  if (!pool) {
    // Initialize pool if not already done
    if (!initPromise) {
      initDatabase().catch(console.error);
    }

    // If still no pool (initialization failed or in progress), return Mock Pool
    console.warn('⚠️  Database not connected. Using Mock Pool.');
    return new MockPool() as any as Pool;
  }
  return pool;
};

export const getRedisClient = () => {
  if (redisClient) {
    return redisClient;
  }

  // If Redis hasn't been initialized yet but is in progress, return null
  // It will be available once initDatabase completes
  if (!redisClient && !initPromise) {
    console.warn('⚠️  Redis client not yet initialized');
  }

  return redisClient;
};

export const closeConnections = async (): Promise<void> => {
  if (pool) {
    await pool.end();
    pool = null;
  }

  if (redisClient) {
    await redisClient.quit();
    redisClient = null;
  }
};