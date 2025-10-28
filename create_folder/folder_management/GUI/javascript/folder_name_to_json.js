// Node.js でファイルやパスを扱う場合
const fs = require('fs');
const path = require('path');
const { exec } = require('child_process');

// __dirname は「このスクリプトファイルがあるディレクトリ」を指す
const current_directory = __dirname;
const parent_directory = path.dirname(current_directory);
const base_json_path = path.join(parent_directory, "json");

const folder_json = path.join(base_json_path, "folder_path.json");
const json_output = path.join(base_json_path, "files_data.json");


// Function to get video length using ffprobe command
function get_video_length(file_path) {
  return new Promise((resolve, reject) => {
    const videoExtensions = ['.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm'];
    const fileExt = path.extname(file_path).toLowerCase();
    
    if (!videoExtensions.includes(fileExt)) {
      return resolve("-");
    }

    // ffprobeコマンドを実行してビデオの長さを取得
    const command = `ffprobe -v quiet -show_entries format=duration -of csv=p=0 "${file_path}"`;
    
    exec(command, (error, stdout, stderr) => {
      if (error) {
        console.log(`Warning: Could not get video length for ${path.basename(file_path)}: ${error.message}`);
        return resolve("-");
      }

      const duration = parseFloat(stdout.trim());
      if (isNaN(duration)) {
        return resolve("-");
      }

      let result = "";
      if (duration >= 3600) {
        const hours = Math.floor(duration / 3600);
        const minutes = Math.floor((duration % 3600) / 60);
        result = minutes > 0 ? `${hours} hours ${minutes} minutes` : `${hours} hours`;
      } else if (duration >= 60) {
        const minutes = Math.floor(duration / 60);
        const seconds = Math.floor(duration % 60);
        result = seconds > 0 ? `${minutes} minutes ${seconds} seconds` : `${minutes} minutes`;
      } else {
        result = `${Math.floor(duration)} seconds`;
      }
      resolve(result);
    });
  });
}


async function walkDirectory(dir) {
  let results = [];

  // ディレクトリ内のエントリを取得
  const list = fs.readdirSync(dir, { withFileTypes: true });

  for (const entry of list) {
    const fullPath = path.join(dir, entry.name);

    if (entry.isDirectory()) {
      console.log(`Processing folder: ${fullPath}`);
      // 再帰的に探索
      results = results.concat(await walkDirectory(fullPath));
    } else {
      results.push(fullPath);
    }
  }

  return results;
}


async function list_files_in_directory(folder) {

    let all_files = [];

    // list up all folders in folder
    for (const [key, value] of Object.entries(folder)) {

        const folder_path = String(value);
        console.log(folder_path);
        await new Promise(resolve => setTimeout(resolve, 1000));

        // list up all folders in folder_path
        if (fs.existsSync(folder_path) === false) {
            console.error(`Error: The folder path ${folder_path} does not exist. Please check the path in folder_path.json.`);
            continue;
        }

        console.log(`Processing folder: ${folder_path}`);
        const files = await walkDirectory(folder_path);
        all_files = all_files.concat(files);
    }
    return all_files;
}

// main function to get folder names from json file, and list up all files in the folders
async function file_data_to_json() {

    // open json file to get folder names
    const fs = require('fs');

    // json file's initial content
    fs.writeFileSync(json_output, JSON.stringify([], null, 4), 'utf-8');

    let folder_names;
    try {
        const jsonData = fs.readFileSync(folder_json, 'utf-8');
        folder_names = JSON.parse(jsonData);
    } catch (err) {
        if (err.code === 'ENOENT') {
            console.error(`Error: The file ${folder_json} was not found.`);
            console.error('Please create the file and add folder names in JSON format, e.g., ["folder1", "folder2"]');
            process.exit(1);
        } else if (err instanceof SyntaxError) {
            folder_names = [];
        } else {
            throw err;
        }
    }

    const all_files = [];

    // list up all folders in the json file including parent key, value in json files
    const drives = Object.keys(folder_names); 
    
    const firstDrive = drives[0]; // "D-Drive"
    const secondDrive = drives[1]; // "Google-Drive"

    const folder1 = folder_names[firstDrive]["folders"];
    const folder2 = folder_names[secondDrive]["folders"];

    // list up all files in the folders
    all_files.push(...await list_files_in_directory(folder1));
    all_files.push(...await list_files_in_directory(folder2));

    console.log(`Total files found: ${all_files.length}`);

    // put files path, and name, tag(separated files name with "-") into json file
    const files_data = [];
    const extentions = [".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm"];


    for (const file_path of all_files) {
        const file_name = path.basename(file_path);

        if (!file_name.includes("-")) {
            console.log("");
            console.log(`No '-' in file name: '${file_name}'`);
            console.log("Skipping this file.");
            continue;
        }
        if (!extentions.some(ext => file_name.endsWith(ext))) {
            console.log("");
            console.log(`Unsupported file extension in file name: '${file_name}'`);
            continue;
        }

        const file_data_size = fs.statSync(file_path).size / 1024 / 1024;  // in MB
        const file_data_length = await get_video_length(file_path);

        const tag_list = [];
        let processed_file_name = file_name.replace(" - Made with Clipchamp", "");
        processed_file_name = processed_file_name.replace(" ", "");

        // delete extensions string from file name
        for (const ext of extentions) {
            processed_file_name = processed_file_name.replace(ext, "");
        }

        const tags = processed_file_name.split("-");

        for (const tag of tags) {
            tag_list.push(tag);
        }

        files_data.push({
            "path": file_path,
            "name": processed_file_name,
            "size_MB": `${file_data_size.toFixed(2)} MB`,
            "video_length": file_data_length,
            "tags": tag_list
        });
    }

    try {
        fs.writeFileSync(json_output, JSON.stringify(files_data, null, 4), 'utf-8');
        console.log(`File data has been written to ${json_output}`);
    } catch (err) {
        if (err.code === 'ENOENT') {
            console.error(`Error: The directory for ${json_output} does not exist. Please create it and try again.`);
        } else {
            console.error(`Error: Unable to write to ${json_output}. ${err.message}`);
        }
        process.exit(1);
    }
}

// window.file_data_to_json = file_data_to_json;

file_data_to_json();