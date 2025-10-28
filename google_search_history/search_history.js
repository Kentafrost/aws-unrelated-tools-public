const sqlite3 = require('sqlite3').verbose();
const db = new sqlite3.Database('bookmarks.db');
const fs = require('fs');
const parse = require('csv-parse');

// Function to add browsing history data to the SQLite database
function add_bookmark(db_path, title, url) {

    // Connect to the SQLite database (or create it if it doesn't exist)
    const db = new sqlite3.Database(db_path);
    const stmt_create_db = 
    ("CREATE TABLE IF NOT EXISTS bookmarks (id INTEGER PRIMARY KEY AUTOINCREMENT,title TEXT NOT NULL,url TEXT NOT NULL)");

    // Create the bookmarks table if it doesn't exist
    if (!db) {
        console.log("Database connection failed.");
        console.log(`Creating database ${db_path}`);
        db.run(stmt_create_db, (err) => {
            if (err) {
                console.error("Error creating bookmarks table:", err);
            }
        });
    }
    
    
    // Insert the new bookmark into the bookmarks table
    const stmt_insert = ("INSERT INTO bookmarks (title, url) VALUES (?, ?)");
    db.run(stmt_insert, [title, url], (err) => {
        if (err) {
            console.error("Error inserting bookmark:", err);
        }
    });
    stmt_insert.finalize();

    // Commit the changes and close the connection
    db.close();
}


function gather_json_data(){
    
    const json_csv_path = "browsing_history.json"
    fs.createReadStream(json_csv_path);
    fs.readFile(json_csv_path, 'utf-8', (err, json_data) => {
        if (err) {
            console.error("Error reading JSON file:", err);
            return;
        }
        json_data = JSON.parse(json_data);
    

        console.log("Browsing History Data:");
        console.log(json_data);
        console.log("Total records:", json_data.length);

        const title_list = [];
        const url_list = [];

        for (const item of json_data) {
            const title = item.title;
            const url = item.url;
            if (title && url) {
                title_list.push(title);
                url_list.push(url);
                add_bookmark("bookmarks.db", title, url);
            }
        }
        return { title_list, url_list };
    });
}


// get history from my browser and add into db

const db_path = "browsing_history.db";
const { title_list, url_list } = gather_json_data();

for (let i = 0; i < title_list.length; i++) {
    add_bookmark(db_path, title_list[i], url_list[i]);
}