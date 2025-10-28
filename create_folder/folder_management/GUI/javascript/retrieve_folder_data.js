// 環境に応じてファイルシステムモジュールを読み込み (Load filesystem modules based on environment)
let fs, path, os;
let current_path, parent_path, json_path;

// Node.js環境の検出と初期化 (Detect and initialize Node.js environment)
function initializeEnvironment() {
    try {
        if (typeof require !== 'undefined') {
            fs = require('fs');
            path = require('path');
            os = require('os');
            
            // 現在のファイルパスを取得 (Get current file path)
            current_path = __dirname;
            parent_path = path.dirname(current_path);
            json_path = path.join(parent_path, 'json', 'files_data.json');
            
            console.log('Node.js environment detected');
            console.log('Current path:', current_path);
            console.log('Parent path:', parent_path);
            console.log('JSON path:', json_path);
            
            if (os) {
                console.log('Platform:', os.platform());
                console.log('Windows version:', os.release());
            }
            
            return true;
        }
    } catch (error) {
        console.log('Node.js modules not available, using browser fallback');
    }
    
    // ブラウザ環境の場合のパス設定 (Set paths for browser environment)
    json_path = './json/files_data.json';
    return false;
}

// 初期化実行
const isNodeEnvironment = initializeEnvironment();

// JSONファイルを読み込み、データを取得 (Load JSON file and fetch data)
function fetchData() {
    return new Promise((resolve, reject) => {
        if (isNodeEnvironment && fs) {
            // Node.js環境での読み込み (Load in Node.js environment)
            try {
                // Check if file exists first
                if (!fs.existsSync(json_path)) {
                    console.error('JSON file not found:', json_path);
                    reject(new Error(`JSON file not found: ${json_path}`));
                    return;
                }

                fs.readFile(json_path, 'utf8', (err, data) => {
                    if (err) {
                        console.error('Error reading file:', err);
                        reject(err);
                        return;
                    }
                    
                    try {
                        const jsonData = JSON.parse(data);
                        console.log('Data loaded successfully. Number of files:', jsonData.length);
                        resolve(jsonData);
                    } catch (parseErr) {
                        console.error('Error parsing JSON:', parseErr);
                        reject(parseErr);
                    }
                });
            } catch (error) {
                console.error('Node.js file read error:', error);
                // フォールバック: fetch APIを試行 (Fallback: try fetch API)
                fetchDataWithFetch().then(resolve).catch(reject);
            }
        } else {
            // ブラウザ環境での読み込み (Load in browser environment)
            fetchDataWithFetch().then(resolve).catch(reject);
        }
    });
}

// ブラウザ環境でのデータ取得 (Fetch data in browser environment)
async function fetchDataWithFetch() {
    try {
        console.log('Using fetch API to load JSON data from:', json_path);
        console.log('Current location:', window.location.href);
        
        const response = await fetch(json_path);
        console.log('Fetch response status:', response.status);
        console.log('Fetch response headers:', Object.fromEntries(response.headers.entries()));
        
        if (!response.ok) {
            let errorDetails = `HTTP ${response.status} - ${response.statusText}`;
            if (response.status === 404) {
                errorDetails += `\n\nThe file ${json_path} was not found. Please check:
1. File path is correct
2. File exists in the json directory
3. Web server is serving the json directory correctly`;
            }
            throw new Error(errorDetails);
        }
        
        const text = await response.text();
        console.log('Response text length:', text.length);
        console.log('First 200 characters:', text.substring(0, 200));
        
        const jsonData = JSON.parse(text);
        console.log('Data loaded successfully via fetch. Number of files:', jsonData.length);
        return jsonData;
    } catch (error) {
        console.error('Fetch API error details:', {
            message: error.message,
            name: error.name,
            stack: error.stack,
            url: json_path,
            currentLocation: window.location.href
        });
        throw error;
    }
}

