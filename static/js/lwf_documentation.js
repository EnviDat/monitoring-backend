// ************************************ Assign JSON path and JSON keys ***********************************************

const json_url = '/static/json/lwf_documentation.json';

const json_keys = ['page_title', 'api_title', 'into_text', 'nodata', 'app', 'model', 'parameter', 'parameter_several',
                    'start_date', 'end_date', 'start_datetime', 'end_datetime', 'parent_class'];


// -------------------------------  Call injectJson() passing JSON URL as an argument ----------------------------------

injectJson(json_url);


// ------------------------------- Function used to validate JSON file has required keys-------------------------------

// Throws error if one or more keys from 'keys' array does not exist in json_object, else returns true
function jsonKeysValid(jsonObject, keys) {

    let missingKeys = [];

    for (let i=0; i < keys.length; i++) {
        if (!jsonObject.hasOwnProperty(keys[i])) {
            missingKeys.push(keys[i]);
        }
    }

    if (missingKeys.length > 0) {
        throw new Error(`JSON file missing key(s): ${missingKeys}`);
    }
    return true;
}


function datesValid(startDate, endDate) {

    const start = new Date(startDate);
    const end = new Date(endDate);

    if (start >= end) {
        throw new Error(`JSON file start date or datetime ${startDate} cannot be greater than or equal to end date or datetime ${endDate}`);
    }
    return true;
}


// ----------------  Function used to assign innerHTML of element arrays and assign anchor href links ----------------

function assignElementsArray (elementsArray, elementString) {
   
    for (let i=0; i < elementsArray.length; i++) {
       
       elementsArray[i].innerHTML = elementString;
       
       if (elementsArray[i].tagName === 'A') {
           elementsArray[i].setAttribute("target", "_onblank");
           elementsArray[i].setAttribute("href", elementString);
       }
   }
}


// ------------------------------- Function used to assign innerHTML of elements --------------------------------------

function assignElements (data) {

    // ----------------------------- Template variables used once --------------------------------------------

    document.getElementById("page_title").innerHTML = data.page_title;
    document.getElementById("api_title").innerHTML = data.api_title;
    document.getElementById("intro_text").innerHTML = data.into_text;


    // ------------------------------- Template variables used multiple times --------------------------------

    let appElements = document.querySelectorAll("span.app_name");
    assignElementsArray(appElements, data.app);

    let modelElements = document.querySelectorAll("span.model_name");
    assignElementsArray(modelElements, data.model);

    let nodataElements = document.querySelectorAll("span.nodata_name");
    assignElementsArray(nodataElements, data.nodata);

    let parameterElements = document.querySelectorAll("span.parameter_name");
    assignElementsArray(parameterElements, data.parameter);

    let parameterSeveralElements = document.querySelectorAll("span.parameter_several");
    assignElementsArray(parameterSeveralElements, data.parameter_several);

    let parentClassElements = document.querySelectorAll("span.parent_class_name");
    assignElementsArray(parentClassElements, data.parent_class);


    // ----------------------------- URL template variables ---------------------------------------------------

    let urlModelsElements = document.querySelectorAll(".url_models");
    assignElementsArray(urlModelsElements, `${data.api_host}/${data.app}/models/${data.parent_class}/`);

    let urlNeadElements = document.querySelectorAll(".url_nead");
    assignElementsArray(urlNeadElements, `${data.api_host}/${data.app}/nead/${data.model}/${data.nodata}/${data.parent_class}/${data.start_date}/${data.end_date}/`);

    let urlNeadAllElements = document.querySelectorAll(".url_nead_all");
    assignElementsArray(urlNeadAllElements,`${data.api_host}/${data.app}/nead/${data.model}/${data.nodata}/${data.parent_class}/`);

    let urlCsvElements = document.querySelectorAll(".url_csv");
    assignElementsArray(urlCsvElements, `${data.api_host}/${data.app}/csv/${data.model}/${data.parameter}/${data.nodata}/${data.parent_class}/${data.start_date}/${data.end_date}/`);

    let urlCsvSeveralElements = document.querySelectorAll(".url_csv_several");
    assignElementsArray(urlCsvSeveralElements, `${data.api_host}/${data.app}/csv/${data.model}/${data.parameter_several}/${data.nodata}/${data.parent_class}/${data.start_date}/${data.end_date}/`);

    let urlJsonElements = document.querySelectorAll(".url_json");
    assignElementsArray(urlJsonElements, `${data.api_host}/${data.app}/json/${data.model}/${data.parameter}/${data.parent_class}/${data.start_datetime}/${data.end_datetime}/`);

    let urlJsonSeveralElements = document.querySelectorAll(".url_json_several");
    assignElementsArray(urlJsonSeveralElements, `${data.api_host}/${data.app}/json/${data.model}/${data.parameter_several}/${data.parent_class}/${data.start_datetime}/${data.end_datetime}/`);

    let urlDailyJsonElements = document.querySelectorAll(".url_daily_json");
    assignElementsArray(urlDailyJsonElements, `${data.api_host}/${data.app}/json/daily/${data.model}/${data.parameter}/${data.parent_class}/${data.start_date}/${data.end_date}/`);

    let urlDailyJsonSeveralElements = document.querySelectorAll(".url_daily_json_several");
    assignElementsArray(urlDailyJsonSeveralElements, `${data.api_host}/${data.app}/json/daily/${data.model}/${data.parameter_several}/${data.parent_class}/${data.start_date}/${data.end_date}/`);

    let urlDailyCsvElements = document.querySelectorAll(".url_daily_csv");
    assignElementsArray(urlDailyCsvElements, `${data.api_host}/${data.app}/csv/daily/${data.model}/${data.parameter}/${data.nodata}/${data.parent_class}/${data.start_date}/${data.end_date}/`);

    let urlDailyCsvSeveralElements = document.querySelectorAll(".url_daily_csv_several");
    assignElementsArray(urlDailyCsvSeveralElements, `${data.api_host}/${data.app}/csv/daily/${data.model}/${data.parameter_several}/${data.nodata}/${data.parent_class}/${data.start_date}/${data.end_date}/`);

    let urlMetadataElements = document.querySelectorAll(".url_metadata");
    assignElementsArray(urlMetadataElements, `${data.api_host}/${data.app}/metadata/${data.model}/${data.parameter}/${data.parent_class}/`);

    let urlMetadataSeveralElements = document.querySelectorAll(".url_metadata_several");
    assignElementsArray(urlMetadataSeveralElements, `${data.api_host}/${data.app}/metadata/${data.model}/${data.parameter_several}/${data.parent_class}/`);
}


