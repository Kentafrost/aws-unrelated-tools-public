## Rakuten API Integration

This project uses the Rakuten Product Search API to retrieve item information based on specific keywords or categories.  
The goal is to streamline product comparison by exporting relevant data into a CSV file for quick analysis and set to send me notifications for the public uses.

### Use Case

- Search for items using Rakuten's API
- Extract key attributes (e.g., item name, price, shop name, URL)
- Save results into a structured CSV file and send it to my e-mail address
- Compare items efficiently without manual browsing

### Technologies Used

- Python (requests, csv)
- Javascript
- Rakuten API (Product Search)

### Example Output

| Item Name | Price | Shop | URL |
|-----------|-------|------|-----|
| Sample A  | ¥1,980 | ShopX | https://... |
| Sample B  | ¥2,480 | ShopY | https://... |

### Notes

- This tool is intended for personal use and non-commercial product research.
- API key is required. Please register via [Rakuten Developers](https://webservice.rakuten.co.jp/) and set it in your environment variables.