// ファイル情報カードを作成 (Create file information card)
function createFileCard(file, index) {
    const fileCard = document.createElement('div');
    fileCard.style.cssText = `
        border: 1px solid #ddd;
        margin: 8px 0;
        padding: 12px;
        border-radius: 8px;
        background-color: #fafafa;
        transition: background-color 0.2s;
    `;
    
    // ホバーエフェクト (Hover effect)
    fileCard.addEventListener('mouseenter', () => {
        fileCard.style.backgroundColor = '#f0f8ff';
    });
    fileCard.addEventListener('mouseleave', () => {
        fileCard.style.backgroundColor = '#fafafa';
    });

    // ファイル名 (File name)
    const nameDiv = document.createElement('div');
    nameDiv.innerHTML = `<strong>${file.name || 'Unknown file'}</strong>`;
    nameDiv.style.cssText = 'font-size: 16px; margin-bottom: 6px; color: #2c3e50;';
    fileCard.appendChild(nameDiv);

    // ファイル情報 (File information)
    const infoDiv = document.createElement('div');
    infoDiv.style.cssText = 'display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 8px; font-size: 13px;';
    
    // サイズ情報 (Size information)
    if (file.size_MB) {
        const sizeSpan = document.createElement('span');
        sizeSpan.innerHTML = `📁 <strong>Size:</strong> ${file.size_MB}`;
        sizeSpan.style.color = '#27ae60';
        infoDiv.appendChild(sizeSpan);
    }

    // 動画の長さ (Video length)
    if (file.video_length) {
        const lengthSpan = document.createElement('span');
        lengthSpan.innerHTML = `⏰ <strong>Length:</strong> ${file.video_length}`;
        lengthSpan.style.color = '#3498db';
        infoDiv.appendChild(lengthSpan);
    }
    
    fileCard.appendChild(infoDiv);

    // パス情報 (Path information) - 縮小表示
    if (file.path) {
        const pathDiv = document.createElement('div');
        pathDiv.style.cssText = 'font-size: 11px; color: #7f8c8d; margin-bottom: 8px; word-break: break-all; cursor: pointer; padding: 2px; border-radius: 3px; transition: background-color 0.2s;';
        const shortPath = file.path.length > 80 ? '...' + file.path.slice(-77) : file.path;
        pathDiv.innerHTML = `📂 ${shortPath}`;
        pathDiv.title = `クリックでExplorerを開く: ${file.path}`; // フルパスをツールチップで表示
        
        // ホバーエフェクト
        pathDiv.addEventListener('mouseenter', () => {
            pathDiv.style.backgroundColor = '#e8f4f8';
        });
        pathDiv.addEventListener('mouseleave', () => {
            pathDiv.style.backgroundColor = 'transparent';
        });
        
        // クリックでExplorer表示
        pathDiv.addEventListener('click', async () => {
            try {
                // Electron環境の場合
                if (typeof require !== 'undefined') {
                    try {
                        // Method 1: shell moduleを使用
                        const { shell } = require('electron');
                        await shell.showItemInFolder(file.path);
                        console.log('Opened in Explorer via electron.shell:', file.path);
                        return;
                    } catch (e) {
                        console.log('electron.shell not available, trying @electron/remote');
                        
                        // Method 2: @electron/remote経由
                        try {
                            const { shell } = require('@electron/remote');
                            await shell.showItemInFolder(file.path);
                            console.log('Opened in Explorer via @electron/remote:', file.path);
                            return;
                        } catch (e2) {
                            console.log('@electron/remote not available, trying child_process');
                        }
                    }
                    
                    // Method 3: child_process経由でWindows Explorerを直接開く
                    try {
                        const { exec } = require('child_process');
                        const command = `explorer /select,"${file.path}"`;
                        exec(command, (error) => {
                            if (error) {
                                console.error('Failed to open Explorer:', error);
                                throw error;
                            } else {
                                console.log('Opened in Explorer via child_process:', file.path);
                            }
                        });
                        return;
                    } catch (e3) {
                        console.error('child_process method failed:', e3);
                    }
                }
                
                // ブラウザ環境の代替手段: パスをクリップボードにコピー
                if (navigator.clipboard) {
                    await navigator.clipboard.writeText(file.path);
                    alert(`ファイルパスをクリップボードにコピーしました:\n${file.path}\n\nエクスプローラーで手動で開いてください。`);
                } else {
                    // クリップボードAPIが使えない場合
                    prompt('ファイルパス (Ctrl+Cでコピー):', file.path);
                }
                
            } catch (error) {
                console.error('Error opening Explorer:', error);
                alert(`エクスプローラーを開けませんでした。\n\nファイルパス: ${file.path}\n\nエラー: ${error.message}`);
            }
        });

        fileCard.appendChild(pathDiv);
    }

    // タグ情報 (Tag information)
    if (file.tags && file.tags.length > 0) {
        const tagsDiv = document.createElement('div');
        tagsDiv.style.cssText = 'margin-top: 8px;';
        
        const tagsLabel = document.createElement('span');
        tagsLabel.innerHTML = '🏷️ <strong>Tags:</strong> ';
        tagsLabel.style.cssText = 'font-size: 12px; color: #34495e;';
        tagsDiv.appendChild(tagsLabel);
        
        file.tags.forEach((tag, tagIndex) => {
            const tagSpan = document.createElement('span');
            tagSpan.textContent = tag;
            tagSpan.style.cssText = `
                display: inline-block;
                background-color: #ecf0f1;
                color: #2c3e50;
                padding: 2px 6px;
                margin: 2px;
                border-radius: 12px;
                font-size: 11px;
                border: 1px solid #bdc3c7;
            `;
            tagsDiv.appendChild(tagSpan);
        });
        
        fileCard.appendChild(tagsDiv);
    }

    // インデックス番号を追加 (Add index number)
    const indexDiv = document.createElement('div');
    indexDiv.textContent = `#${index + 1}`;
    indexDiv.style.cssText = `
        position: absolute;
        top: 8px;
        right: 8px;
        background-color: #95a5a6;
        color: white;
        padding: 2px 6px;
        border-radius: 10px;
        font-size: 10px;
        font-weight: bold;
    `;
    fileCard.style.position = 'relative';
    fileCard.appendChild(indexDiv);

    return fileCard;
}

