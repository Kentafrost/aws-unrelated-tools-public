const axios = require('axios');
const fs = require('fs');
const path = require('path');

// Disable SSL verification warnings (for development only)
process.env["NODE_TLS_REJECT_UNAUTHORIZED"] = 0;

// ディレクトリ設定
const currentDir = __dirname;
const resultsDir = path.join(currentDir, 'results');

// RapidAPI経由での楽天API呼び出し設定
const ApiUrl = "https://app.rakuten.co.jp/services/api/IchibaItem/Search/20220601";

// jsonファイルから設定を読み込む
const searchParams = JSON.parse(fs.readFileSync(path.join(currentDir, 'search_param.json'), 'utf-8'));
const applicationId = searchParams.applicationId;
const rapidApiHeaders = {
    "x-rapidapi-key": searchParams["x-rapidapi-key"],
    "x-rapidapi-host": searchParams["x-rapidapi-host"]
};

// 楽天APIで取得できるページ, キーワード設定
const number_hits = searchParams.number_hits;
const page = searchParams.page;
const max_page = searchParams.max_page;
const keywords = searchParams.keywords;
const requirements = searchParams.requirements || {};

// 結果ディレクトリを作成
if (!fs.existsSync(resultsDir)) {
    fs.mkdirSync(resultsDir, { recursive: true });
}

// CSVに保存する関数
function saveToCSV(items, currentPage, csvPath) {

    // CSVファイルの初期化
    fs.writeFile(csvPath, '', (err) => {
        if (err) {
            console.error('Error creating file:', err);
        } else {
            console.log('File created successfully');
        }
    });

    // CSVファイルに書き込み
    const headers = 'Name,Catchcopy,Availability,Price,URL,Shop,ShopURL,Page\n';
    fs.writeFileSync(csvPath, headers, 'utf-8');

    const csvData = [];
    console.log(`📦 ${items.length}件の商品が見つかりました (ページ ${currentPage}):`);
    
    items.forEach((item, index) => {
        const info = item.Item || item;
        const name = info.itemName || info.productName || '-';
        const catchcopy = info.catchcopy || '-';
        const availability = info.availability || '-';
        const price = info.itemPrice || info.productPrice || '-';
        const url = info.itemUrl || info.productUrl || '-';
        const shopName = info.shopName || '-';
        const shopUrl = info.shopUrl || '-';

        // if requirements is matched then skip the item to write
        try {
            if (requirements.cost[0].min < price && price < requirements.cost[1].max &&
                requirements.makers.some(maker => name.includes(maker))) {

                console.log(`❌ ${name} - ¥${price} は要件を満たしていません`);
                return;
            }
        } catch (error) {
            console.log("要件のチェック項目が書かれていません。\nすべての商品を保存します。");
        }

        const row = `${name},${catchcopy},${availability},${price},${url},${shopName},${shopUrl},${currentPage}\n`;

        // if data doesn't exist, write in write mode
        if (!fs.existsSync(csvPath) || fs.statSync(csvPath).size === 0) {
            fs.writeFileSync(csvPath, row, 'utf-8');
        } else {
            fs.appendFileSync(csvPath, row, 'utf-8');
        }

        console.log(`${index + 1}. ${name} - ¥${price} - ${shopName}`);
    });

    console.log(`✅ ${currentPage}ページ目 ${csvData.length}件の商品をCSVに保存しました: ${csvPath}`);
}


// // 方法1: RapidAPI経由で楽天商品検索
async function fetchItemsViaRapidAPI(keyword, csvPath) {
    try {
        console.log('🛍️ RapidAPI経由で楽天商品を検索中...');
        
        const params = {
            keyword: keyword,
            format: 'json',
            page: page,
            hits: number_hits
        };
        
        const response = await axios.get(ApiUrl, {
            headers: rapidApiHeaders,
            params: params,
            timeout: 30000
        });

        console.log(`✅ API呼び出し成功 (ステータス: ${response.status})`);
        
        if (response.data && response.data.products) {
            saveToCSV(response.data.Items);
        } else if (response.data && response.data.Items.Item) {
            saveToCSV(response.data.Items);
        } else {
            console.log('⚠️ 商品データが見つかりませんでした');
            console.log('レスポンス:', JSON.stringify(response.data, null, 2));
        }
        
    } catch (error) {
        console.error('❌ RapidAPI呼び出しエラー:', error.message);
        if (error.response) {
            console.log('ステータス:', error.response.status);
            console.log('レスポンス:', error.response.data);
        }
        throw error;
    }
}

// 方法2: 直接楽天API呼び出し
async function fetchItemsDirectAPI(keyword, csvPath) {
    try {
        console.log('🛍️ 直接楽天APIで商品を検索中...');
        
        for (let currentPage = 1; currentPage <= max_page; currentPage++) {
            console.log(`🔄 ページ ${currentPage} を取得中...`);

            const params = {
                applicationId: applicationId,
                keyword: keyword,
                format: 'json',
                page: currentPage,
                hits: number_hits
            };
            
            const response = await axios.get(ApiUrl, {
                params: params,
                timeout: 30000
            });
            console.log(`✅ 直接API呼び出し成功 (ステータス: ${response.status})`);
            
            if (response.data && response.data.Items) {
                saveToCSV(response.data.Items, currentPage, csvPath);
            } else {
                console.log('⚠️ 商品データが見つかりませんでした');
                console.log('レスポンス:', JSON.stringify(response.data, null, 2));
            }
            // sleep for 10 seconds
            await new Promise(resolve => setTimeout(resolve, 10000));
        }
            
    } catch (error) {
        console.error('❌ 直接API呼び出しエラー:', error.message);
        if (error.response) {
            console.log('ステータス:', error.response.status);
            console.log('レスポンス:', error.response.data);
        }
        throw error;
    }
}

 // メイン実行関数
async function fetchItems(keyword, csvPath) {
    console.log(`🔍 キーワード "${keyword}" で商品検索を開始...`);
    
    // RapidAPIで試行
    try {
        await fetchItemsViaRapidAPI(keyword, csvPath);
    } catch (error) {
        console.log('\n🔄 RapidAPIが失敗したので、直接APIを試行...');
        
        try {
            await fetchItemsDirectAPI(keyword, csvPath);
        } catch (error2) {
            console.log('\n❌ 両方のAPI呼び出しが失敗しました');
            console.log('\n💡 解決方法:');
            console.log('1. インターネット接続を確認');
            console.log('2. RapidAPIキーが有効か確認');
            console.log('3. 楽天アプリケーションIDが有効か確認');
            console.log('4. 検索キーワードを変更してみる');
        }
    }
}


// メイン実行関数
async function main() {
    for (const keyword of keywords) {
        const csvPath = path.join(resultsDir, `rakuten_products_${keyword}.csv`);
        
        try {
            await fetchItems(keyword, csvPath);
        } catch (error) {
            console.error(`❌ ${keyword} の商品検索中にエラーが発生しました:`, error.message);
        }
    }
}

// スクリプト実行
main().catch(error => {
    console.error('❌ アプリケーションエラー:', error);
    process.exit(1);
});