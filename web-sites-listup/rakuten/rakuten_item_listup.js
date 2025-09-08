const axios = require('axios');
const fs = require('fs');
const path = require('path');

// Disable SSL verification warnings (for development only)
process.env["NODE_TLS_REJECT_UNAUTHORIZED"] = 0;

const url = "https://rakuten_webservice-rakuten-marketplace-product-search-v1.p.rapidapi.com/services/api/Product/Search/20170426";

// Add query parameters for the search
const params = {
    keyword: 'モデルガン',  // Model gun keyword
    format: 'json',
    elements: 'productName,productPrice,productUrl,imageUrl',
    page: '1',
    hits: '30'  // Number of results
};

const headers = {
    "x-rapidapi-key": "b36cb36eedmsh0785bc594a50608p17069djsn6f651a5811e5",
    "x-rapidapi-host": "rakuten_webservice-rakuten-marketplace-product-search-v1.p.rapidapi.com"
};

// Configure axios with retry-like behavior and timeout
const axiosConfig = {
    timeout: 30000,
    headers: headers,
    params: params,
    httpsAgent: new (require('https')).Agent({
        rejectUnauthorized: false  // Bypass SSL verification
    })
};

const currentDir = __dirname;
const resultsDir = path.join(currentDir, 'results');
const csvPath = path.join(resultsDir, 'rakuten_products.csv');

// Create results directory if it doesn't exist
if (!fs.existsSync(resultsDir)) {
    fs.mkdirSync(resultsDir, { recursive: true });
}

function listUp(result) {
    const csvData = [];
    console.log(result.products || []);

    // Display first few products
    const products = result.products || [];
    for (let i = 0; i < Math.min(3, products.length); i++) {
        const product = products[i];
        const name = product.productName || 'N/A';
        const price = product.productPrice || 'N/A';
        const url = product.productUrl || 'N/A';
        
        csvData.push([name, price, url]);
    }

    // Write to CSV file
    const csvContent = 'Name,Price,URL\n' + 
        csvData.map(row => 
            row.map(field => `"${String(field).replace(/"/g, '""')}"`)
               .join(',')
        ).join('\n');

    fs.writeFileSync(csvPath, csvContent, 'utf-8');
    console.log(`✅ ${csvData.length} products listed up successfully!`);
}

// Method 1: Try with SSL verification bypassed
async function fetchRakutenData() {
    try {
        const response = await axios.get(url, axiosConfig);
        console.log("✅ SSL verification bypassed - Response received!");
        
        if (response.status === 200) {
            listUp(response.data);
        } else {
            console.log("Response Text:", response.data);
        }
        
    } catch (error) {
        console.log(`❌ Request failed: ${error.message}`);
        
        // Method 2: Try with different URL (direct RapidAPI endpoint)
        try {
            console.log("\n🔄 Trying alternative approach...");
            const altUrl = "https://rakuten-web-service.p.rapidapi.com/services/api/Product/Search/20170426";
            const altHeaders = {
                "X-RapidAPI-Key": "b36cb36eedmsh0785bc594a50608p17069djsn6f651a5811e5",
                "X-RapidAPI-Host": "rakuten-web-service.p.rapidapi.com"
            };
            
            const altConfig = {
                ...axiosConfig,
                headers: altHeaders
            };
            
            const response = await axios.get(altUrl, altConfig);
            console.log("✅ Alternative URL worked!");
            console.log("Status Code:", response.status);
            
            if (response.status === 200) {
                listUp(response.data);
            } else {
                console.log("Response Text:", response.data);
            }
            
        } catch (error2) {
            console.log(`❌ Alternative method also failed: ${error2.message}`);
            console.log("\n💡 Solutions to try:");
            console.log("1. Check if your RapidAPI subscription is active");
            console.log("2. Verify the API endpoint URL in RapidAPI dashboard");
            console.log("3. Update your API key if needed");
            console.log("4. Try using curl or Postman to test the endpoint directly");
        }
    }
}

// Run the script
fetchRakutenData();
