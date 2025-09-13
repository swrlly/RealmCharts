var backgroundColor = "#141414";
var seriesColor = "#517affff";
var selectorColor = "#4d4d4dff";
var linesInChartColor = "#969696";
var yAxisLineColor = "#5e5e5e";
var inputBoxBorderColor = "#6e6e6e";
var axisLabelColor = "#bdbdbd";
var zoomLabelColor = "#969696";
var disabledZoomLabelColor = "#252526";
var chartFont = "Open Sans";

/*
const req = new XMLHttpRequest();
req.open("GET",'/api/playercount', true);
req.setRequestHeader("Access-Control-Allow-Origin", "same-origin")
req.send();*/

async function getData(link) {
    return await fetch(link).then(response => response.json());
}

async function createChart() {

    //var data = await getData("http://localhost:8001/api/playercount");
    var data = await getData("https://rotmg.swrlly.com/api/playercount");

    for (index = 0; index < data.length; index++) {
        data[index][0] *= 1000;
        data[index][1] = data[index][1] === 0 ? null : data[index][1]
    }
        
    Highcharts.setOptions({
        chart : {
            backgroundColor: backgroundColor,
            style: {
                fontFamily: chartFont,
                color: linesInChartColor,
                fontSize: "1rem"
            }
        }
    });
    Highcharts.seriesTypes.scatter.prototype.getPointSpline = Highcharts.seriesTypes.spline.prototype.getPointSpline;
    var chart = Highcharts.stockChart("playercount-chart", {
        chart : {
            reflow: true,
            events : {
                async load() {
                    removeSkeleton();
                } 
            }
        },
        navigator: {
            // slider opacity + color
            maskFill : "rgba(102,133,194,0.08)",
            xAxis: {
                labels: {
                    style : {
                        color: linesInChartColor
                    }
                }
            }
        },

        scrollbar: {
            height: 0
        },
        exporting : {
            buttons : {
                contextButton : {
                    enabled : false
                }
            }
        },
        title: {
            enabled: false
        },
        rangeSelector: {
            enabled: true,
            buttons: [
                {
                    type: 'day',
                    count: 1,
                    text: '24h'
                }, {
                    type: 'week',
                    count: 1,
                    text: '7d'
                }, {
                    type: 'month',
                    count: 1,
                    text: '1m'
                }, {
                    type: 'year',
                    count: 1,
                    text: '1y'
                }, {
                    type: 'all',
                    text: 'All'
                },
            ],
            buttonTheme : {
                fill: "none",
                states: {
                    hover: {}, select: {},
                    disabled: {
                        color: disabledZoomLabelColor
                    }
                },
                style: {
                    color: zoomLabelColor
                },
            },
            inputEnabled: true,
            inputStyle: {
                backgroundColor: backgroundColor,
                color: linesInChartColor,
                border: "none"
            },
            labelStyle: {
                color: zoomLabelColor
            },
            inputBoxBorderColor: backgroundColor
        },
        series: [{
            name: 'Players',
            data: data,
            lineWidth: 2,
            color: seriesColor,
            tooltip: {
                /*backgroundColor: 'rgba(255, 255, 255, 1)',*/
                hideDelay: 0,
                style: {
                    color: '#000000',
                    fontSize: '14px',
                },
                pointFormatter: function() {
                    return `${Highcharts.dateFormat('%A, %b %d, %H:%M UTC', this.x)}<br/>`
                        + `<span style="color:${this.color}">\u25CF</span> ${this.series.name}:`
                        + ` <b>${this.y.toLocaleString()}</b><br/>`;
                },
                valueDecimals: 0,
            },
            showInLegend: true
        }],
        xAxis: {
            lineColor: linesInChartColor,
            tickColor: linesInChartColor,
            gridLineWidth:0,
            type: 'datetime',
            labels: {
                style : {
                    color: axisLabelColor
                }
            },
            ordinal: false,
            crosshair: {
                dashStyle: 'ShortDash',
                color: selectorColor,
            },
            tickPixelInterval: 120,
            min: Date.now() - (168 * 60 * 60 * 1000),
            max: Date.now()

        },
        yAxis: {
            gridLineColor: yAxisLineColor,
            labels: {
                style: {
                    color: axisLabelColor
                }
            }
        },
        
    });

    /*document.getElementById("playercount-chart").addEventListener("resize", function() {
        chart.reflow();
    });*/
    
    return [chart, data];
    /*
    setInterval(() => {
    console.log('Chart size:', chart.chartWidth, 'x', chart.chartHeight);
    console.log('Container size:', chart.container.offsetWidth, 'x', chart.container.offsetHeight);
    }, 1000);
    */
   
    /*setInterval(function() {
        var point = [
            Date.now(), // current timestamp
            Math.random() * 100 // replace with your actual data value
        ];
        
        chart.series[0].addPoint(point, true, true);
    }, 5000);*/

}

