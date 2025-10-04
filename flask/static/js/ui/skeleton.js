// skeleton loading utilities + tooltip positioning

// helper function to remove skeleton styling with optional border
function removeBorderSkeleton(element, borderColor, showBorder) {
    if (showBorder === true) {
        element.style.border = borderColor;
        element.style.background = window.getComputedStyle(document.body).getPropertyValue("--card-background-color");
        element.style.animation = "none";
        element.style.backgroundSize = "none";
    } else {
        element.style.animation = "none";
        element.style.backgroundSize = "none";
    }
}

// helper function to remove background skeleton styling
function removeBackgroundSkeleton(element) {
    element.style.background = "none";
    element.style.animation = "none";
    element.style.backgroundSize = "none";
}

// enable review chart skeleton
export function enableReviewSkeleton() {
    var reviewChart = document.getElementsByClassName("chart-skeleton")[1];
    reviewChart.style.border = "";
    reviewChart.style.background = "";
    reviewChart.style.animation = "";
    reviewChart.style.backgroundSize = "";
    reviewChart.style.boxShadow = "";
}

// remove skeleton loading for review chart specifically
export function removeReviewSkeleton() {
    let cardBorderColor = "2px " + window.getComputedStyle(document.body).getPropertyValue("--card-border-color") + " solid";
    var reviewChart = document.getElementsByClassName("chart-skeleton")[1];
    removeBorderSkeleton(reviewChart, cardBorderColor, true);
    reviewChart.style["box-shadow"] = "0px 0px 10px 0.1px black";

    // text - make text appear
    var hiddenText = document.querySelectorAll(".review-card-header-text,.steam-review-header,.review-callout-info");
    for (let i = 0; i < hiddenText.length; i++) { 
        hiddenText[i].style.visibility = "visible"; 
    }

    // headers
    var header = document.getElementsByClassName("steam-review-header")[0];
    removeBorderSkeleton(header, "", false);

    // make card background normal + show border
    var card = document.getElementsByClassName("review-card");
    for (let i = 0; i < card.length; i++) { 
        removeBorderSkeleton(card[i], cardBorderColor, true); 
    }
}

// temove skeleton loading for everything + player count chart
export function removePlayerCountSkeleton() {
    let cardBorderColor = "2px " + window.getComputedStyle(document.body).getPropertyValue("--card-border-color") + " solid";

    // text - make text appear
    var hiddenText = document.querySelectorAll(".card-header-text,.playercount-header,.navbar-text,.title-div,.player-forecast-info,.forecast-disabled-warning,.forecast-line");
    for (let i = 0; i < hiddenText.length; i++) { 
        hiddenText[i].style.visibility = "visible"; 
    }

    // headers
    var header = document.getElementsByClassName("playercount-header")[0];
    removeBorderSkeleton(header, "", false);

    // make card background normal + show border
    var card = document.querySelectorAll(".card,.forecast-card");
    for (let i = 0; i < card.length; i++) { 
        removeBorderSkeleton(card[i], cardBorderColor, true); 
    }

    // make chart background normal + show border
    var playerChart = document.getElementsByClassName("chart-skeleton")[0];
    removeBorderSkeleton(playerChart, cardBorderColor, true);
    playerChart.style["box-shadow"] = "0px 0px 10px 0.1px black";

    // navbar
    var navbar = document.getElementsByClassName("navbar-text");
    for (let i = 0; i < navbar.length; i++) { 
        removeBorderSkeleton(navbar[i], "none", false); 
    }

    // remove wrapper backgrounds
    navbar = document.querySelectorAll(".navbar-text-wrapper,.title-div-wrapper");
    for (let i = 0; i < navbar.length; i++) { 
        removeBackgroundSkeleton(navbar[i]); 
    }
}

// position tooltip elements correctly
export function positionTooltips() {
    // put above hover area
    var tooltip = document.getElementsByClassName("tooltip-text");
    let vw = Math.max(document.documentElement.clientWidth || 0, window.innerWidth || 0);
    if (vw >= 1100) {
        for (let i = 0; i < tooltip.length; i++) {
            var width = tooltip[i].clientWidth;
            // remove icon from both edges, get center offset, then adjust 12 px b/c left of icon is currently at center due to inline-inset-start: 0 being directly lined up w/ left side of box
            // then add 8 for icon 8 units to right
            tooltip[i].style["inset-inline-start"] = (-1 * (width - 48) / 2 - 12 + 8).toString() + "px"; 
        }
    }
    else {
        for (let i = 0; i < tooltip.length; i++) {
            var width = tooltip[i].clientWidth;
            tooltip[i].style["inset-inline-start"] = "-80px"; 
            tooltip[i].style["font-size"] = " calc(0.4rem + 0.831vw)";
        }
    }
}