#!/usr/bin/env node

const { exec } = require('child_process');
const path = require('path');

const scriptPath = "g:\\My Drive\\IT_Learning\\Git\\aws-unrelated-tools-private\\web-sites-listup\\rakuten\\rakuten_item_listup.js";

console.log('🛍️ Running Rakuten Product Fetcher...');

exec(`node "${scriptPath}"`, { cwd: path.dirname(scriptPath) }, (error, stdout, stderr) => {
    if (error) {
        console.error(`❌ Error: ${error.message}`);
        return;
    }
    if (stderr) {
        console.warn(`⚠️ Warning: ${stderr}`);
    }
    console.log(stdout);
    console.log('✅ Completed!');
});