// メイン実行 (Main execution)
async function json_data_list() {
    console.log('Starting json_data_list function...');
    
    try {
        // ステップ1: 環境チェック
        console.log('Step 1: Environment check');
        console.log('- isNodeEnvironment:', isNodeEnvironment);
        console.log('- json_path:', json_path);
        console.log('- Current location:', window.location ? window.location.href : 'No window.location');
        
        // ステップ2: DOM要素チェック
        console.log('Step 2: DOM element check');
        const fileListDiv = document.getElementById('file-list');
        if (!fileListDiv) {
            const errorMsg = 'Element with id "file-list" not found';
            console.error(errorMsg);
            
            // DOM構造をデバッグ出力
            console.log('Available elements with IDs:');
            const elementsWithId = document.querySelectorAll('[id]');
            elementsWithId.forEach(el => console.log(`- ${el.tagName}#${el.id}`));
            
            throw new Error(errorMsg);
        }
        console.log('- file-list element found:', fileListDiv);

        // ステップ3: データ取得
        console.log('Step 3: Fetching data...');
        const data = await fetchData();
        console.log('- Data fetched successfully');
        console.log('- Data type:', typeof data);
        console.log('- Data is array:', Array.isArray(data));
        console.log('- Data length:', data ? data.length : 'null/undefined');

        if (data && data.length > 0) {
            console.log('- Sample file structure:', Object.keys(data[0]));
        }

        // ステップ4: HTML更新
        console.log('Step 4: Updating HTML...');
        fileListDiv.innerHTML = ''; // 既存の内容をクリア (Clear existing content)

        // fileListDivにデータを入れて、divに配列を入れる (Add data to fileListDiv and create array)
        const fileArray = [];
        
        if (!data || data.length === 0) {
            console.log('- No data found, displaying message');
            const noDataItem = document.createElement('div');
            noDataItem.innerHTML = `
                <div style="text-align: center; padding: 40px; color: #666;">
                    <h4>📭 No files found</h4>
                    <p>The JSON file appears to be empty or contains no data.</p>
                    <button onclick="checkFileExistence()" style="margin-top: 10px; padding: 5px 10px;">Check File</button>
                    <button onclick="debugEnvironment()" style="margin-top: 10px; margin-left: 10px; padding: 5px 10px;">Debug</button>
                </div>
            `;
            fileListDiv.appendChild(noDataItem);
            return fileArray;
        }

        console.log('Step 5: Creating file cards...');
        let cardCount = 0;
        data.forEach((file, index) => {
            try {
                const fileItem = createFileCard(file, index);
                fileListDiv.appendChild(fileItem);
                fileArray.push(file);
                cardCount++;
                
                // 進行状況をログ出力（最初の5個と10個おき）
                if (index < 5 || (index + 1) % 10 === 0) {
                    console.log(`- Created card ${index + 1}/${data.length}: ${file.name || 'Unknown'}`);
                }
            } catch (cardError) {
                console.error(`Error creating card for file ${index}:`, cardError);
                console.log('Problematic file data:', file);
            }
        });
        
        console.log(`- Successfully created ${cardCount} file cards`);

        // 統計情報を表示 (Display statistics)
        console.log('Step 6: Adding statistics...');
        const statsDiv = document.createElement('div');
        const tagCount = data.reduce((count, file) => {
            return count + (file.tags ? file.tags.length : 0);
        }, 0);
        
        statsDiv.innerHTML = `
            <strong>📊 Total Files: ${data.length}</strong> | 
            <strong>🏷️ Total Tags: ${tagCount}</strong> | 
            <strong>✅ Cards Created: ${cardCount}</strong>
        `;
        statsDiv.style.cssText = 'padding: 10px; background-color: #e8f4f8; border-radius: 4px; margin-bottom: 10px; font-weight: bold;';
        fileListDiv.insertBefore(statsDiv, fileListDiv.firstChild);

        console.log('✅ json_data_list completed successfully');
        return fileArray;
        
    } catch (error) {
        console.error('❌ Main execution error:', error);
        console.error('Error stack:', error.stack);
        
        const fileListDiv = document.getElementById('file-list');
        if (fileListDiv) {
            fileListDiv.innerHTML = `
                <div style="color: red; padding: 20px; border: 1px solid red; border-radius: 5px; background-color: #ffebee;">
                    <h4>❌ Error loading data</h4>
                    <p><strong>Error:</strong> ${error.message || 'Unknown error'}</p>
                    <p><strong>JSON Path:</strong> ${json_path || 'Not set'}</p>
                    <p><strong>Environment:</strong> ${isNodeEnvironment ? 'Node.js' : 'Browser'}</p>
                    <p><strong>Current URL:</strong> ${window.location ? window.location.href : 'Not available'}</p>
                    
                    <details style="margin-top: 10px;">
                        <summary>🔍 Technical Details</summary>
                        <pre style="font-size: 12px; overflow: auto; max-height: 200px;">${error.stack || error.toString()}</pre>
                    </details>
                    
                    <div style="margin-top: 15px;">
                        <button onclick="debugEnvironment()" style="padding: 8px 12px; margin-right: 10px; background-color: #6c757d; color: white; border: none; border-radius: 4px;">
                            🐛 Debug Environment
                        </button>
                        <button onclick="checkFileExistence()" style="padding: 8px 12px; margin-right: 10px; background-color: #ffc107; color: black; border: none; border-radius: 4px;">
                            📄 Check File
                        </button>
                        <button onclick="location.reload()" style="padding: 8px 12px; background-color: #17a2b8; color: white; border: none; border-radius: 4px;">
                            🔄 Reload Page
                        </button>
                    </div>
                </div>
            `;
        } else {
            // file-list要素も見つからない場合
            console.error('Cannot display error - file-list element not found');
            alert(`Critical Error: ${error.message}\n\nfile-list element not found in DOM.\nCheck HTML structure.`);
        }
        return [];
    }
}

