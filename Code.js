function querySimfin(simfinID, timeValues, indicatorIds) {
  //General Info
  var apiKey = "myApiKey"
  var metaID = "6";
  var operator = "eq";
  var request = "";
  var method = "post";
  var contentType = "application/json";
  var payload = "";
  
  //Create full payload json structure as a string based on requested indicator and time values
  payload = '{"search":[';
  
  for (var i=0; i<indicatorIds.length; i++) {
    for (var j=0; j<timeValues.length; j++) {
      payload = payload + '{"indicatorId": "' + indicatorIds[i] + '","meta": [{"id": ' + metaID + ', "value": "' + timeValues[j] + '", "operator": "' + operator + '"}]}';
      if ((i >= indicatorIds.length-1) && (j >= timeValues.length-1)) {
        payload = payload;
      } else {
        payload = payload + ',';
      }
    }
  }
  
  payload = payload +'],"simIdList": [' + simfinID + ']}';
  payload = JSON.parse(payload);
  
  //Create request structure
  request =
      {
        "method": method,
        "contentType": contentType,
        "payload" : JSON.stringify(payload)
      };
  
  //Perform query for stock data
  var queryURL = "https://simfin.com/api/v1/finder?api-key=" + apiKey;
  var query = UrlFetchApp.fetch(queryURL, request);
  var queryString = query.getContentText();
  var queryJSON = JSON.parse(queryString);
  
  //Parse the result into a 2D array [timeValues, indicatorIds]
  var resultArray = new Array(indicatorIds.length);
  for (var i=0; i<resultArray.length; i++) {
    resultArray[i] = new Array(timeValues.length);
  }
  
  for (var i=0; i<resultArray.length; i++) {
    for (var j=0; j<resultArray[0].length; j++) {
      resultArray[i][j] = queryJSON.results[0].values[(i*resultArray[0].length)+j].value;
    }
  }
  
  return resultArray;
}



