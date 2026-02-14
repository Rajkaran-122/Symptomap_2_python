
import { test, expect } from '@playwright/test';

test('User Signup and Login Flow', async ({ page }) => {
    // Generate unique user
    const uniqueId = Date.now();
    const email = `test.user.${uniqueId}@example.com`;
    const password = 'Password@123';
    const name = `Test User ${uniqueId}`;

    console.log(`Starting test with email: ${email}`);

    // Listen for console logs
    page.on('console', msg => console.log(`[BROWSER] ${msg.text()}`));

    // 1. Go to Register Page
    await page.goto('http://localhost:3000/register');

    // 2. Fill Registration Form
    await page.fill('input[name="full_name"]', name);
    await page.fill('input[name="email"]', email);
    await page.fill('input[name="phone"]', '+919876543210');
    await page.fill('input[name="password"]', password);

    // Take screenshot before submit
    await page.screenshot({ path: 'before_register.png' });

    // 3. Submit Registration
    await page.click('button[type="submit"]');
    console.log('Clicked submit...');

    // 4. Expect Redirect to /user/login
    console.log('Waiting for registration redirect...');
    try {
        await expect(page).toHaveURL(/.*\/user\/login/, { timeout: 15000 });
        console.log('✅ Registration successful, redirected to /user/login');
    } catch (e) {
        await page.screenshot({ path: 'register_fail.png' });
        const content = await page.content();
        console.log('Page content on fail:', content.substring(0, 1000));
        throw e;
    }

    // 5. Fill Login Form (already on /user/login)
    await page.fill('input[type="email"]', email);
    await page.fill('input[type="password"]', password);

    // 6. Click Sign In
    await page.click('button[type="submit"]');

    // 7. Expect Redirect to /user/dashboard
    console.log('Waiting for dashboard redirect...');
    try {
        await expect(page).toHaveURL(/.*\/user\/dashboard/, { timeout: 20000 });
        console.log('✅ Login successful, redirected to User Dashboard');
    } catch (e) {
        await page.screenshot({ path: 'login_fail.png' });
        throw e;
    }
});
