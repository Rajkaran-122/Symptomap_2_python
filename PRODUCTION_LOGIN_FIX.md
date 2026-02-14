# Fixing Production Login (401 Error)

The "Invalid Credentials" error happens because your new Render database is **empty**. It does not have the user account you created locally.

## Solution 1: Run the Seeder (Recommended)
This will create the default admin user and populate the map with data.

1.  Go to your **Render Dashboard**.
2.  Select your **Backend Service** (symptomap-api).
3.  Click **Shell** (or "Connect").
4.  Run this command:
    ```bash
    python seed_production_data.py
    ```
5.  **Login with:**
    -   **Email:** `admin@symptomap.com`
    -   **Password:** `admin123`

## Solution 2: Create a Custom User
If you want to create a specific user, I have included a script `create_prod_user.py`.

1.  In the Render Shell, run:
    ```bash
    python create_prod_user.py
    ```
## Solution 3: Use the API Endpoint (Easiest)
If you cannot use the Shell (Free Tier restriction), use this special endpoint I created.

1.  **Wait for Deployment** of the latest changes.
2.  **Open this URL in your browser:**
    `https://symptomap-2-python-1.onrender.com/api/v1/admin-ops/seed-production`
3.  You should see a JSON response: `{"status": "success", ...}`.
4.  **Login with:**
    -   **Email:** `admin@symptomap.com`
    -   **Password:** `admin123`

## Solution 4: Unlock Account (Fix 429 Error)
If you get "Too many failed attempts", use this endpoint to unlock your account immediately.

1.  **Open this URL in your browser:**
    `https://symptomap-2-python-1.onrender.com/api/v1/admin-ops/unlock-account?email=user@symptomap.com`
    *(Replace email if needed)*
2.  You should see `{"status": "success", ...}`.
3.  Try logging in again.
