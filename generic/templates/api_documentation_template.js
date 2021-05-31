// ************************************ Assign JSON path and JSON keys ***********************************************

const json_url = './api_documentation_template.json';

// TODO add new keys
const json_keys = ['page_title', 'api_title', 'into_text', 'nodata', 'app', 'model', 'parameter', 'parameter_several',
                    'start_date'];


// -------------------------------  Call injectJson() passing JSON URL as an argument ----------------------------------

injectJson(json_url);


// ------------------------------- Function used to validate JSON file has required keys-------------------------------

// Throws error if one or more keys from 'keys' array does not exist in json_object, else returns true
function jsonKeysValid(json_object, keys) {

    let missingKeys = [];

    for (let i=0; i < keys.length; i++) {
        if (!json_object.hasOwnProperty(keys[i])) {
            missingKeys.push(keys[i]);
        }
    }

    if (missingKeys.length > 0) {
        throw new Error('JSON file missing key(s): ' + missingKeys);
    }
    return true;
}


// ------------------------------- Function used to assign innerHTML of element arrays --------------------------------

function assignElementsArray (elementsArray, elementString) {
   for (let i=0; i < elementsArray.length; i++) {
       elementsArray[i].innerHTML = elementString;
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

    // ----------------------------- URL template variables --------------------------------------------------
    // TODO use querySelectorAll to fix URL href links in HTML
    let urlModelsElements = document.querySelectorAll("span.url_models");
    assignElementsArray(urlModelsElements, `${data.api_host}/${data.app}/models/`);

    let urlNeadElements = document.querySelectorAll(".url_nead");
    document.getElementById("test_link").setAttribute("href", `https://www.envidat.ch/data-api/${data.app}/nead/${data.model}/end/empty/${data.start_date}/${data.end_date}`)
    assignElementsArray(urlNeadElements, `https://www.envidat.ch/data-api/${data.app}/nead/${data.model}/end/empty/${data.start_date}/${data.end_date}`);

    // document.getElementById("url_nead").innerHTML = `https://www.envidat.ch/data-api/${data.app}/nead/${data.model}/end/empty/${data.start_date}/${data.end_date}`;

    document.getElementById("url_nead_all").innerHTML =  `https://www.envidat.ch/data-api/${data.app}/nead/${data.model}/end/empty/`;

    document.getElementById("url_csv").innerHTML = `https://www.envidat.ch/data-api/${data.app}/csv/${data.model}/${data.parameter}/end/-999/${data.start_date}/${data.end_date}/`;

    document.getElementById("url_csv_several").innerHTML = `https://www.envidat.ch/data-api/${data.app}/csv/${data.model}/${data.parameter_several}/end/-999/${data.start_date}/${data.end_date}/`;

    document.getElementById("url_json").innerHTML = `https://www.envidat.ch/data-api/${data.app}/json/${data.model}/${data.parameter}/2020-11-04T17:00:00/2020-11-10T00:00:00/`;

    document.getElementById("url_json_several").innerHTML = `https://www.envidat.ch/data-api/${data.app}/json/${data.model}/${data.parameter_several}/2020-11-04T17:00:00/2020-11-10T00:00:00/`;

    document.getElementById("url_daily_json").innerHTML = `http://www.envidat.ch/data-api/${data.app}/summary/daily/json/${data.model}/${data.parameter}/${data.start_date}/${data.end_date}/`;

    document.getElementById("url_daily_json_several").innerHTML = `http://www.envidat.ch/data-api/${data.app}/summary/daily/json/${data.model}/${data.parameter_several}/${data.start_date}/${data.end_date}/`;

    document.getElementById("url_daily_csv").innerHTML = `https://www.envidat.ch/data-api/${data.app}/summary/daily/csv/${data.model}/${data.parameter}/end/empty/${data.start_date}/${data.end_date}/`;

    document.getElementById("url_daily_csv_several").innerHTML = `https://www.envidat.ch/data-api/${data.app}/summary/daily/csv/${data.model}/${data.parameter_several}/end/empty/${data.start_date}/${data.end_date}/`;

    document.getElementById("url_metadata").innerHTML = `http://www.envidat.ch/data-api/${data.app}/metadata/${data.model}/${data.parameter}/`;

    document.getElementById("url_metadata_several").innerHTML = `http://www.envidat.ch/data-api/${data.app}/metadata/${data.model}/${data.parameter_several}/`;
}


// --------- Function to get JSON Data, validate JSON keys and fill html template elements with JSON values -----------

function injectJson(url) {

    let request = new XMLHttpRequest();
    request.open("GET", url, true);
    request.send();

    request.addEventListener("readystatechange", function() {

        let data;

        // Load and parse JSON file
        if (this.readyState === this.DONE) {

            data = JSON.parse(this.response);

            // Validate JSON file has required keys
            try {
                jsonKeysValid(data, json_keys);
            }
            catch (err) {
                alert(err);
            }

            // Assign HTML elements
            assignElements(data);

        }
    });
}
