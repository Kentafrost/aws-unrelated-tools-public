// install_modules.js - Windowsモジュールのインストールスクリプト
const { exec } = require('child_process');
const path = require('path');

const modules = [
    'node-windows',
    'windows-shortcuts', 
    'node-powershell',
    'winattr',
    'windows-registry',
    'electron-windows-notifications'
];

console.log('Installing Windows modules...');
console.log('Modules to install:', modules.join(', '));

async function installModule(moduleName) {
    return new Promise((resolve, reject) => {
        console.log(`Installing ${moduleName}...`);
        exec(`npm install ${moduleName}`, (error, stdout, stderr) => {
            if (error) {
                console.error(`Error installing ${moduleName}:`, error.message);
                reject(error);
                return;
            }
            if (stderr) {
                console.warn(`Warning for ${moduleName}:`, stderr);
            }
            console.log(`✓ ${moduleName} installed successfully`);
            resolve(stdout);
        });
    });
}

async function installAllModules() {
    try {
        for (const module of modules) {
            await installModule(module);
        }
        console.log('\n✓ All Windows modules installed successfully!');
        console.log('\nYou can now use Windows-specific features in your Node.js application.');
        console.log('\nNext steps:');
        console.log('1. Run: node retrieve_data.js');
        console.log('2. Run: node example_usage.js');
    } catch (error) {
        console.error('\n✗ Installation failed:', error.message);
        console.log('\nTry running as administrator or check your network connection.');
    }
}

// メイン実行
if (require.main === module) {
    installAllModules();
}

module.exports = { installAllModules, installModule };