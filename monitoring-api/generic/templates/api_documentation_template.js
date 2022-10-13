// ************************************ Assign JSON path and JSON keys ***********************************************

const json_url = "./api_documentation_template.json";

const json_keys = [
  "page_title",
  "api_title",
  "into_text",
  "nodata",
  "app",
  "model",
  "parameter",
  "parameter_several",
  "start_date",
  "end_date",
  "start_datetime",
  "end_datetime",
  "parent_class",
];

// -------------------------------  Call injectJson() passing JSON URL as an argument ----------------------------------

injectJson(json_url);

// ------------------------------- Function used to validate JSON file has required keys-------------------------------

// Throws error if one or more keys from 'keys' array does not exist in json_object, else returns true
function jsonKeysValid(jsonObject, keys) {
  let missingKeys = [];

  for (let i = 0; i < keys.length; i++) {
    if (!jsonObject.hasOwnProperty(keys[i])) {
      missingKeys.push(keys[i]);
    }
  }

  if (missingKeys.length > 0) {
    throw new Error(`JSON file missing key(s): ${missingKeys}`);
  }
  return true;
}

// Throws error if startDate is greater than or equal to endDate
function datesValid(startDate, endDate) {
  const start = new Date(startDate);
  const end = new Date(endDate);

  if (start >= end) {
    throw new Error(
      `JSON file start date or datetime ${startDate} cannot be greater than or equal to end date or datetime ${endDate}`
    );
  }
  return true;
}

// ----------------  Function used to assign innerHTML of element arrays and assign anchor href links ----------------

function assignElementsArray(elementsArray, elementString) {
  for (let i = 0; i < elementsArray.length; i++) {
    elementsArray[i].innerHTML = elementString;

    if (elementsArray[i].tagName === "A") {
      elementsArray[i].setAttribute("target", "_onblank");
      elementsArray[i].setAttribute("href", elementString);
    }
  }
}

// ------------------------------- Function used to assign innerHTML of elements --------------------------------------

function assignElements(data) {
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

  let parameterSeveralElements = document.querySelectorAll(
    "span.parameter_several"
  );
  assignElementsArray(parameterSeveralElements, data.parameter_several);

  let parentClassElements = document.querySelectorAll("span.parent_class_name");
  assignElementsArray(parentClassElements, data.parent_class);

  // ----------------------------- URL template variables ---------------------------------------------------

  let urlModelsElements = document.querySelectorAll(".url_models");
  assignElementsArray(
    urlModelsElements,
    `${data.api_host}/${data.app}/models/${data.parent_class}/`
  );

  let urlNeadElements = document.querySelectorAll(".url_nead");
  assignElementsArray(
    urlNeadElements,
    `${data.api_host}/${data.app}/nead/${data.model}/${data.nodata}/${data.parent_class}/${data.start_date}/${data.end_date}/`
  );

  let urlNeadAllElements = document.querySelectorAll(".url_nead_all");
  assignElementsArray(
    urlNeadAllElements,
    `${data.api_host}/${data.app}/nead/${data.model}/${data.nodata}/${data.parent_class}/`
  );

  let urlCsvElements = document.querySelectorAll(".url_csv");
  assignElementsArray(
    urlCsvElements,
    `${data.api_host}/${data.app}/csv/${data.model}/${data.parameter}/${data.nodata}/${data.parent_class}/${data.start_date}/${data.end_date}/`
  );

  let urlCsvSeveralElements = document.querySelectorAll(".url_csv_several");
  assignElementsArray(
    urlCsvSeveralElements,
    `${data.api_host}/${data.app}/csv/${data.model}/${data.parameter_several}/${data.nodata}/${data.parent_class}/${data.start_date}/${data.end_date}/`
  );

  let urlJsonElements = document.querySelectorAll(".url_json");
  assignElementsArray(
    urlJsonElements,
    `${data.api_host}/${data.app}/json/${data.model}/${data.parameter}/${data.parent_class}/${data.start_datetime}/${data.end_datetime}/`
  );

  let urlJsonSeveralElements = document.querySelectorAll(".url_json_several");
  assignElementsArray(
    urlJsonSeveralElements,
    `${data.api_host}/${data.app}/json/${data.model}/${data.parameter_several}/${data.parent_class}/${data.start_datetime}/${data.end_datetime}/`
  );

  let urlDailyJsonElements = document.querySelectorAll(".url_daily_json");
  assignElementsArray(
    urlDailyJsonElements,
    `${data.api_host}/${data.app}/json/daily/${data.model}/${data.parameter}/${data.parent_class}/${data.start_date}/${data.end_date}/`
  );

  let urlDailyJsonSeveralElements = document.querySelectorAll(
    ".url_daily_json_several"
  );
  assignElementsArray(
    urlDailyJsonSeveralElements,
    `${data.api_host}/${data.app}/json/daily/${data.model}/${data.parameter_several}/${data.parent_class}/${data.start_date}/${data.end_date}/`
  );

  let urlDailyCsvElements = document.querySelectorAll(".url_daily_csv");
  assignElementsArray(
    urlDailyCsvElements,
    `${data.api_host}/${data.app}/csv/daily/${data.model}/${data.parameter}/${data.nodata}/${data.parent_class}/${data.start_date}/${data.end_date}/`
  );

  let urlDailyCsvSeveralElements = document.querySelectorAll(
    ".url_daily_csv_several"
  );
  assignElementsArray(
    urlDailyCsvSeveralElements,
    `${data.api_host}/${data.app}/csv/daily/${data.model}/${data.parameter_several}/${data.nodata}/${data.parent_class}/${data.start_date}/${data.end_date}/`
  );

  let urlMetadataElements = document.querySelectorAll(".url_metadata");
  assignElementsArray(
    urlMetadataElements,
    `${data.api_host}/${data.app}/metadata/${data.model}/${data.parameter}/${data.parent_class}/`
  );

  let urlMetadataSeveralElements = document.querySelectorAll(
    ".url_metadata_several"
  );
  assignElementsArray(
    urlMetadataSeveralElements,
    `${data.api_host}/${data.app}/metadata/${data.model}/${data.parameter_several}/${data.parent_class}/`
  );
}

