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

    // convert timestamps to milliseconds
    for (let index = 0; index < data.length; index++) {
        data[index][0] *= 1000;
    }
    
    let reviews = data.slice(0, data.length).map(i => [i[0], i[1]]);
    let proportions = data.slice(0, data.length).map(i => [i[0], i[2] * 100]);
    
    var chart = Highcharts.stockChart("review-chart", {
        chart: {
            reflow: true,
            events: {
                async load() {
                    removeReviewSkeleton();
                } 
            }
        },
        navigator: {
            enabled: false,
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
                style: {
                    color: COLORS.axisLabelColor
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
                style: {
                    color: COLORS.axisLabelColor
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
            /*
            events: {
                setExtremes: function(event) {
                    console.log(event.min);
                    console.log(event.max);
                }*/
            events: {
                /* 
                0 date,
                1 daily_total_reviews, 
                2 all_time_prop, 
                3 daily_playtime_last_two_weeks, 
                4 daily_votes_up, 
                5 daily_playtime_at_review, 
                6 daily_playtime_forever
                */
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
            }
        }
    });

    return chart;
}