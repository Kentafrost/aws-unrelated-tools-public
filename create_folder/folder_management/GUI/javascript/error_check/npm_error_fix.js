// npm_error_fix.js - Node.js版のnpmエラー修正スクリプト
const { exec, spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

class NpmErrorFixer {
    constructor() {
        this.currentDir = process.cwd();
        this.success = false;
    }

    log(message, type = 'info') {
        const timestamp = new Date().toLocaleTimeString();
        const prefix = {
            info: '📋',
            success: '✅',
            warning: '⚠️',
            error: '❌',
            step: '🔧'
        };
        
        console.log(`${prefix[type] || 'ℹ️'} [${timestamp}] ${message}`);
    }

    async executeCommand(command, description) {
        return new Promise((resolve, reject) => {
            this.log(`Executing: ${description}`, 'step');
            this.log(`Command: ${command}`, 'info');
            
            exec(command, (error, stdout, stderr) => {
                if (error) {
                    this.log(`Failed: ${description}`, 'error');
                    this.log(`Error: ${error.message}`, 'error');
                    reject(error);
                    return;
                }
                
                if (stderr) {
                    this.log(`Warning: ${stderr}`, 'warning');
                }
                
                this.log(`Success: ${description}`, 'success');
                if (stdout) {
                    console.log(stdout);
                }
                resolve(stdout);
            });
        });
    }

    async cleanNpmCache() {
        try {
            await this.executeCommand('npm cache clean --force', 'Cleaning npm cache');
        } catch (error) {
            this.log('Cache cleaning failed, but continuing...', 'warning');
        }
    }

    async removeNodeModules() {
        const nodeModulesPath = path.join(this.currentDir, 'node_modules');
        
        if (fs.existsSync(nodeModulesPath)) {
            this.log('Removing node_modules directory...', 'step');
            try {
                fs.rmSync(nodeModulesPath, { recursive: true, force: true });
                this.log('node_modules removed successfully', 'success');
            } catch (error) {
                this.log(`Failed to remove node_modules: ${error.message}`, 'error');
            }
        } else {
            this.log('node_modules directory not found', 'info');
        }
    }

    async removePackageLock() {
        const packageLockPath = path.join(this.currentDir, 'package-lock.json');
        
        if (fs.existsSync(packageLockPath)) {
            this.log('Removing package-lock.json...', 'step');
            try {
                fs.unlinkSync(packageLockPath);
                this.log('package-lock.json removed successfully', 'success');
            } catch (error) {
                this.log(`Failed to remove package-lock.json: ${error.message}`, 'error');
            }
        } else {
            this.log('package-lock.json not found', 'info');
        }
    }

    async tryInstallMethods() {
        const installMethods = [
            {
                name: 'Standard npm install',
                command: 'npm install --verbose --no-optional'
            },
            {
                name: 'npm install with legacy peer deps',
                command: 'npm install --legacy-peer-deps'
            },
            {
                name: 'npm install with force',
                command: 'npm install --force'
            },
            {
                name: 'Install only fluent-ffmpeg',
                command: 'npm install fluent-ffmpeg --no-optional --verbose'
            },
            {
                name: 'Install fluent-ffmpeg with save',
                command: 'npm install --save fluent-ffmpeg'
            }
        ];

        for (const method of installMethods) {
            if (this.success) break;

            this.log(`\n=== Trying: ${method.name} ===`, 'step');
            
            try {
                await this.executeCommand(method.command, method.name);
                this.success = true;
                this.log(`✅ Successfully installed with: ${method.name}`, 'success');
                break;
            } catch (error) {
                this.log(`❌ Method failed: ${method.name}`, 'error');
                await new Promise(resolve => setTimeout(resolve, 1000)); // 1秒待機
            }
        }
    }

    async verifyInstallation() {
        this.log('\n=== Verifying installation ===', 'step');
        
        try {
            await this.executeCommand('npm list fluent-ffmpeg', 'Checking fluent-ffmpeg installation');
            
            // Node.js内で実際にrequireしてみる
            try {
                require('fluent-ffmpeg');
                this.log('✅ fluent-ffmpeg can be required successfully', 'success');
            } catch (requireError) {
                this.log(`❌ fluent-ffmpeg require failed: ${requireError.message}`, 'error');
            }
            
        } catch (error) {
            this.log('Could not verify fluent-ffmpeg installation', 'warning');
        }
    }

    async showSystemInfo() {
        this.log('\n=== System Information ===', 'info');
        
        try {
            const nodeVersion = await this.executeCommand('node --version', 'Node.js version');
            const npmVersion = await this.executeCommand('npm --version', 'npm version');
            
            this.log(`Current directory: ${this.currentDir}`, 'info');
            this.log(`Platform: ${process.platform}`, 'info');
            this.log(`Architecture: ${process.arch}`, 'info');
            
        } catch (error) {
            this.log('Could not retrieve system information', 'warning');
        }
    }

    async fixNpmError() {
        this.log('🚀 Starting npm EBADF error fix process...', 'info');
        this.log('='.repeat(50), 'info');
        
        await this.showSystemInfo();
        
        // Step 1: キャッシュクリア
        this.log('\n📦 Step 1: Cleaning npm cache', 'step');
        await this.cleanNpmCache();
        
        // Step 2: node_modules削除
        this.log('\n🗑️ Step 2: Removing node_modules', 'step');
        await this.removeNodeModules();
        
        // Step 3: package-lock.json削除
        this.log('\n🔒 Step 3: Removing package-lock.json', 'step');
        await this.removePackageLock();
        
        // Step 4: インストール試行
        this.log('\n💿 Step 4: Attempting installation with multiple methods', 'step');
        await this.tryInstallMethods();
        
        // Step 5: 検証
        this.log('\n🔍 Step 5: Verifying installation', 'step');
        await this.verifyInstallation();
        
        // 結果報告
        this.log('\n' + '='.repeat(50), 'info');
        if (this.success) {
            this.log('🎉 npm error fix completed successfully!', 'success');
            this.log('You should now be able to use fluent-ffmpeg', 'success');
        } else {
            this.log('❌ Could not resolve the npm error', 'error');
            this.log('Recommendations:', 'warning');
            this.log('1. Try running as Administrator', 'warning');
            this.log('2. Check your internet connection', 'warning');
            this.log('3. Try using yarn instead of npm', 'warning');
            this.log('4. Update Node.js and npm to latest versions', 'warning');
        }
    }
}

// メイン実行
async function main() {
    const fixer = new NpmErrorFixer();
    
    try {
        await fixer.fixNpmError();
    } catch (error) {
        console.error('💥 Unexpected error occurred:', error);
        process.exit(1);
    }
}

// スクリプトが直接実行された場合
if (require.main === module) {
    main();
}

module.exports = NpmErrorFixer;