// フォルダ選択ダイアログを表示して選択されたパスをHTMLに表示 (Display folder selection dialog and show selected path in HTML)
async function selectfolder() {
    try {
        // Electron環境の検出 (Detect Electron environment)
        const isElectron = typeof require !== 'undefined' && typeof window !== 'undefined' && window.process && window.process.type;
        
        if (isElectron) {
            // Electronの場合 (For Electron environment)
            try {
                // 複数のElectron APIを試行 (Try multiple Electron APIs)
                let dialog = null;
                
                // Method 1: Modern @electron/remote
                try {
                    dialog = require('@electron/remote').dialog;
                } catch (e) {
                    console.log('@electron/remote not available, trying electron.remote');
                }
                
                // Method 2: Legacy electron.remote
                if (!dialog) {
                    try {
                        dialog = require('electron').remote.dialog;
                    } catch (e) {
                        console.log('electron.remote not available, trying main process');
                    }
                }
                
                // Method 3: Main process (if available)
                if (!dialog && window.electronAPI) {
                    const result = await window.electronAPI.selectfolder();
                    if (result) {
                        displaySelectedFolder(result);
                        return result;
                    }
                }
                
                if (dialog) {
                    const result = await dialog.showOpenDialog({
                        properties: ['openDirectory'],
                        title: 'Select Folder',
                        buttonLabel: 'Select Folder'
                    });

                    if (result.canceled) {
                        console.log('Folder selection canceled');
                        return null;
                    }

                    const selectedFolder = result.filePaths[0];
                    console.log('Selected folder:', selectedFolder);
                    displaySelectedFolder(selectedFolder);
                    alert('Selected folder: ' + selectedFolder);
                    return selectedFolder;
                }
            } catch (electronError) {
                console.error('Electron dialog error:', electronError);
            }
        }
        
        // ブラウザ環境またはElectronが利用できない場合の代替手段 (Fallback for browser or when Electron is not available)
        console.log('Using browser fallback for folder selection');
        return await browserFolderSelect();
        
    } catch (error) {
        console.error('Error selecting folder:', error);
        const folderPath = document.getElementById('selected-folder-path');
        if (folderPath) {
            folderPath.innerHTML = '<span style="color: red;">Error selecting folder: ' + error.message + '</span>';
        }
        return null;
    }
}