function assessStock() {
  //General Info
  var apiKey = "Sy9mGPTylcXRXrLlMk4HDQQyHNGzs5Tf";
  
  
  //Gather data from the spreadsheet
  var compareSheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("Comparator");
  var tickerRange = "A2";
  var tickerValue = compareSheet.getRange(tickerRange).getValue();
  var ticker = tickerValue;
  
  //Perform initial query for metadata on the given stock ticker
  var queryURL01 = "https://simfin.com/api/v1/info/find-id/ticker/" + ticker + "?api-key=" + apiKey;
  var query01 = UrlFetchApp.fetch(queryURL01);
  var queryString01 = query01.getContentText();
  var queryJSON01 = JSON.parse(queryString01);
  var tickerID = queryJSON01[0].simId;
  var tickerName = queryJSON01[0].name;
  
  //Get Year, Month, and Day as numbers from today's date
  var today = new Date();
  var dd = today.getDate();
  var mm = today.getMonth() + 1; //January comes out as 0
  var yyyy = today.getFullYear();
  
  //Solve for the current quarter based on the current month
  if(mm < 4){var qq = 1;}
  else if(mm < 7){var qq = 2;}
  else if(mm < 10){var qq = 3;}
  else{var qq = 4;}
  
  //Create an array with all the quarters of the year starting with the current one
  if(qq = 1){var quarterArray = ["Q1","Q2","Q3","Q4"];}
  else if(qq = 2){var quarterArray = ["Q2","Q3","Q4","Q1"];}
  else if(qq = 3){var quarterArray = ["Q3","Q4","Q1","Q2"];}
  else{var quarterArray = ["Q4","Q1","Q2","Q3"];}
  
  //Create an array for the current and previous 4 years
  var yearArray = [yyyy,yyyy-1,yyyy-2,yyyy-3,yyyy-4];
  for(var i in yearArray){yearArray[i] = yearArray[i].toString();}
  
  //Create strings that describe the current year, month, day, and quarter
  var currentYear = yearArray[0];
  var currentMonth = mm.toString();
  var currentDay = dd.toString();
  var currentQuarter = quarterArray[0];
  
  //Create an array to fill with the stock info
  var outputArray = [
    [ticker,tickerName,"ID#: "+tickerID,"","","","","","","","","","","","","","","","",""],
    ["","","","","","","","","","","","","","","","","","","",""],
    [yearArray[0],"","","","","","","","","","","","","","","","","","",""],
    [yearArray[1],"","","","","","","","","","","","","","","","","","",""],
    [yearArray[2],"","","","","","","","","","","","","","","","","","",""],
    [yearArray[3],"","","","","","","","","","","","","","","","","","",""],
    [yearArray[4],"","","","","","","","","","","","","","","","","","",""],
    ["","","","","","","","","","","","","","","","","","","",""],
    ["Nasdaq 12 Links","","","","","","","","","","","","","","","","","","",""],
    ["","","","","","","","","","","","","","","","","","","",""],
    ["Result","","","","","","","","","","","","","","","","","","",""]
  ];
  
  //Create strings with equations for important Google Finance metrics
  var googEquation = new Array(1);
  googEquation[0] = '=concatenate("Price: $", GOOGLEFINANCE("' + ticker + '", "price"))';     //calculate current price
  googEquation[1] = '=concatenate("Day Volume: ", ((GOOGLEFINANCE("' + ticker + '", "volume")' + '/' + 'GOOGLEFINANCE("' + ticker + '", "volumeavg"))' + '-1)*100, "%")';     //calculate percentage of current volume vs average volume
  googEquation[2] = '=concatenate("52w High: $", GOOGLEFINANCE("' + ticker + '", "high52"))';     //calculate 52 week high
  googEquation[3] = '=concatenate("52w Low: $", GOOGLEFINANCE("' + ticker + '", "low52"))';     //calculate 52 week low
  googEquation[4] = '=concatenate("Beta: ", GOOGLEFINANCE("' + ticker + '", "beta"))';     //calculate beta
  
  for (var i=0; i<googEquation.length; i++) {
    outputArray[0][i + 3] = googEquation[i];
  }
  
  //Create links to analyze the Nasdaq 12 and put them in the outputArray
  var nasdaq12Links = [,,,,,,,,,,,,];
  //Check that total revenue is increasing for the last 3 years - Revenue=1-1
  nasdaq12Links[1] = "https://www.nasdaq.com/symbol/" + ticker + "/revenue-eps";
  //Check that EPS is increasing for the last 3 years - EPS(basic)=4-12   EPS(dilluted)=4-13
  nasdaq12Links[2] = "https://www.nasdaq.com/symbol/" + ticker + "/revenue-eps";
  //Check that Return on Equity (ROE) is increasing for the last 2 years (ROE = AvgShareHolderEquity(past year) / NetProfit(past year)) - ROE=4-7   NetIncome-1-58
  nasdaq12Links[3] = "https://www.nasdaq.com/symbol/" + ticker + "/financials?query=ratios";
  //Check if consensus analyst recommendations are currently at "buy" or "strong buy"
  nasdaq12Links[4] = "https://www.nasdaq.com/symbol/" + ticker + "/recommendations";
  //Check if EPS has beaten the EPS Target for the last 4 quarters straight (is all earnings surprises are positive) - EPS(basic)=4-12   EPS(dilluted)=4-13   
  nasdaq12Links[5] = "https://www.nasdaq.com/symbol/" + ticker + "/earnings-surprise";
  //Check if EPS forcast numbers increase year over year (don't know if this is for past or future)
  nasdaq12Links[6] = "https://www.nasdaq.com/symbol/" + ticker + "/earnings-forecast";
  //Check if the earnings growth number for longterm/5-years in the future is above 8%
  nasdaq12Links[7] = "https://www.nasdaq.com/symbol/" + ticker + "/earnings-growth";
  //Check that PEG ratio os less than 1.0 (PEG = PE / Expected12MonthGrowthRate)
  nasdaq12Links[8] = "https://www.nasdaq.com/symbol/" + ticker + "/peg-ratio";
  //Check that the PE is higher than the industry average PE - PE Ratio=4-14
  nasdaq12Links[9] = "https://www.nasdaq.com/symbol/" + ticker + "/analyst-research";
  //Check that days to cover is less than 2 days (DTC = ShortInterestShares / AvgTradingVolume)
  nasdaq12Links[10] = "https://www.nasdaq.com/symbol/" + ticker + "/short-interest";
  //Check that insider trading net activity has been positive for the last 3 months straight
  nasdaq12Links[11] = "https://www.nasdaq.com/symbol/" + ticker + "/insider-trades";
  //Check that the weighted alpha is currently positive
  nasdaq12Links[12] = "https://www.nasdaq.com/markets/barchart-sectors.aspx?symbol=" + ticker;
  
  var nasdaqRow = outputArray.length - 3;
  var nasdaqCol = 1;
  for (var i=0; i<nasdaq12Links.length; i++) {
    outputArray[nasdaqRow][i+nasdaqCol] = nasdaq12Links[i];
  }
  
  
  //Create variables for the query data call request
  var timeValue = ["ttm","ttm-1","ttm-2","ttm-3","ttm-4"];
  //Indicators can be found at this link: https://simfin.com/data/help/main?topic=api-indicators
  var indicatorIDList = [
    [
      "1-1",     //Revenue
      "4-12",    //EPS(basic)
      "4-7"     //Return on Equity (RoE)
    ],
    [
      "1-58",    //Net Income(common shareholders)
      "2-41",    //Total Assets
      "4-6"     //Total Debt
    ],
    [
      "2-84",    //Total Equity
      "3-32",    //Dividends Paid
      "4-0"     //Gross Margin
    ],
    [
      "4-1",     //Operating Margin
      "4-2",     //Net Profit Margin
      "4-5"     //Debt to Assets Ratio
    ],
    [
      "4-29",    //Dividends per Share
      "4-14",    //Price to Earnings Ratio (PE)
      "0-73"     //Sector Classification
    ]   //Length = 15
  ];
  
  //Perform second query for stock data
  var resultArray = new Array(1);
  for (var i=0; i<indicatorIDList.length; i++) {
    resultArray[i] = querySimfin(tickerID, timeValue, indicatorIDList[i]);
  }
  
  //Merge the resultArrays into a single array
  var fullArray = new Array(resultArray[0][0].length);
  for (var i=0; i<fullArray.length; i++) {
      fullArray[i] = new Array(resultArray.length*resultArray[0].length);
  }
  
  for (var i=0; i<resultArray.length; i++) {
    for (var j=0; j<resultArray[0].length; j++) {
      for (var k=0; k<resultArray[0][0].length; k++) {
        fullArray[k][i*resultArray[0].length+j] = resultArray[i][j][k];
      }
    }
  }
  
  //Pass the resultant array into the outputArray
  var labelRow = 1;    //row to place the data labels (starts at 0)
  var labelCol = 1;    //first column to place data labels (starts at 0)
  var outputRow = labelRow + 1;   //first row to place the output data (starts at 0)
  var outputCol = labelCol;   //first column to place the output data (starts at 0)
  
  for (var i=0; i<fullArray.length; i++) {
    for (var j=0; j<fullArray[0].length; j++) {
      outputArray[i+outputRow][j+outputCol] = fullArray[i][j];
    }
  }
  
  //Add labels to data columns in output array
  var indNameArray = new Array(1);
  for (var i=0; i<indicatorIDList.length; i++) {
    for (var j=0; j<indicatorIDList[0].length; j++) {
      var indName = labelIndicators(indicatorIDList[i][j]);
      indNameArray[i*indicatorIDList[0].length+j] = indName;
      outputArray[labelRow][i*indicatorIDList[0].length+j+labelCol] = indName;
    }
  }
  
  //Analyze the resultant data
  var analysisArray = new Array(1);
  var analysisResult = new Array(1);
  for (var i=0; i<indNameArray.length; i++) {
    analysisArray[0] = indNameArray[i];
    for (var j=0; j<fullArray.length; j++) {
      analysisArray[j+1] = fullArray[j][i];
    }
    analysisResult[i] = metricAnalysis(analysisArray);
  }
  
  //Insert analysis results into outputArray
  var resultRow = outputArray.length - 1;
  var resultCol = labelCol;
  for (var i=0; i<analysisResult.length; i++) {
    outputArray[resultRow][i+resultCol] = analysisResult[i];
  }
  
  //Write output array to sheet
  compareSheet.insertRowsBefore(3,outputArray.length);     //insert 11 rows before row 3
  
  var resultRowNum = 3;
  var resultColNum = 1;
  for (var i=0; i<outputArray.length; i++) {
    for (var j=0; j<outputArray[0].length; j++) {
         compareSheet.getRange(i+resultRowNum,j+resultColNum).setValue(outputArray[i][j]);
         //compareSheet.getRange(i+resultRowNum,j+resultColNum).setHorizontalAlignment("left");
    }
  }
  
  //Set formatting on the output range
  compareSheet.getRange(resultRowNum, resultColNum, outputArray.length, outputArray[0].length).setBorder(true, true, true, true, false, false, "black", SpreadsheetApp.BorderStyle.SOLID_THICK);
  compareSheet.getRange(resultRowNum, resultColNum, 1, outputArray[0].length).setBorder(true, true, true, true, false, false, "black", SpreadsheetApp.BorderStyle.SOLID_THICK);
  for (var i=0; i<outputArray[0].length; i++) {
    if (outputArray[outputArray.length - 1][i] == "PASS") {
      compareSheet.getRange(resultRowNum + outputArray.length - 1, resultColNum + i).setBackground("lime");
    } else if (outputArray[outputArray.length - 1][i] == "FAIL") {
      compareSheet.getRange(resultRowNum + outputArray.length - 1, resultColNum + i).setBackground("red");
    }
  }
  
}



