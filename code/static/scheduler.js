var fileForm;
var times = []; // this list will be populated with the times the clocks should ring, read from the uploaded file
var vacationMode = false;

// called when the page loads; adds an event listener to the form
function init() {
    fileForm = document.getElementById('fileForm');

    // fileForm.addEventListener('submit', function(event) {
    //     // TODO: rn the page refreshes on form submit so you dont actually see any of this stuff
    //     // lowk I should prolly just redirect to a new html file but whateva thats a future me deal
    //     // screw you future me
        
    //     //event.preventDefault(); // stops the page from reloading
    //     let logo = document.getElementById('logo');
    //     logo.classList.add('logo');
    //     readFile();
    // });
}

// opens a new FileReader object to read the uploaded file
function readFile() {
    file = document.getElementById('timingFile').files[0];
    let fr = new FileReader();
    fileForm.reset();

    fr.onload = function() {
        console.log(fr.result);
        // parse text file
        times = fr.result.split("\n");
        displayTxtFile();
    }
    fr.readAsText(file);
}

// outputs the uploaded file to the page
function displayTxtFile() {
    let output = document.getElementById('output');
    output.hidden = false;
    let timesHtml = "";
    for (let i = 0; i < times.length; i++) {
        timesHtml += "<li><input type=\"text\" class=\"text-input\" value=\"" 
        + times[i] 
        + "\"></li>\n";
    }
    output.innerHTML += "<form><ul>\n" + timesHtml + "</ul>" 
    + "<input type=\"submit\" class=\"btn\" value=\"Save Changes\"></form>";
}

// toggles a visual indicator of "vacation mode"
function toggleVacationMode() {
    let timesTxt = document.getElementsByClassName('text-input');
    let vacayCheckBox = document.getElementById('vacayCheckBox');

    if (vacationMode){
        vacationMode = false;
        for (let i = 0; i < timesTxt.length; i++) {
            timesTxt[i].classList.remove('disabled');
        }
    }
    else if (!vacationMode){
        vacationMode = true;
        for (let i = 0; i < timesTxt.length; i++) {
            timesTxt[i].classList.add('disabled');
        }
    }
    
    vacayCheckBox.checked = vacationMode;
}