function removeBorderSkeleton(s, c, b) {

    if (b === true) {
        s.style.border = c;
        s.style.background = window.getComputedStyle(document.body).getPropertyValue("--card-background-color");
        s.style.animation = "none";
        s.style.backgroundSize = "none";
    }
    else {
        s.style.animation = "none";
        s.style.backgroundSize = "none";
    }
}

function removeBackgroundSkeleton(s) {
    s.style.background = "none";
    s.style.animation = "none";
    s.style.backgroundSize = "none";
}

function removeSkeleton() {

    let cardBorderColor = "2px " + window.getComputedStyle(document.body).getPropertyValue("--card-border-color") + " solid";

    // text
    // make text appear
    var hiddenText = document.querySelectorAll(".card-header-text,.playercount-header,.navbar-text,.title-div");
    console.log(hiddenText);
    for (let i = 0; i < hiddenText.length; i++) { hiddenText[i].style.visibility = "visible"; }

    // headers
    var header = document.getElementsByClassName("playercount-header")[0];
    removeBorderSkeleton(header, "", false);

    // make card background normal + show border
    var card = document.getElementsByClassName("card");
    for (let i = 0; i < card.length; i++) { removeBorderSkeleton(card[i], cardBorderColor, true); }

    // make chart background normal + show border
    var playerChart = document.getElementsByClassName("chart-skeleton")[0];
    removeBorderSkeleton(playerChart, cardBorderColor, true);
    playerChart.style["box-shadow"] = "0px 0px 10px 0.1px black";

    //navbar
    var navbar = document.getElementsByClassName("navbar-text");
    console.log(navbar);
    for (let i = 0; i < navbar.length; i++) { removeBorderSkeleton(navbar[i], "none", false); }

    // now remove wrapper backgrounds
    navbar = document.querySelectorAll(".navbar-text-wrapper,.title-div-wrapper");
    for (let i = 0; i < navbar.length; i++) { removeBackgroundSkeleton(navbar[i]); }

}

function positionTooltips() {
    // put above hover area
    var tooltip = document.getElementsByClassName("tooltip-text")[0];
    var width = tooltip.clientWidth;
    // remove icon from both edges, get center offset, then adjust 12 px b/c left of icon is currently at center due to inline-inset-start: 0 being directly lined up w/ left side of box
    // then add 8 for icon 8 units to right
    tooltip.style["inset-inline-start"] = (-1 * (width - 48) / 2 - 12 + 8).toString() + "px"; 
}

function tsToSeconds(time) {
    let seconds = Math.floor((Date.now() - time) / 1000);
    let minutes = Math.floor(seconds / 60);
    let hours = Math.floor(seconds / 3600);
    let days = Math.floor(seconds / (3600 * 24));
    let s = "";
    if (days > 0) {
        s = days == 1 ? days + " day" : days + " days";
    } else if (hours > 0) {
        s = hours == 1 ? hours + " hour" : hours + " hours";
    } else if (minutes > 0) {
        s = minutes == 1 ? minutes + " minute" : minutes + " minutes";
    } else if (seconds > 0) {
        s = seconds == 1 ? seconds + " second" : seconds + " seconds";
    }
    return s;
}

async function getGameOnline(time) {
    var data = await getData("https://rotmg.swrlly.com/api/online");
    return data;
}

async function updateCards(data) {
    let content = document.getElementById("players-online");
    content.innerHTML = data[data.length - 1][1];

    content = document.getElementById("server-status");
    var serverStatus = await getGameOnline();
    if (serverStatus["online"] === 1){
        content.innerHTML = '<img class="server-up-emoji" style="animation: growFromCenter 0.4s ease-out forwards;" src="/static/images/pogfish.png"></img>';
    }
    else {
        console.log(serverStatus["online"])
        content.innerHTML = '<img class="server-up-emoji" style="animation: growFromCenter 0.4s ease-out forwards;" src="/static/images/shinyglape.png"></img>';
    }
    
    setTimeout(() => {document.getElementsByClassName("server-up-emoji")[0].style.removeProperty("animation");}, 400);

}

async function main() {
    let [chart, data] = await createChart();
    positionTooltips();
    await updateCards(data);
}

main();






//updateTimeUpdated(data[data.length -1][0]);
//setInterval(updateTimeUpdated, 1000, data[data.length - 1][0]);

/*
function updateTimeUpdated(time) {
    let seconds = Math.floor((Date.now() - time) / 1000);
    let minutes = Math.floor(seconds / 60);
    let hours = Math.floor(seconds / 3600);
    let days = Math.floor(seconds / (3600 * 24));
    let s = "";
    if (days > 0) {
        s = days == 1 ? days + " day" : days + " days";
    } else if (hours > 0) {
        s = hours == 1 ? hours + " hour" : hours + " hours";
    } else if (minutes > 0) {
        s = minutes == 1 ? minutes + " minute" : minutes + " minutes";
    } else if (seconds > 0) {
        s = seconds == 1 ? seconds + " second" : seconds + " seconds";
    }
    let content = document.getElementById("time-updated");
    content.innerHTML = "Updated " + s + " ago";
}*/