// 選択されたフォルダをHTMLに表示 (Display selected folder in HTML)
function displaySelectedFolder(selectedFolder) {
    const folderPath = document.getElementById('selected-folder-path');
    if (!folderPath) {
        console.error('Element with id "selected-folder-path" not found');
        return;
    }

    folderPath.innerHTML = ''; // Clear existing content
    folderPath.textContent = selectedFolder;
    folderPath.style.padding = '10px';
    folderPath.style.backgroundColor = '#f0f0f0';
    folderPath.style.border = '1px solid #ccc';
    folderPath.style.borderRadius = '4px';
}

// ブラウザ環境でのフォルダ選択代替手段 (Browser fallback for folder selection)
async function browserFolderSelect() {
    try {
        // Web APIs for directory selection (Chrome 86+)
        if ('showDirectoryPicker' in window) {
            const dirHandle = await window.showDirectoryPicker();
            const folderName = dirHandle.name;
            console.log('Browser selected folder:', folderName);
            displaySelectedFolder(folderName);
            return folderName;
        } else {
            // Fallback: Manual input
            const folderPath = prompt('フォルダパスを入力してください (Enter folder path):', '');
            if (folderPath) {
                displaySelectedFolder(folderPath);
                refreshData(); 
                return folderPath;
            }
        }
    } catch (error) {
        console.error('Browser folder selection error:', error);
        // Manual input fallback
        const folderPath = prompt('フォルダパスを入力してください (Enter folder path):', '');
        if (folderPath) {
            displaySelectedFolder(folderPath);
            return folderPath;
        }
    }
    return null;
}

// イベントリスナーの初期化 (Initialize event listeners)
function initializeEventListeners() {
    // データ読み込み後にタグを動的に追加 (Add tags dynamically after data loading)
    json_tag_selection();

    // タグセレクトボックスのイベント (Tag select box event)
    const tagSelect = document.getElementById('tag-item');
    if (tagSelect) {
        tagSelect.addEventListener('change', function() {
            const selectedTag = this.value;
            const searchInput = document.getElementById('search-input');
            const searchTerm = searchInput ? searchInput.value.trim() : '';
            
            if (selectedTag || searchTerm) {
                filterFiles(selectedTag, searchTerm);
            } else {
                json_data_list(); // Show all files if no filter
            }
        });
    }

    // 検索インプットのイベント (Search input event)
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
        let searchTimeout;
        searchInput.addEventListener('input', function() {
            const searchTerm = this.value.trim();
            const tagSelect = document.getElementById('tag-item');
            const selectedTag = tagSelect ? tagSelect.value : '';
            
            // デバウンス処理 (Debounce)
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                if (selectedTag || searchTerm) {
                    filterFiles(selectedTag, searchTerm);
                } else {
                    json_data_list(); // Show all files if no filter
                }
            }, 300);
        });
    }
}