// --------- Function to get JSON Data, validate JSON keys and fill html template elements with JSON values -----------

function injectJson(url) {

    let request = new XMLHttpRequest();
    request.open("GET", url, true);
    request.send();

    request.addEventListener("readystatechange", function() {

        let data;


        // ----------------------------- Load and parse JSON file---------------------------------------------------
        if (this.readyState === this.DONE) {

            data = JSON.parse(this.response);

            // ---------------------------- JSON validators --------------------------------------------------------

            // Validate JSON file has all required keys
            try {
                jsonKeysValid(data, json_keys);
            }
            catch (err) {
                alert(err);
            }

            // Validate start_date is less than end_date
            try {
                datesValid(data.start_date, data.end_date);
            }
            catch (err) {
                alert(err);
            }

            // Validate start_datetime is less than end_datetime
            try {
                datesValid(data.start_datetime, data.end_datetime);
            }
            catch (err) {
                alert(err);
            }

            // --------------------------- Assign HTML elements
            assignElements(data);

        }
    });
}

function generate_table() {

  let divTable = document.getElementById("div_table");
  console.log(divTable);

  const mydata = JSON.parse(document.getElementById('div_table').textContent);
  console.log(mydata);

  // let divTable = document.createElement("div"); //create new <div>
  // divTable.id = "tablediv";

    // creates a <table> element and a <tbody> element
  var tbl = document.createElement("table");
  var tblBody = document.createElement("tbody");

  // creating all cells
  for (var i = 0; i < 2; i++) {
    // creates a table row
    var row = document.createElement("tr");

    for (var j = 0; j < 2; j++) {
      // Create a <td> element and a text node, make the text
      // node the contents of the <td>, and put the <td> at
      // the end of the table row
      var cell = document.createElement("td");
      var cellText = document.createTextNode("cell in row "+i+", column "+j);
      cell.appendChild(cellText);
      row.appendChild(cell);
    }

    // add the row to the end of the table body
    tblBody.appendChild(row);
  }

  // put the <tbody> in the <table>
  tbl.appendChild(tblBody);
  // appends <table> into <body>
  divTable.appendChild(tbl);
  // sets the border attribute of tbl to 2;
  tbl.setAttribute("border", "2");
}

generate_table();


function populateParameterTable() {

    const mydata = JSON.parse(document.getElementById('objectdata').textContent);
    console.log(mydata);
    // let i = 0;

    let tag = ''; let i = 0;

    var msgContainer = document.createDocumentFragment();

    const  li = msgContainer.appendChild(document.createElement("li"));
        li.textContent = value;

    for (const[key, value] of Object.entries(mydata)) {
        let  li = msgContainer.appendChild(document.createElement("li"));
        li.textContent = value;
        // li.value = 'TEST';
        // tag = tag + "<h" + i + ">" + value + "</h" + i + ">";
        // // tag = `<li>${value}</li>`;
        // document.getElementById("demo").innerHTML = tag;
        i++;
    document.getElementById("demo").appendChild(msgContainer);



            // let liTag = document.createElement("li");
            // let valText = document.createTextNode(value);
            // liTag.appendChild(valText);
            // let element = document.getElementById("new" + i);
            // element.appendChild(liTag);
            // i++;
            // document.write(value);
            // document.write(`<p>${value}</p>`);
            // document.write(`<li>${value}</li>`);
    }
}

// populateParameterTable();
