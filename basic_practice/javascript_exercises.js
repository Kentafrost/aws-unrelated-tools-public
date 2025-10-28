const test = "This is a test string.";
const test_list = { key1: "value1", key2: "value2" };

for (const [key, value] of Object.entries(test_list)){
    console.log(`${key}: ${value}`);
    
    if (key === "key1") {
        console.log("Key1 found!");
    } else {
        console.log(`This is not key1. This one is ${key}`);
    }
}

const test_array = ["item1", "item2", "item3"];

for (const item of test_array) {
    console.log(item);

    if (item.includes("1")) {
        console.log("Item contains '1'");
    } else {
        console.log("Item does not contain '1'");
    }
}

function character_greeting() {
    const character = document.getElementById("greeting").querySelector("input[name='character']").value;
    let msg = "Alice";
    if (character === "Alice") {
        msg = "In Kivotos, INM is embarrassing! It's so clear. Stop Alice! You gotta stop!";
    } else {
        msg = `Hello, ${character}! Welcome!`;
    }
    const return_msg = document.getElementById("msg_display");
    return_msg.innerHTML = msg;
}

try {
    const result = character_greeting("Alice");
    const result2 = character_greeting("Bob");

    console.log(result);
    console.log(result2);
} catch (error) {
    console.error("Error occurred:", error);
}

function data() {
    const input = document.getElementById("data").querySelector("input[name='content']").value;
    const display = document.getElementById("data_display");
    display.innerHTML = "You entered: " + input;
}


function character_form() {
    const form = document.getElementById("form");
    const name = form.querySelector("input[name='character_name']").value;
    const age = form.querySelector("input[name='age']").value;
    const role = form.querySelector("input[name='role']").value;
    const quote = form.querySelector("input[name='quote']").value;

    if (name === "Alice") {
        msg = "In Kivotos, INM is embarrassing! It's so clear. Stop Alice! You gotta stop!";
        img = "<img src='image/Alice.webp' alt='Alice' width='100'>";
    } else {
        msg = `Hello, ${name}! Welcome!`;
        img = "<img src='image/Default.webp' alt='Default' width='100'>";
    }
    
    const form_data = {
        name: name,
        age: age,
        role: role,
        quote: quote,
        msg: msg,
        img: img
    }

    document.getElementById("form_display").innerHTML = `
        <br>Name: ${form_data.name}</br>
        <br>Age: ${form_data.age}</br>
        <br>Role: ${form_data.role}</br>
        <br>Quote: <strong>${form_data.quote}</strong></br>
        <br>Message: <h3><strong>${form_data.msg}</strong></h3></br>
        <br>${form_data.img}</br>
    `;
}