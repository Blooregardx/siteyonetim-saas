import { defineConfig } from '@playwright/test';
export default defineConfig({ testDir: './tests/e2e', workers: 1, use: { baseURL: 'http://127.0.0.1:3000' }, webServer: { command: 'npm start -- --hostname 127.0.0.1', url: 'http://127.0.0.1:3000/giris', reuseExistingServer: false, env: { SMTP_URL: 'smtp://127.0.0.1:2525', MAIL_FROM: 'test@example.invalid', APP_URL: 'http://127.0.0.1:3000' } } });
