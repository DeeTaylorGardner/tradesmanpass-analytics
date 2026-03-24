#!/usr/bin/env node
const { google } = require('googleapis');
const nodemailer = require('nodemailer');
const cron = require('node-cron');
const Anthropic = require('@anthropic-ai/sdk');

const {
  GOOGLE_CLIENT_ID,
  GOOGLE_CLIENT_SECRET,
  GOOGLE_REFRESH_TOKEN,
  GMAIL_USER,
  GMAIL_APP_PASSWORD,
  ANTHROPIC_API_KEY,
} = process.env;

const requiredEnvVars = [
  'GOOGLE_CLIENT_ID',
  'GOOGLE_CLIENT_SECRET',
  'GOOGLE_REFRESH_TOKEN',
  'GMAIL_USER',
  'GMAIL_APP_PASSWORD',
  'ANTHROPIC_API_KEY',
];

const missingVars = requiredEnvVars.filter(v => !process.env[v]);
if (missingVars.length > 0) {
  console.error(`❌ Missing required environment variables: ${missingVars.join(', ')}`);
  process.exit(1);
}

const anthropic = new Anthropic({ apiKey: ANTHROPIC_API_KEY });

const oauth2Client = new google.auth.OAuth2(
  GOOGLE_CLIENT_ID,
  GOOGLE_CLIENT_SECRET,
  'http://localhost:3000/oauth2callback'
);

oauth2Client.setCredentials({
  refresh_token: GOOGLE_REFRESH_TOKEN,
});

const analytics = google.analytics('v3');

const transporter = nodemailer.createTransport({
  service: 'gmail',
  auth: {
    user: GMAIL_USER,
    pass: GMAIL_APP_PASSWORD,
  },
});

async function fetchGAData(propertyId) {
  try {
    const today = new Date();
    const sevenDaysAgo = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000);
    const startDate = sevenDaysAgo.toISOString().split('T')[0];
    const endDate = today.toISOString().split('T')[0];

    const response = await analytics.data.ga.get({
      auth: oauth2Client,
      ids: `ga:529710515`,
      'start-date': startDate,
      'end-date': endDate,
      metrics: 'ga:sessions,ga:users,ga:pageviews,ga:bounceRate,ga:avgSessionDuration',
      dimensions: 'ga:date,ga:source',
    });

    return response.data;
  } catch (error) {
    console.error('❌ Error fetching GA data:', error.message);
    throw error;
  }
}

async function generateSummary(gaData) {
  try {
    const dataString = JSON.stringify(gaData, null, 2);
    const message = await anthropic.messages.create({
      model: 'claude-opus-4-20250805',
      max_tokens: 1024,
      messages: [
        {
          role: 'user',
          content: `Provide a brief 2-3 sentence summary of this Google Analytics data from the past 7 days:\n\n${dataString}`,
        },
      ],
    });
    return message.content[0].text;
  } catch (error) {
    console.error('❌ Error generating summary:', error.message);
    throw error;
  }
}

async function sendReport(gaData, summary) {
  try {
    const mailOptions = {
      from: GMAIL_USER,
      to: GMAIL_USER,
      subject: `TradesmanPass Analytics Report - ${new Date().toLocaleDateString()}`,
      html: `
        <h2>TradesmanPass Weekly Analytics Report</h2>
        <p><strong>Report Date:</strong> ${new Date().toLocaleDateString()}</p>
        <h3>Summary</h3>
        <p>${summary}</p>
        <h3>Raw Data</h3>
        <pre>${JSON.stringify(gaData, null, 2)}</pre>
      `,
    };
    await transporter.sendMail(mailOptions);
    console.log('✅ Report sent to', GMAIL_USER);
  } catch (error) {
    console.error('❌ Error sending email:', error.message);
    throw error;
  }
}

async function runReport() {
  try {
    console.log('🚀 Running analytics report...');
    const gaData = await fetchGAData('529710515');
    const summary = await generateSummary(gaData);
    await sendReport(gaData, summary);
    console.log('✅ Report completed');
  } catch (error) {
    console.error('❌ Report failed:', error.message);
  }
}

const cronExpression = '0 8 * * 1';

console.log('🕐 Analytics agent initialized');
console.log('📅 Scheduled: Every Monday at 8:00 AM Mountain Time');

cron.schedule(cronExpression, () => {
  console.log('⏰ Running report');
  runReport();
});
```

**Step 5:** Scroll down. Click green **"Commit changes"** button.

---

## FILE 3: Procfile

**Step 1:** Click green **"Code"** button → Click **"Add file"** → Click **"Create new file"**

**Step 2:** In filename field, type:
```
Procfile
```

**Step 3:** Click in editor and paste:
```
worker: node analytics-agent-simplified.js