function metricAnalysis(metricArray) {
  //metricArray input should have this form: ["metric name", this year value, year-1 value, year-2 value, year-3 value, year-4 value]
  var tally = 0;   //tally to be used to count successful comparisons in the switch-case structure
  var comparisons = metricArray.length - 2;   //total possible comparisons between years in the input array (excludes the name at position 0)
  var result = "";
  
  switch (metricArray[0]) {
      
    case "Revenues":
      for (var i=1; i<metricArray.length-1; i++) {
        if (metricArray[i] > metricArray[i+1]) {
          tally = tally + 1;
        }
      }
      if (tally >= comparisons-1) {
        var result = "PASS";
      } else {
        var result = "FAIL";
      }
      break;
      
    case "Earnings per Share, Basic":
      for (var i=1; i<metricArray.length-1; i++) {
        if (metricArray[i] > metricArray[i+1]) {
          tally = tally + 1;
        }
      }
      if (tally >= comparisons-1) {
        var result = "PASS";
      } else {
        var result = "FAIL";
      }
      break;
        
    case "Return on Equity":
      for (var i=1; i<metricArray.length-1; i++) {
        if (metricArray[i] > metricArray[i+1]) {
          tally = tally + 1;
        }
      }
      if (tally >= comparisons-1) {
        var result = "PASS";
      } else {
        var result = "FAIL";
      }
      break;
        
    case "Net Income (common shareholders)":
      break;
        
    case "Total Assets":
      break;
        
    case "Total Debt":
      break;
        
    case "Total Equity":
      break;
        
    case "Dividends Paid":
      break;
        
    case "Gross Margin":
      break;
        
    case "Operating Margin":
      break;
        
    case "Net Profit Margin":
      break;
        
    case "Debt to Assets Ratio":
      break;
        
    case "Dividends per Share":
      break;
        
    case "Price to Earnings Ratio":
      break;
        
    case "Sector Classification":
      break;
  }
  
  return result;
}



