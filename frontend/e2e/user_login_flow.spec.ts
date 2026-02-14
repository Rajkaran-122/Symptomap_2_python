
import { test, expect } from '@playwright/test';

test('User Login Flow - Dashboard Redirect', async ({ page }) => {
    // 1. Go to User Login Page
    await page.goto('http://localhost:3000/user/login');

    // 2. Fill Credentials
    // Assuming you have a test user. If not, we might need to register one first or use known credentials.
    // Based on previous logs, 'test.patient.final@example.com' seems to be a valid user.
    await page.fill('input[type="email"]', 'test.patient.final@example.com');
    await page.fill('input[type="password"]', 'Password@123'); // Adjust if password differs

    // 3. Click Login
    await page.click('button[type="submit"]');

    // 4. Expect Redirect to /user/dashboard
    // We increase timeout just in case of backend latency
    await expect(page).toHaveURL(/.*\/user\/dashboard/, { timeout: 15000 });

    console.log('✅ Successfully redirected to User Dashboard');
});
