
import { test, expect } from '@playwright/test';

test('Dashboard Protection Verification', async ({ page }) => {
    console.log('Navigating to /user/dashboard directly...');
    await page.goto('http://localhost:3000/user/dashboard');

    console.log('Checking for redirect to /user/login...');
    await expect(page).toHaveURL(/.*\/user\/login/);
    console.log('✅ Redirect confirmed.');
});
