// ----------------------------- Template variables used once -------------------------------------------------

let pageTitle = "GC-Net API";
document.getElementById("page_title").innerHTML = pageTitle;

let apiTitle = "GC-Net API Documentation";
document.getElementById("api_title").innerHTML = apiTitle;

let introText =
  "Greenland Climate Network (GC-Net) Automated Weather Stations (AWS) collect climate information on\n" +
  "                    Greenland's ice sheet. They are equipped with communication satellite transmitters that enable near real time\n" +
  "                    monitoring of weather conditions on the Greenland ice sheet. Transmission latency is typically 1-2 hours,\n" +
  "                    and occasionally as long as 48 hours. All times displayed are in UTC (Coordinated Universal Time).\n" +
  "                    Hourly average data are transmitted via a satellite link (GOES or ARGOS) throughout the year.\n" +
  "                    In addition, measurements are stored in solid state memory. The system is powered with two 100 Ah batteries,\n" +
  "                    charged by 10 W or 20 W solar panels. The satellite data-link is powered by two separate 100 Ah batteries\n" +
  "                    connected to a 20 W solar panel. This setup guarantees continuous data recordings and storage,\n" +
  "                    even in the case of satellite transmission failure.";
document.getElementById("intro_text").innerHTML = introText;

// ------------------------------- Function used to assign innerHTML of element arrays ------------------------

function assignElements(elementsArray, elementString) {
  for (let i = 0; i < elementsArray.length; i++) {
    elementsArray[i].innerHTML = elementString;
  }
}

// ------------------------------- Template variables used multiple times -------------------------------------

let app = "gcnet";
let appElements = document.querySelectorAll("span.app_name");
assignElements(appElements, app);

let model = "swisscamp";
let modelElements = document.querySelectorAll("span.model_name");
assignElements(modelElements, model);

let nodata = "-999";
let nodataElements = document.querySelectorAll("span.nodata_name");
assignElements(nodataElements, nodata);

let parameter = "airtemp1";
let parameterElements = document.querySelectorAll("span.parameter_name");
assignElements(parameterElements, parameter);

let parameterSeveral = "airtemp1,airtemp2,swin,rh1";
let parameterSeveralElements = document.querySelectorAll(
  "span.parameter_several"
);
assignElements(parameterSeveralElements, parameterSeveral);

// ----------------------------- URL variables ---------------------------------------------------------------

urlModels = `https://www.envidat.ch/data-api/${app}/models/`;
let urlModelsElements = document.querySelectorAll("span.url_models");
assignElements(urlModelsElements, urlModels);

urlNEAD = `https://www.envidat.ch/data-api/${app}/nead/${model}/end/empty/2020-11-03/2020-11-06/`;
document.getElementById("url_nead").innerHTML = urlNEAD;

urlNEADAll = `https://www.envidat.ch/data-api/${app}/nead/${model}/end/empty/`;
document.getElementById("url_nead_all").innerHTML = urlNEADAll;

urlCSV = `https://www.envidat.ch/data-api/${app}/csv/${model}/${parameter}/end/-999/2020-11-04/2020-11-06/`;
document.getElementById("url_csv").innerHTML = urlCSV;

urlCSVSeveral = `https://www.envidat.ch/data-api/${app}/csv/${model}/${parameterSeveral}/end/-999/2020-11-04/2020-11-06/`;
document.getElementById("url_csv_several").innerHTML = urlCSVSeveral;

urlJSON = `https://www.envidat.ch/data-api/${app}/json/${model}/${parameter}/2020-11-04T17:00:00/2020-11-10T00:00:00/`;
document.getElementById("url_json").innerHTML = urlJSON;

urlJSONSeveral = `https://www.envidat.ch/data-api/${app}/json/${model}/${parameterSeveral}/2020-11-04T17:00:00/2020-11-10T00:00:00/`;
document.getElementById("url_json_several").innerHTML = urlJSONSeveral;

urlDailyJSON = `http://www.envidat.ch/data-api/${app}/summary/daily/json/${model}/${parameter}/2020-11-03/2020-11-06/`;
document.getElementById("url_daily_json").innerHTML = urlDailyJSON;

urlDailyJSONSeveral = `http://www.envidat.ch/data-api/${app}/summary/daily/json/${model}/${parameterSeveral}/2020-11-03/2020-11-06/`;
document.getElementById("url_daily_json_several").innerHTML =
  urlDailyJSONSeveral;

urlDailyCSV = `https://www.envidat.ch/data-api/${app}/summary/daily/csv/${model}/${parameter}/end/empty/2020-11-01/2020-11-06/`;
document.getElementById("url_daily_csv").innerHTML = urlDailyCSV;

urlDailyCSVSeveral = `https://www.envidat.ch/data-api/${app}/summary/daily/csv/${model}/${parameterSeveral}/end/empty/2020-11-01/2020-11-06/`;
document.getElementById("url_daily_csv_several").innerHTML = urlDailyCSVSeveral;

urlMetadata = `http://www.envidat.ch/data-api/${app}/metadata/${model}/${parameter}/`;
document.getElementById("url_metadata").innerHTML = urlMetadata;

urlMetadataSeveral = `http://www.envidat.ch/data-api/${app}/metadata/${model}/${parameterSeveral}/`;
document.getElementById("url_metadata_several").innerHTML = urlMetadataSeveral;

// ---------------------------------- GC-Net Specific -----------------------------------------------------------

let honoraryText =
  "Prof. Dr. Konrad Steffen was the principal investigator of GC-Net and tragically died during a research\n" +
  "                            expedition in Greenland on August 8, 2020 in an accident. His dedication made GC-Net possible and he\n" +
  "                            encouraged the developers of this API to ensure that the application was robust to guarantee access to the\n" +
  "                            meteorological data. Prof. Dr. Steffen was a committed scientist and generous friend and is deeply missed.";
document.getElementById("honorary_text").innerHTML = honoraryText;