// ファイルをフィルタリング (Filter files)
async function filterFiles(tag, searchTerm) {
    try {
        const data = await fetchData();
        let filteredFiles = [...data];

        // タグでフィルタリング (Filter by tag)
        if (tag) {
            filteredFiles = filteredFiles.filter(file => 
                file.tags && Array.isArray(file.tags) && file.tags.includes(tag)
            );
        }

        // 検索語でフィルタリング (Filter by search term)
        if (searchTerm) {
            filteredFiles = filteredFiles.filter(file => 
                (file.name && file.name.toLowerCase().includes(searchTerm.toLowerCase())) ||
                (file.path && file.path.toLowerCase().includes(searchTerm.toLowerCase())) ||
                (file.tags && file.tags.some(t => t.toLowerCase().includes(searchTerm.toLowerCase())))
            );
        }

        displayFilteredFiles(filteredFiles, tag, searchTerm);
    } catch (error) {
        console.error('Error filtering files:', error);
    }
}

// フィルタリング結果を表示 (Display filtered results)
function displayFilteredFiles(filteredFiles, tag, searchTerm) {
    const fileListDiv = document.getElementById('file-list');
    if (!fileListDiv) {
        console.error('Element with id "file-list" not found');
        return;
    }

    fileListDiv.innerHTML = ''; // Clear existing content

    // 統計情報を表示 (Display statistics)
    const statsDiv = document.createElement('div');
    let filterInfo = '';
    if (tag && searchTerm) {
        filterInfo = ` (Tag: ${tag}, Search: "${searchTerm}")`;
    } else if (tag) {
        filterInfo = ` (Tag: ${tag})`;
    } else if (searchTerm) {
        filterInfo = ` (Search: "${searchTerm}")`;
    }
    
    statsDiv.innerHTML = `<strong>Filtered Files: ${filteredFiles.length}</strong>${filterInfo}`;
    statsDiv.style.cssText = 'padding: 10px; background-color: #fff3cd; border-radius: 4px; margin-bottom: 10px; font-weight: bold;';
    fileListDiv.appendChild(statsDiv);

    if (filteredFiles.length === 0) {
        const noResultsDiv = document.createElement('div');
        noResultsDiv.innerHTML = `
            <div style="text-align: center; padding: 40px; color: #666;">
                <h4>😔 検索結果が見つかりません</h4>
                <p>フィルター条件を変更してみてください</p>
            </div>
        `;
        fileListDiv.appendChild(noResultsDiv);
    } else {
        filteredFiles.forEach((file, index) => {
            const fileCard = createFileCard(file, index);
            fileListDiv.appendChild(fileCard);
        });
    }
}

// データを再読込 (Refresh data)
async function refreshData() {
    try {
        const fileListDiv = document.getElementById('file-list');
        if (fileListDiv) {
            fileListDiv.innerHTML = '<div style="text-align: center; padding: 20px;">🔄 データを再読込中...</div>';
        }
        
        // 少し遅延を入れて再読込感を演出
        setTimeout(async () => {
            await json_data_list();
            
            // 検索とフィルターをクリア
            const tagSelect = document.getElementById('tag-item');
            const searchInput = document.getElementById('search-input');
            if (tagSelect) tagSelect.value = '';
            if (searchInput) searchInput.value = '';
            
            console.log('Data refreshed successfully');
        }, 500);
        
    } catch (error) {
        console.error('Error refreshing data:', error);
    }
}

// 環境デバッグ用関数 (Debug environment function)
function debugEnvironment() {
    const debugInfo = [];
    
    // 基本情報
    debugInfo.push('=== Environment Debug Information ===');
    debugInfo.push(`Current URL: ${window.location.href}`);
    debugInfo.push(`Protocol: ${window.location.protocol}`);
    debugInfo.push(`Is Node Environment: ${isNodeEnvironment}`);
    debugInfo.push(`JSON Path: ${json_path}`);
    
    // Node.js環境チェック
    debugInfo.push('\n=== Node.js Environment ===');
    try {
        debugInfo.push(`require available: ${typeof require !== 'undefined'}`);
        debugInfo.push(`__dirname: ${typeof __dirname !== 'undefined' ? __dirname : 'undefined'}`);
        if (fs) {
            debugInfo.push(`fs module loaded: true`);
            try {
                debugInfo.push(`JSON file exists: ${fs.existsSync(json_path)}`);
            } catch (e) {
                debugInfo.push(`Error checking file existence: ${e.message}`);
            }
        } else {
            debugInfo.push(`fs module loaded: false`);
        }
    } catch (e) {
        debugInfo.push(`Node.js environment error: ${e.message}`);
    }
    
    // ブラウザ環境チェック
    debugInfo.push('\n=== Browser Environment ===');
    debugInfo.push(`fetch API available: ${typeof fetch !== 'undefined'}`);
    debugInfo.push(`User Agent: ${navigator.userAgent}`);
    
    // DOM要素チェック
    debugInfo.push('\n=== DOM Elements ===');
    debugInfo.push(`file-list element: ${document.getElementById('file-list') ? 'found' : 'not found'}`);
    debugInfo.push(`tag-item element: ${document.getElementById('tag-item') ? 'found' : 'not found'}`);
    debugInfo.push(`search-input element: ${document.getElementById('search-input') ? 'found' : 'not found'}`);
    
    const result = debugInfo.join('\n');
    console.log(result);
    alert(result);
}