// ------------------------------- Function used to generate and populate Parameter List table -----------------------

function populateParameterTable() {
  // Get parameters from context passed to html template
  const parameters = JSON.parse(
    document.getElementById("parameter_table").textContent
  );

  // Create table and tbody elements
  const tbl = document.createElement("table");
  const tblBody = document.createElement("tbody");

  // Create header row and cells
  const headerRow = document.createElement("tr");

  const headerParameter = document.createElement("th");
  headerParameter.innerHTML = "Parameter";
  headerRow.appendChild(headerParameter);

  const headerName = document.createElement("th");
  headerName.innerHTML = "Name";
  headerRow.appendChild(headerName);

  const headerUnits = document.createElement("th");
  headerUnits.innerHTML = "Units";
  headerRow.appendChild(headerUnits);

  tblBody.appendChild(headerRow);

  // Populate rows of table
  const params = Object.values(parameters);

  for (let i = 0; i < params.length; i++) {
    let row = document.createElement("tr");

    let cellParam = document.createElement("td");
    cellParam.innerHTML = params[i].param;
    row.appendChild(cellParam);

    let cellLongName = document.createElement("td");
    cellLongName.innerHTML = params[i].long_name;
    row.appendChild(cellLongName);

    let cellUnits = document.createElement("td");
    cellUnits.innerHTML = params[i].units;
    row.appendChild(cellUnits);

    // Add the row to the end of the table body
    tblBody.appendChild(row);
  }

  // Put the <tbody> in the <table>
  tbl.appendChild(tblBody);

  // Append <table> into divTable
  const divTable = document.getElementById("parameter_table");
  divTable.appendChild(tbl);
}

// ---- Function to get and validate JSON Data, fill html template elements and generate Parameter List table --------

function injectJson(url) {
  let request = new XMLHttpRequest();
  request.open("GET", url, true);
  request.send();

  request.addEventListener("readystatechange", function () {
    let data;

    // ----------------------------- Load and parse JSON file--------
    if (this.readyState === this.DONE) {
      data = JSON.parse(this.response);

      // ---------------------------- JSON validators --------------

      // Validate JSON file has all required keys
      try {
        jsonKeysValid(data, json_keys);
      } catch (err) {
        alert(err);
      }

      // Validate start_date is less than end_date
      try {
        datesValid(data.start_date, data.end_date);
      } catch (err) {
        alert(err);
      }

      // Validate start_datetime is less than end_datetime
      try {
        datesValid(data.start_datetime, data.end_datetime);
      } catch (err) {
        alert(err);
      }

      //  --- Populate Parameter List table ---
      populateParameterTable();

      // --- Assign HTML elements -------------
      assignElements(data);
    }
  });
}
