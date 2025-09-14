var backgroundColor = "#141414";

var seriesColor = "#517affff";
var columnColor = "#7b7b7b80";
var reviewColor = "#47bfff80";
var linesInChartColor = "#969696";
var yAxisLineColor = "#5e5e5e";
var inputBoxBorderColor = "#6e6e6e";
var axisLabelColor = "#adadadff";
var zoomLabelColor = "#c9c9c9";
var rangeSelectorColorDisabled = "rgba(16, 16, 16, 1)";
var rangeSelectorColor = "#1c1c1cff";
var rangeSelectorEnabled = "#343434ff";
var rangeSelectorHover = "#343434ff";
var textColor = "#c9c9c9";
var disabledTextColor = "#4a4a4aff";
var chartFont = "Open Sans";
//var playerCountLink = "http://localhost:8001/api/playercount";
//var reviewsLink = "http://localhost:8001/api/review-proportions";
//var latestPlayerCountLink = "http://localhost:8001/api/players-now";
//var serverUpLink = "http://localhost:8001/api/is-game-online";
var playerCountLink = "https://realmcharts.swrlly.com/api/playercount";
var reviewsLink = "https://realmcharts.swrlly.com/api/review-proportions"
var latestPlayerCountLink = "https://realmcharts.swrlly.com/api/players-now";
var serverUpLink = "https://realmcharts.swrlly.com/api/is-game-online";

/*
const req = new XMLHttpRequest();
req.open("GET",'/api/playercount', true);
req.setRequestHeader("Access-Control-Allow-Origin", "same-origin")
req.send();*/

async function getData(link) {
    return await fetch(link).then(response => response.json());
}

