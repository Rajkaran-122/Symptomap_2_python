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
2.  Follow the prompts to enter email and password.
