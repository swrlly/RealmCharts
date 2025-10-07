import { COLORS, API_ENDPOINTS, RANGE_SELECTOR_THEME } from "../config/constants.js";
import { getData } from "../automation/dataService.js";
import { removeReviewSkeleton } from "../ui/skeleton.js";

function minutesToHumanTime(minutes) {
    let minutesDisplay = minutes % 60;
    let hours = Math.floor(minutes / 60) % 24;
    if (minutes < 60) {
        return minutes += "m";
    }
    hours += minutesDisplay >= 30 ? 1 : 0; // round hour by minutes, too noisy
    let days = Math.floor(minutes / (60 * 24));
    let txt = "";
    if (days > 0) {
        txt += days + "d ";
    } 
    if (hours > 0) {
        txt += hours + "h ";
    } 
    if (minutes == 0) {
        txt = "0m";
    }
    return txt;
}

export async function createReviewsChart() {
    var data = await getData(API_ENDPOINTS.reviews);
    const tsToReviewProp = new Map();

    // convert timestamps to milliseconds
    for (let index = 0; index < data.length; index++) {
        data[index][0] *= 1000;
        data[index][2] *= 100;
        var date = new Date(data[index][0]);
        tsToReviewProp.set(date.getUTCFullYear() + "-" + String(date.getUTCMonth() + 1).padStart(2, "0") + "-" +  String(date.getUTCDate()).padStart(2, "0"), data[index][2]);
    }
    
    let reviews = data.slice(0, data.length).map(i => [i[0], i[1]]);
    let proportions = data.slice(0, data.length).map(i => [i[0], i[2]]);
    
    var chart = Highcharts.stockChart("review-chart", {
        chart: {
            reflow: true,
            events: {
                async load() {
                    removeReviewSkeleton();
                } 
            }
        },
        time: {
            timezone: "utc"
        },
        navigator: {
            enabled: true,
            maskFill: "rgba(133, 133, 133, 0.08)",
            xAxis: {
                labels: {
                    style: {
                        color: COLORS.linesInChartColor
                    }
                }
            }
        },
        scrollbar: {
            height: 0
        },
        exporting: {
            buttons: {
                contextButton: {
                    enabled: false
                }
            }
        },
        rangeSelector: {
            enabled: true,
            buttons: [
                {
                    type: "day",
                    count: 6,
                    text: "7d"
                }, {
                    type: "day",
                    count: 30,
                    text: "1m"
                }, {
                    type: "year",
                    count: 1,
                    text: "1y"
                }, {
                    type: "all",
                    text: "All"
                }
            ],
            buttonTheme: RANGE_SELECTOR_THEME,
            inputEnabled: true,
            inputStyle: {
                backgroundColor: COLORS.backgroundColor,
                color: COLORS.linesInChartColor,
                border: {
                    style: {
                        color: COLORS.backgroundColor
                    }
                }
            },
            labelStyle: {
                color: COLORS.zoomLabelColor
            },
            inputBoxBorderColor: COLORS.backgroundColor
        },
        yAxis: [{
            // left axis - percentage
            gridLineColor: COLORS.yAxisLineColor,
            labels: {
                align: "left",
                x: 1,
                style: {
                    color: COLORS.axisLabelColor,
                    fontSize: "0.6rem"
                },
                format: "{value}%"
            },
            title: {
                text: "% total positive reviews"
            },
            opposite: false
        }, {
            // right axis - review count
            gridLineColor: COLORS.yAxisLineColor,
            labels: {
                align: "right",
                x: -1,
                style: {
                    color: COLORS.axisLabelColor,
                    fontSize: "0.6rem"
                },
                format: "{value}"
            },
            title: {
                text: "# reviews"
            },
            opposite: true
        }],
        series: [{
            name: "Total positive",
            type: "spline",
            yAxis: 0, // left axis
            lineWidth: 3,
            data: proportions,
            color: COLORS.seriesColor,
            tooltip: {
                valueSuffix: "%",
                pointFormatter: function() {
                    return `<span style="color:${this.color}">\u25CF</span> ${this.series.name}:`
                        + ` <b>${this.y.toFixed(3)}%</b><br/>`;
                },
                backgroundColor: COLORS.backgroundColor,
                hideDelay: 0,
                style: {
                    color: COLORS.textColor,
                }
            }
        }, {
            name: "Number of reviews",
            type: "column",
            yAxis: 1, // right axis
            data: reviews,
            color: {
                linearGradient: { x1: 0, x2: 0, y1: 0, y2: 1 },
                stops: [
                    [0, "#896eff66"],
                    [1, "#aaaaaa5f"]
                ]
            },
            tooltip: {
                backgroundColor: COLORS.backgroundColor,
                hideDelay: 0,
                style: {
                    color: COLORS.textColor,
                }
            }
        }],
        xAxis: {
            lineColor: COLORS.linesInChartColor,
            tickColor: COLORS.linesInChartColor,
            gridLineWidth: 0,
            labels: {
                style: {
                    color: COLORS.axisLabelColor
                }
            },
            ordinal: false,
            crosshair: {
                dashStyle: "ShortDash"
            },
            tickPixelInterval: 120,
            events: {

                afterSetExtremes: function(event) {
                    var start = Math.ceil(event.min);
                    var end = Math.floor(event.max);
                    let ctr = 0
                    let num_reviews = 0;
                    let tot_playtime_two_weeks = 0;
                    let tot_positive = 0;
                    let tot_playtime_at_review = 0;
                    let tot_playtime = 0;
                    for (let index = 0; index < data.length; index++) {
                        if (start <= data[index][0] & data[index][0] <= end) {
                            num_reviews += data[index][1];
                            tot_playtime_two_weeks += data[index][3];
                            tot_positive += data[index][4];
                            tot_playtime_at_review += data[index][5];
                            tot_playtime += data[index][6];
                            ctr += 1;
                        }
                    }
                    tot_playtime_two_weeks = Math.round(tot_playtime_two_weeks / num_reviews);
                    tot_positive = ((tot_positive / num_reviews) * 100).toFixed(2);
                    tot_playtime_at_review = Math.round(tot_playtime_at_review / num_reviews);
                    tot_playtime = Math.round(tot_playtime / num_reviews);
                    let content = document.getElementById("percent-positive-reviews");
                    content.style.backgroundPosition =  `${100 - parseFloat(tot_positive)}% 0`;
                    content.innerHTML = tot_positive + "%";
                    content = document.getElementById("avg-playtime-at-review");
                    content.innerHTML = minutesToHumanTime(tot_playtime_at_review);
                    content = document.getElementById("avg-playtime-last-two-weeks");
                    content.innerHTML = minutesToHumanTime(tot_playtime_two_weeks);
                    content = document.getElementById("avg-total-playtime");
                    content.innerHTML = minutesToHumanTime(tot_playtime);
                }
            }
        },/*
        legend: {
            align: "left",
            verticalAlign: "top"
        },*/
        tooltip: {
            shared: true,
            backgroundColor: COLORS.backgroundColor,
            hideDelay: 0,
            style: {
                color: COLORS.textColor,
            },
            followTouchMove: false
        },
        annotations: [
            {
                draggable: "",
                labelOptions: {
                    //shape: 'connector',
                    backgroundColor: COLORS.annotationBackgroundColor,
                    borderColor: COLORS.annotationLineColor,
                    borderWidth: 1
                },
                labels: [
                    {
                        allowOverlap: true,
                        point: {
                            xAxis: 0,
                            yAxis: 0,
                            x: "2012-06-18",
                            y: tsToReviewProp.get("2012-06-18")
                        },
                        x: 0,
                        y: 10,
                        text: "Kabam takeover of Wildshadow"
                    }, {
                        allowOverlap: true,
                        point: {
                            xAxis: 0,
                            yAxis: 0,
                            x: "2013-12-12",
                            y: tsToReviewProp.get("2013-12-12")
                        },
                        x: -50,
                        y: 50,
                        useHTML: true,
                        text: "<img src='/static/images/shatters.png' class='review-image-annotation'></img>"
                    }, {
                        allowOverlap: true,
                        point: {
                            xAxis: 0,
                            yAxis: 0,
                            x: "2014-04-18",
                            y: tsToReviewProp.get("2014-04-18")
                        },
                        x: 50,
                        y: 0,
                        useHTML: true,
                        text: "<div style='display: flex; align-items: center'><img src='/static/images/cyanbag.png' class='small-review-image-annotation'></img><div>rework</div></div>"
                    }, {
                        allowOverlap: true,
                        point: {
                            xAxis: 0,
                            yAxis: 0,
                            x: "2016-07-27",
                            y: tsToReviewProp.get("2016-07-27")
                        },
                        x: -20,
                        y: 25,
                        text: "DECA takeover"
                    }, {
                        allowOverlap: true,
                        point: {
                            xAxis: 0,
                            yAxis: 0,
                            x: "2016-11-24",
                            y: tsToReviewProp.get("2016-11-24")
                        },
                        x: 0,
                        y: -5,
                        text: "Portal exploit fix"
                    }, {
                        allowOverlap: true,
                        point: {
                            xAxis: 0,
                            yAxis: 0,
                            x: "2017-08-01",
                            y: tsToReviewProp.get("2017-08-01")
                        },
                        x: -10,
                        y: 60,
                        useHTML: true,
                        text: "<img src='/static/images/lh.png' class='review-image-annotation'></img>"
                    }, {
                        allowOverlap: true,
                        point: {
                            xAxis: 0,
                            yAxis: 0,
                            x: "2018-05-24",
                            y: tsToReviewProp.get("2018-05-24")
                        },
                        x: -30,
                        y: -60,
                        useHTML: true,
                        text: "<div style='display: flex; align-items: center'><img src='/static/images/lh.png' class='small-review-image-annotation'></img><div style='padding-left:5px;'>rework</div></div>"
                    }, {
                        allowOverlap: true,
                        point: {
                            xAxis: 0,
                            yAxis: 0,
                            x: "2019-10-23",
                            y: tsToReviewProp.get("2019-10-23")
                        },
                        x: 0,
                        y: 50,
                        useHTML: true,
                        text: "<div style='display: flex; align-items: center'><img src='/static/images/totalia.png' class='review-image-annotation'></img><div>event</div></div>"
                    }, {
                        allowOverlap: true,
                        point: {
                            xAxis: 0,
                            yAxis: 0,
                            x: "2020-04-15",
                            y: tsToReviewProp.get("2020-04-15")
                        },
                        x: -40,
                        y: -5,
                        text: "Unity client"
                    }, {
                        allowOverlap: true,
                        point: {
                            xAxis: 0,
                            yAxis: 0,
                            x: "2020-07-22",
                            y: tsToReviewProp.get("2020-07-22")
                        },
                        x: 10,
                        y: -5,
                        useHTML: true,
                        text: "<img src='/static/images/osanc.png' class='review-image-annotation'></img>"
                    }, {
                        allowOverlap: true,
                        point: {
                            xAxis: 0,
                            yAxis: 0,
                            x: "2020-11-24",
                            y: tsToReviewProp.get("2020-11-24")
                        },
                        x: 20,
                        y: 40,
                        useHTML: true,
                        text: "<div style='display: flex; align-items: center'><img src='/static/images/fame.png' class='small-review-image-annotation'></img><div style='padding-left:5px;'>rework</div></div>"
                    }, {
                        allowOverlap: true,
                        point: {
                            xAxis: 0,
                            yAxis: 0,
                            x: "2021-08-26",
                            y: tsToReviewProp.get("2021-08-26")
                        },
                        useHTML: true,
                        x: -60,
                        y: -60,
                        text: "<div style='display: flex; align-items: center'><img src='/static/images/shatters.png' class='small-review-image-annotation'></img><div style='padding-left:5px;'>rework</div></div>"
                    }, {
                        allowOverlap: true,
                        point: {
                            xAxis: 0,
                            yAxis: 0,
                            x: "2022-08-02",
                            y: tsToReviewProp.get("2022-08-02")
                        },
                        x: 0,
                        y: -5,
                        text: "Season 1"
                    }, {
                        allowOverlap: true,
                        point: {
                            xAxis: 0,
                            yAxis: 0,
                            x: "2023-03-28",
                            y: tsToReviewProp.get("2023-03-28")
                        },
                        x: -40,
                        y: 50,
                        useHTML: true,
                        text: "<img src='/static/images/mv.png' class='review-image-annotation'></img>"
                    }, {
                        allowOverlap: true,
                        point: {
                            xAxis: 0,
                            yAxis: 0,
                            x: "2023-07-11",
                            y: tsToReviewProp.get("2023-07-11")
                        },
                        x: -50,
                        y: -45,
                        text: "Enchanting - release"
                    }, {
                        allowOverlap: true,
                        point: {
                            xAxis: 0,
                            yAxis: 0,
                            x: "2023-12-12",
                            y: tsToReviewProp.get("2023-12-12")
                        },
                        x: -50,
                        y: -80,
                        text: "Enchanting - rework"
                    }, {
                        allowOverlap: true,
                        point: {
                            xAxis: 0,
                            yAxis: 0,
                            x: "2024-11-26",
                            y: tsToReviewProp.get("2024-11-26")
                        },
                        x: -40,
                        y: 40,
                        text: "S18/Oryxmas"
                    }, {
                        allowOverlap: true,
                        point: {
                            xAxis: 0,
                            yAxis: 0,
                            x: "2025-05-06",
                            y: tsToReviewProp.get("2025-05-06")
                        },
                        x: -50,
                        y: -20,
                        text: "Enchanting - divines"
                    }
                ]
            },
        ],
    });

    return chart;
}