// ファイル存在確認用関数 (File existence check function)
async function checkFileExistence() {
    try {
        console.log('Checking file existence...');
        
        if (isNodeEnvironment && fs) {
            const exists = fs.existsSync(json_path);
            console.log(`File exists (Node.js): ${exists}`);
            
            if (exists) {
                const stats = fs.statSync(json_path);
                console.log(`File size: ${stats.size} bytes`);
                console.log(`Last modified: ${stats.mtime}`);
            }
            
            return exists;
        } else {
            // ブラウザ環境でfetch APIを使用してファイル存在確認
            try {
                const response = await fetch(json_path, { method: 'HEAD' });
                console.log(`File exists (Browser): ${response.ok}`);
                console.log(`Response status: ${response.status}`);
                return response.ok;
            } catch (fetchError) {
                console.log(`File check failed (Browser): ${fetchError.message}`);
                return false;
            }
        }
    } catch (error) {
        console.error('Error checking file existence:', error);
        return false;
    }
}

async function json_tag_selection() {
  try {
    const data = await fetchData(); // 直接JSONデータを取得
    
    if (!data || data.length === 0) {
      console.warn('No data available for tag selection');
      return;
    }

    const select = document.getElementById("tag-item");
    if (!select) {
      console.error('Tag select element not found');
      return;
    }

    // 既存の動的タグオプションをクリア（デフォルトオプションは保持）
    const dynamicOptions = Array.from(select.options).filter(option => 
      !option.disabled && 
      option.value !== '' && 
      !['doujin', 'game', 'bf'].includes(option.value)
    );
    dynamicOptions.forEach(option => option.remove());

    // 全ファイルからユニークなタグを収集
    const allTags = new Set();
    
    data.forEach(file => {
      if (file.tags && Array.isArray(file.tags)) {
        file.tags.forEach(tag => {
          if (tag && typeof tag === 'string' && tag.trim()) {
            allTags.add(tag.trim());
          }
        });
      }
    });

    // タグをソート
    const sortedTags = Array.from(allTags).sort((a, b) => {
      return a.localeCompare(b, 'ja', { numeric: true });
    });

    // セパレーター追加
    if (sortedTags.length > 0) {
      const separator = document.createElement("option");
      separator.disabled = true;
      separator.textContent = "───── All Tags ─────";
      separator.style.fontStyle = 'italic';
      separator.style.color = '#666';
      select.appendChild(separator);
    }

    // タグオプションを追加
    sortedTags.forEach(tag => {
      const option = document.createElement("option");
      option.value = tag;
      option.textContent = tag;
      select.appendChild(option);
    });

    console.log(`Added ${sortedTags.length} unique tags to select box`);

  } catch (error) {
    console.error("タグの読み込みに失敗しました:", error);
  }
}


// DOMContentLoadedイベントでイベントリスナーを初期化 (Initialize event listeners on DOMContentLoaded)
if (typeof document !== 'undefined') {
    document.addEventListener('DOMContentLoaded', initializeEventListeners);
}


// グローバル関数としてエクスポート (Export as global functions)
window.getTaggedFiles = getTaggedFiles;
window.json_data_list = json_data_list;
window.selectfolder = selectfolder;
window.initializeEventListeners = initializeEventListeners;
window.checkElectronEnvironment = checkElectronEnvironment;
window.refreshdata = refreshdata;
window.filterFiles = filterFiles;
window.json_tag_selection = json_tag_selection;
window.debugEnvironment = debugEnvironment;
window.checkFileExistence = checkFileExistence;