async function playercountChart() {

    var data = await getData(playerCountLink);

    for (index = 0; index < data.length; index++) {
        data[index][0] *= 1000;
        data[index][1] = data[index][1] === 0 ? null : data[index][1];
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
                    text: '1m',
                    enabled: false,
                }, {
                    type: 'year',
                    count: 1,
                    text: '1y',
                    enabled: false,
                }, {
                    type: 'all',
                    text: 'All'
                },
            ],
            buttonTheme : {
                fill: rangeSelectorColor,
                states: {
                    hover: {
                        fill: rangeSelectorHover,
                        style: {
                            color: textColor
                        }
                    }, 
                    select: {
                        fill: rangeSelectorEnabled,
                    },
                    disabled: {
                        fill: rangeSelectorColorDisabled,
                        style: {
                            color: disabledTextColor
                        }
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
            lineWidth: 3,
            color: seriesColor,
            tooltip: {
                backgroundColor: backgroundColor,
                hideDelay: 0,
                style: {
                    color: textColor,
                },
                
                pointFormatter: function() {
                    return `<span style="color:${this.color}">\u25CF</span> ${this.series.name}:`
                        + ` <b>${this.y.toFixed(2)}</b><br/>`;
                },
                /*valueDecimals: 0,*/
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
                //color: selectorColor,
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
        tooltip: {
            shared: true,
            backgroundColor: backgroundColor,
            hideDelay: 0,
            style: {
                color: textColor,
            }
        }
        
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

async function reviewChart() {

    //var data = await getData("http://localhost:8001/api/playercount");
    var data = await getData(reviewsLink);
    let reviews = data.slice(0, data.length - 1).map(i => i.slice(0, 2));
    let proportions = data.slice(0, data.length - 1).map(i => [i[0], i[2] * 100]);

    //for (index = 0; index < data.length; index++) {
    //    data[index][1] = data[index][1] === 0 ? null : data[index][1]
    //}
    /*
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
    */
    var chart = Highcharts.stockChart("review-chart", {
        chart : {
            reflow: true,
            events : {
                async load() {
                    removeReviewSkeleton();
                } 
            }
        },
        /*title: {
            text: "% of positive reviews, all time",
            align: "left"
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
        },*/
        navigator: {
            enabled: false
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
                fill: rangeSelectorColor,
                states: {
                    hover: {
                        fill: rangeSelectorHover,
                        style: {
                            color: textColor
                        }
                    }, 
                    select: {
                        fill: rangeSelectorEnabled,
                    },
                    disabled: {
                        fill: rangeSelectorColorDisabled,
                        style: {
                            color: disabledTextColor
                        }
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
                border: {
                    style: {
                        color: backgroundColor
                    }
                }
            },
            labelStyle: {
                color: zoomLabelColor
            },
            inputBoxBorderColor: backgroundColor
        },
        yAxis: [{
            gridLineColor: yAxisLineColor,
            labels: {
                style: {
                    color: axisLabelColor
                },
                format: "{value}%"
            },

            title: {
                text: "% positive reviews"
            },
            opposite: false
        }, {
            gridLineColor: yAxisLineColor,
            labels: {
                style: {
                    color: axisLabelColor
                },
                format: "{value}"
            },
            title: {
                text: "Number of reviews"
            },
            opposite: true
        }],
        series: [{
            name: "Positive reviews",
            type: "spline",
            yAxis: 0,
            lineWidth: 3,
            data: proportions,
            color: seriesColor,/*{
                linearGradient: { x1: 0, x2: 0, y1: 0, y2: 3 },
                stops: [
                    [0, "#3fe533ff"],
                    [1, "#e53333ff"]
                ]
            },*/

            tooltip: {
                valueSuffix: "%",
                pointFormatter: function() {
                    return `<span style="color:${this.color}">\u25CF</span> ${this.series.name}:`
                        + ` <b>${this.y.toFixed(2)}%</b><br/>`;
                },
                backgroundColor: backgroundColor,
                hideDelay: 0,
                style: {
                    color: textColor,
                }
            }
        }, {
            name: "Number of reviews",
            type: "column",
            yAxis: 1,
            data: reviews,
            color: {
                linearGradient: { x1: 0, x2: 0, y1: 0, y2: 1 },
                stops: [
                    [0, "#896eff66"],
                    [1, "#aaaaaa5f"]
                ]
            },
            tooltip: {
                backgroundColor: backgroundColor,
                hideDelay: 0,
                style: {
                    color: textColor,
                }
            }
        }],
        xAxis: {
            lineColor: linesInChartColor,
            tickColor: linesInChartColor,
            gridLineWidth: 0,
            /*type: 'datetime',*/
            labels: {
                style : {
                    color: axisLabelColor
                }
            },
            ordinal: false,
            crosshair: {
                dashStyle: 'ShortDash',
                /*color: "black",*/
            },
            tickPixelInterval: 120,
        },
        legend: {
            align: 'left',
            verticalAlign: 'top'
        },
        tooltip: {
            shared: true,
            backgroundColor: backgroundColor,
            hideDelay: 0,
            style: {
                color: textColor,
            }
        },
    });

    return [chart, data];
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

function removeReviewSkeleton() {
    let cardBorderColor = "2px " + window.getComputedStyle(document.body).getPropertyValue("--card-border-color") + " solid";
    var reviewChart = document.getElementsByClassName("chart-skeleton")[1];
    removeBorderSkeleton(reviewChart, cardBorderColor, true);
    reviewChart.style["box-shadow"] = "0px 0px 10px 0.1px black";
}

function removeSkeleton() {

    let cardBorderColor = "2px " + window.getComputedStyle(document.body).getPropertyValue("--card-border-color") + " solid";

    // text
    // make text appear
    var hiddenText = document.querySelectorAll(".card-header-text,.playercount-header,.navbar-text,.title-div");
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

function updatePlayerCountTimeUpdated(data) {

    const txt = tsToSeconds(data[data.length - 1][0]);
    let content = document.getElementById("players-last-updated");
    content.innerHTML = "Updated " + txt + " ago";

}

function tsToSeconds(time) {
    let seconds = Math.floor((Date.now() - time) / 1000);
    let minutes = Math.floor(seconds / 60);
    let hours = Math.floor(seconds / 3600);
    let days = Math.floor(seconds / (3600 * 24));
    let txt = "";
    if (days > 0) {
        txt = days == 1 ? days + " day" : days + " days";
    } else if (hours > 0) {
        txt = hours == 1 ? hours + " hour" : hours + " hours";
    } else if (minutes > 0) {
        txt = minutes == 1 ? minutes + " minute" : minutes + " minutes";
    } else if (seconds > 0) {
        txt = seconds == 1 ? seconds + " second" : seconds + " seconds";
    }
    return txt;
}

async function updateCards(data) {
    // update players now
    let content = document.getElementById("players-online");
    let num = data[data.length - 1][1];
    if (isFinite(num) && !isNaN(num)) {

        if (num >= 1000) {
            let remainder = num % 1000;
            let thousands_digit = (num - remainder) / 1000;
            content.innerHTML = thousands_digit.toString() + "," + remainder.toString();
        }
        else {
            content.innerHTML = num;
        }
    }
    else {
        content.innerHTML = "-"
    }
    
    // update weekly % chnage
    content = document.getElementById("players-weekly-change");
    let percent = parseFloat(((data[data.length-1][1] / data[data.length - 1 - 10080][1]) * 100  - 100).toFixed(2));
    // toFixed converts to string
    if (isFinite(percent) && !isNaN(percent) && percent !== -100) {
        if (percent > 0) {
            content.innerHTML = percent.toString() + "% " + '<svg width="24px" height="24px" fill="#2dc83cff" viewBox="0 0 24.00 24.00" fill="none" stroke="" stroke-width="0.00024000000000000003"><path fill-rule="evenodd" clip-rule="evenodd" d="M7.00003 15.5C6.59557 15.5 6.23093 15.2564 6.07615 14.8827C5.92137 14.509 6.00692 14.0789 6.29292 13.7929L11.2929 8.79289C11.6834 8.40237 12.3166 8.40237 12.7071 8.79289L17.7071 13.7929C17.9931 14.0789 18.0787 14.509 17.9239 14.8827C17.7691 15.2564 17.4045 15.5 17 15.5H7.00003Z"></path></svg>';
        }
        else if (percent === 0) {
            content.innerHTML = percent.toString() + "% " + '<svg class="percent-change-icon" width="16px" height="24px" fill="#907128ff" viewBox="0 0 459.313 459.314" stroke-width="0.00459313"><path d="M459.313,229.648c0,22.201-17.992,40.199-40.205,40.199H40.181c-11.094,0-21.14-4.498-28.416-11.774 C4.495,250.808,0,240.76,0,229.66c-0.006-22.204,17.992-40.199,40.202-40.193h378.936 C441.333,189.472,459.308,207.456,459.313,229.648z"></path> </svg>';
        }
        else {
            content.innerHTML = percent.toString() + "% " + '<svg width="24px" height="24px" fill="#a02121ff" viewBox="0 0 24.00 24.00" fill="none" stroke="" stroke-width="0.00024000000000000003"><path fill-rule="evenodd" clip-rule="evenodd" d="M7.00003 8.5C6.59557 8.5 6.23093 8.74364 6.07615 9.11732C5.92137 9.49099 6.00692 9.92111 6.29292 10.2071L11.2929 15.2071C11.6834 15.5976 12.3166 15.5976 12.7071 15.2071L17.7071 10.2071C17.9931 9.92111 18.0787 9.49099 17.9239 9.11732C17.7691 8.74364 17.4045 8.5 17 8.5H7.00003Z"></path></svg>';
        }
    }
    else {
        content.innerHTML = "-";
    }

    // update server online status
    content = document.getElementById("server-status");
    var serverStatus = await getData(serverUpLink);
    if (serverStatus["online"] === 1){
        content.innerHTML = '<img class="server-up-emoji" style="animation: growFromCenter 0.4s ease-out forwards;" src="/static/images/pogfish.png"></img>';
    }
    else {
        content.innerHTML = '<img class="server-up-emoji" style="animation: growFromCenter 0.4s ease-out forwards;" src="/static/images/shinyglape.png"></img>';
    }
    
    setTimeout(() => {document.getElementsByClassName("server-up-emoji")[0].style.removeProperty("animation");}, 400);

    content = document.getElementById("not-sure-yet");
    content.innerHTML = '<img class="not-sure-yet" style="animation: growFromCenter 0.4s ease-out forwards;" src="/static/images/glape.png"></img>';
    setTimeout(() => {document.getElementsByClassName("not-sure-yet")[0].style.removeProperty("animation");}, 400);

}

async function updateCardsJob(chart, data) {
    // function to update cards every minute
    var newData = await getData(latestPlayerCountLink);
    newData[0] *= 1000;
    data.push(newData);
    chart.series[0].addPoint(newData);
    await updateCards(data);
    return Promise.resolve([chart, data]);
}

async function main() {
    let [chart, data] = await playercountChart();
    updatePlayerCountTimeUpdated(data);
    positionTooltips();
    await updateCards(data);
    let [review_chart, review_data] = await reviewChart();
    setInterval(updatePlayerCountTimeUpdated, 5000, data);
    // begin live update logic
    const now = new Date();
    const msUntilFirstUpdate = Math.max(60000 - (now - data[data.length - 1][0]), 0);
    console.log("waiting", msUntilFirstUpdate / 1000, "seconds");
    const firstJobId = setTimeout(() => {
        updateCardsJob(chart, data).then(result => {
            [chart, data] = result;
            //console.log("first update", data[data.length - 1])
            const intervalJobId = setInterval(() => {
                updateCardsJob(chart, data).then(result => {
                    [chart, data] = result;
                    //console.log("reg update", data[data.length - 1]);
                });
            }, 60000);
        });
    }, msUntilFirstUpdate);
}

main();


//updateTimeUpdated(data[data.length -1][0]);


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
