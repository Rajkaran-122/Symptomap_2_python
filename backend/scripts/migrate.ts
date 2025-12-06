import { getPool } from '../src/database/connection.js';
import fs from 'fs';
import path from 'path';

console.log('Migrate script loaded');

async function runMigrations() {
  console.log('STARTING MIGRATION');
  const pool = getPool();

  try {
    console.log('🔄 Running database migrations...');

    // Read the schema file
    const schemaPath = path.join(process.cwd(), 'src', 'database', 'schema.sql');
    const schema = fs.readFileSync(schemaPath, 'utf8');

    // Execute the schema
    await pool.query(schema);

    console.log('✅ Database migrations completed successfully');
    fs.writeFileSync('migration.log', 'SUCCESS');

  } catch (error) {
    console.error('❌ Migration failed:', error);
    fs.writeFileSync('migration.log', 'FAILED: ' + error);
    process.exit(1);
  } finally {
    await pool.end();
  }
}

// Run migrations
runMigrations();
