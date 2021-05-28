

// -------------------------------  Call loadJson() passing JSON URL as an argument ----------------------------------
loadJson('./api_documentation_template.json');


// ------------------------------- Function used to assign innerHTML of element arrays --------------------------------

function assignElements (elementsArray, elementString) {
   for (let i=0; i < elementsArray.length; i++) {
       elementsArray[i].innerHTML = elementString;
   }
}


// ----------------------------- Function to get JSON Data and fill html template elements with JSON values -----------

function loadJson(url) {

    let request = new XMLHttpRequest();
    request.open("GET", url, true);
    request.send();

    request.addEventListener("readystatechange", function() {

        let data;

        if (this.readyState === this.DONE) {

            data = JSON.parse(this.response);

            // ----------------------------- Template variables used once --------------------------------------------
            document.getElementById("page_title").innerHTML = data.page_title;
            document.getElementById("api_title").innerHTML = data.api_title;
            document.getElementById("intro_text").innerHTML = data.into_text;

            // ------------------------------- Template variables used multiple times --------------------------------
            let appElements = document.querySelectorAll("span.app_name");
            assignElements(appElements, data.app);

            let modelElements = document.querySelectorAll("span.model_name");
            assignElements(modelElements, data.model);

            let nodataElements = document.querySelectorAll("span.nodata_name");
            assignElements(nodataElements, data.nodata);

            let parameterElements = document.querySelectorAll("span.parameter_name");
            assignElements(parameterElements, data.parameter);

            let parameterSeveralElements = document.querySelectorAll("span.parameter_several");
            assignElements(parameterSeveralElements, data.parameter_several);

            // ----------------------------- URL template variables --------------------------------------------------
            let urlModelsElements = document.querySelectorAll("span.url_models");
            assignElements(urlModelsElements, `https://www.envidat.ch/data-api/${data.app}/models/`);

            document.getElementById("url_nead").innerHTML = `https://www.envidat.ch/data-api/${data.app}/nead/${data.model}/end/empty/2020-11-03/2020-11-06`;

            document.getElementById("url_nead_all").innerHTML =  `https://www.envidat.ch/data-api/${data.app}/nead/${data.model}/end/empty/`;

            document.getElementById("url_csv").innerHTML = `https://www.envidat.ch/data-api/${data.app}/csv/${data.model}/${data.parameter}/end/-999/2020-11-04/2020-11-06/`;

            document.getElementById("url_csv_several").innerHTML = `https://www.envidat.ch/data-api/${data.app}/csv/${data.model}/${data.parameter_several}/end/-999/2020-11-04/2020-11-06/`;

            document.getElementById("url_json").innerHTML = `https://www.envidat.ch/data-api/${data.app}/json/${data.model}/${data.parameter}/2020-11-04T17:00:00/2020-11-10T00:00:00/`;

            document.getElementById("url_json_several").innerHTML = `https://www.envidat.ch/data-api/${data.app}/json/${data.model}/${data.parameter_several}/2020-11-04T17:00:00/2020-11-10T00:00:00/`;

            document.getElementById("url_daily_json").innerHTML = `http://www.envidat.ch/data-api/${data.app}/summary/daily/json/${data.model}/${data.parameter}/2020-11-03/2020-11-06/`;

            document.getElementById("url_daily_json_several").innerHTML = `http://www.envidat.ch/data-api/${data.app}/summary/daily/json/${data.model}/${data.parameter_several}/2020-11-03/2020-11-06/`;

            document.getElementById("url_daily_csv").innerHTML = `https://www.envidat.ch/data-api/${data.app}/summary/daily/csv/${data.model}/${data.parameter}/end/empty/2020-11-01/2020-11-06/`;

            document.getElementById("url_daily_csv_several").innerHTML = `https://www.envidat.ch/data-api/${data.app}/summary/daily/csv/${data.model}/${data.parameter_several}/end/empty/2020-11-01/2020-11-06/`;

            document.getElementById("url_metadata").innerHTML = `http://www.envidat.ch/data-api/${data.app}/metadata/${data.model}/${data.parameter}/`;

            document.getElementById("url_metadata_several").innerHTML = `http://www.envidat.ch/data-api/${data.app}/metadata/${data.model}/${data.parameter_several}/`;

        }
    });
}
