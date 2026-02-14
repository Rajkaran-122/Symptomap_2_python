
import { test, expect } from '@playwright/test';

test('Landing Page Link Verification', async ({ page }) => {
    // 1. Go to Landing Page
    await page.goto('http://localhost:3000');
    await expect(page).toHaveTitle(/SymptoMap/);

    // 2. Check Hero "View Live Map" -> /user/map
    // Map is public
    await page.goto('http://localhost:3000');
    await page.getByText('View Live Map').first().click();
    await expect(page).toHaveURL(/.*\/user\/map/);
    console.log('Verified View Live Map -> /user/map');

    // 3. Check Hero "AI Predictions" -> /user/dashboard -> Login (Protected)
    await page.goto('http://localhost:3000');
    // Using a specific locator to avoid ambiguity if multiple "AI Predictions" text exist
    await page.locator('button:has-text("AI Predictions")').first().click();

    // Now that UserDashboard enforces login, this MUST redirect to /user/login
    await expect(page).toHaveURL(/.*\/user\/login/);
    console.log('Verified Hero AI Predictions -> Redirects to User Login');

    // 4. Check "I'm a Patient" -> /user/dashboard -> Login
    await page.goto('http://localhost:3000');
    await page.getByText("I'm a Patient").click();
    await expect(page).toHaveURL(/.*\/user\/login/);
    console.log("Verified 'I'm a Patient' -> Redirects to User Login");

    // 5. Check Feature Grid Links
    const features = ['AI Predictions', 'Alert Management', 'Analytics Dashboard', 'Reports'];

    for (const feature of features) {
        await page.goto('http://localhost:3000');
        await page.getByText('Powerful Features').scrollIntoViewIfNeeded();

        console.log(`Checking link: ${feature}`);
        await page.getByRole('button', { name: feature }).click();

        // Should redirect to user login
        await expect(page).toHaveURL(/.*\/user\/login/);
    }
});
