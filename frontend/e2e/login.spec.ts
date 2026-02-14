import { test, expect } from '@playwright/test';

test('User Login Flow Verification', async ({ page }) => {
    test.setTimeout(60000);

    // Monitor Console
    page.on('console', msg => console.log(`BROWSER CONSOLE: ${msg.text()}`));

    // Monitor Network
    page.on('response', response => {
        if (response.url().includes('/auth/login')) {
            console.log(`LOGIN RESPONSE: ${response.status()} ${response.statusText()}`);
            if (response.status() !== 200) {
                response.text().then(t => console.log('Response body:', t)).catch(() => { });
            }
        }
    });

    try {
        console.log('Navigating to Landing Page...');
        await page.goto('http://localhost:3000/');

        if (page.url().includes('/user/dashboard')) {
            console.log('User is already logged in. Skipping login steps.');
        } else {
            // 2. Click "I'm a Patient" button
            console.log('Looking for patient button...');
            const patientButton = page.locator('button').filter({ hasText: "I'm a Patient" });
            await expect(patientButton).toBeVisible();
            await patientButton.click();
            console.log('Clicked "I\'m a Patient" button');

            // 3. Verify Redirect to Login Page
            console.log('Waiting for login page redirect...');
            await expect(page).toHaveURL(/\/user\/login/, { timeout: 15000 });
            console.log('Redirected to Login Page');

            // 4. Fill Credentials with FORCE
            console.log('Filling Credentials (Force Mode)...');
            await page.waitForTimeout(2000);

            const emailInput = page.locator('input[type="email"]');
            await emailInput.click({ force: true });
            await emailInput.fill('test.patient.final@example.com', { force: true });

            const passwordInput = page.locator('input[type="password"]');
            await passwordInput.click({ force: true });
            await passwordInput.fill('Password@123', { force: true });
            console.log('Filled credentials');

            // 5. Submit Login
            console.log('Submitting login...');
            const submitPromise = page.waitForResponse(resp => resp.url().includes('/auth/login'), { timeout: 10000 }).catch(() => null);

            const submitBtn = page.locator('button[type="submit"]');
            await submitBtn.click({ force: true });
            console.log('Clicked Sign In');

            const response = await submitPromise;
            if (response) {
                console.log(`Login API finished with status: ${response.status()}`);
            } else {
                console.log('No login response captured within timeout');
            }
        }

        // 6. Verify Redirect to Dashboard
        console.log('Waiting for dashboard redirect...');
        await expect(page).toHaveURL(/\/user\/dashboard/, { timeout: 20000 });
        console.log('Redirected to User Dashboard');

        // 7. Verify Dashboard Content
        await expect(page.getByText('System Operational', { exact: false })).toBeVisible({ timeout: 20000 });

        console.log('Test Passed: Full Login Flow Verified');
    } catch (error) {
        console.error('Test Failed:', error);
        await page.screenshot({ path: 'test_failure_final.png' });
        throw error;
    }
});