function labelIndicators(indicator) {
  
  indicator = "a" + indicator.replace("-", "")
  
  var label = {
    "a03": {"name": "Number of Employees","description": ""},
    "a05": {"name": "Founding Year","description": ""},
    "a06": {"name": "Headquarter Location","description": ""},
    "a031": {"name": "Last Closing Price","description": ""},
    "a064": {"name": "Common Shares Outstanding","description": ""},
    "a065": {"name": "Preferred Shares Outstanding","description": ""},
    "a066": {"name": "Average Shares Outstanding, basic","description": ""},
    "a067": {"name": "Average Shares Outstanding, diluted","description": ""},
    "a071": {"name": "Ticker","description": ""},
    "a073": {"name": "Sector Classification","description": ""},
    "a11": {"name": "Revenues","description": ""},
    "a12": {"name": "Cost of Goods Sold","description": ""},
    "a14": {"name": "Gross Profit","description": ""},
    "a111": {"name": "Operating Expenses","description": ""},
    "a112": {"name": "Selling, General and Administrative","description": ""},
    "a115": {"name": "Research & Development Expenses","description": ""},
    "a119": {"name": "Operating Income (EBIT)","description": ""},
    "a121": {"name": "Interest Expense, net","description": ""},
    "a128": {"name": "Pretax Income (adjusted)","description": ""},
    "a143": {"name": "Pretax Income","description": ""},
    "a144": {"name": "Income Taxes","description": ""},
    "a149": {"name": "Income from Continuing Operations","description": ""},
    "a158": {"name": "Net Income (common shareholders)","description": ""},
    "a21": {"name": "Cash and Cash-equivalents","description": ""},
    "a25": {"name": "Receivables, net","description": ""},
    "a221": {"name": "Total Current Assets","description": ""},
    "a222": {"name": "Property, Plant and Equipment, net","description": ""},
    "a241": {"name": "Total Assets","description": ""},
    "a243": {"name": "Accounts Payable","description": ""},
    "a247": {"name": "Current Debt","description": ""},
    "a257": {"name": "Total Current Liabilities","description": ""},
    "a258": {"name": "Non-current Debt","description": ""},
    "a273": {"name": "Total Liabilities","description": ""},
    "a274": {"name": "Preferred Equity","description": ""},
    "a276": {"name": "Common Stock","description": ""},
    "a282": {"name": "Equity Before Minorities","description": ""},
    "a283": {"name": "Minority Interest","description": ""},
    "a284": {"name": "Total Equity","description": ""},
    "a32": {"name": "Depreciation & Amortisation","description": ""},
    "a37": {"name": "Change in Working Capital","description": ""},
    "a313": {"name": "Operating Cash Flow","description": ""},
    "a314": {"name": "Net Change in PP&E & Intangibles","description": ""},
    "a331": {"name": "Investing Cash Flow","description": ""},
    "a332": {"name": "Dividends Paid","description": ""},
    "a343": {"name": "Financing Cash Flow","description": ""},
    "a346": {"name": "Net Change in Cash","description": ""},
    "a40": {"name": "Gross Margin","description": ""},
    "a41": {"name": "Operating Margin","description": ""},
    "a42": {"name": "Net Profit Margin","description": ""},
    "a43": {"name": "Current Ratio","description": ""},
    "a44": {"name": "Liabilities to Equity Ratio","description": ""},
    "a45": {"name": "Debt to Assets Ratio","description": ""},
    "a46": {"name": "Total Debt","description": ""},
    "a47": {"name": "Return on Equity","description": ""},
    "a49": {"name": "Return on Assets","description": ""},
    "a410": {"name": "EBITDA","description": ""},
    "a411": {"name": "Market Capitalisation","description": ""},
    "a412": {"name": "Earnings per Share, Basic","description": ""},
    "a413": {"name": "Earnings per Share, Diluted","description": ""},
    "a414": {"name": "Price to Earnings Ratio","description": ""},
    "a415": {"name": "Price to Sales Ratio","description": ""},
    "a416": {"name": "Price to Book Value","description": ""},
    "a417": {"name": "Sales per Share","description": ""},
    "a418": {"name": "Book Value per Share","description": ""},
    "a420": {"name": "Enterprise Value","description": ""},
    "a421": {"name": "EV/EBITDA","description": ""},
    "a422": {"name": "EV/Sales","description": ""},
    "a423": {"name": "Book to Market Value","description": ""},
    "a424": {"name": "Operating Income/EV","description": ""},
    "a425": {"name": "Free Cash Flow","description": ""},
    "a426": {"name": "Free Cash Flow per Share","description": ""},
    "a427": {"name": "Price to Free Cash Flow","description": ""},
    "a428": {"name": "Free Cash Flow to Net Income","description": ""},
    "a429": {"name": "Dividends per Share","description": ""},
    "a430": {"name": "Pietroski F-Score","description": ""},
    "a431": {"name": "EV/FCF","description": ""},
    "a411": {"name": "Market Capitalisation","description": ""}     //this is a duplicate that was shown in the Simfin documentation
  }
  
  if (indicator in label) {
    var name = eval("label." + String(indicator) + ".name");
    var description = eval("label." + String(indicator) + ".name");
  } else {
    var name = "Undefined";
    var description = "Undefined";
  }
  
  return name, description;  
}



function clearComparator() {
  var compSheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("Comparator");
  var totalRows = compSheet.getMaxRows();
  
  if (totalRows > 3) {
    compSheet.deleteRows(3, totalRows-3);    //subtract 3 rows for the title bar and the blank end row
  }

  var dummyRow = compSheet.getRange("A3:3");
  dummyRow.clearContent();

}




function ADD_SIMFIN() {
  var ui = SpreadsheetApp.getUi();
  ui.createMenu('SimFin API')
      .addItem('Load data','callApi')
      .addToUi();
}
