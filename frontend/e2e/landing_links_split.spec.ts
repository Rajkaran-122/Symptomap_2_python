
import { test, expect } from '@playwright/test';

test('Part 1: Public Map Access', async ({ page }) => {
    await page.goto('http://localhost:3000');
    await page.getByText('View Live Map').first().click();
    // Use a more lenient check or print URL
    await expect(page).toHaveURL(/.*\/user\/map/);
    console.log('Verified View Live Map -> /user/map');
});

test('Part 2: Dashboard Access via Hero', async ({ page }) => {
    await page.goto('http://localhost:3000');
    await page.locator('button:has-text("AI Predictions")').first().click();
    await expect(page).toHaveURL(/.*\/user\/login/);
    console.log('Verified Hero AI Predictions -> Redirects to User Login');
});
