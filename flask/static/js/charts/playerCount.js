import { COLORS, API_ENDPOINTS, BASE_CHART_OPTIONS, RANGE_SELECTOR_THEME } from "../config/constants.js";
import { getData } from "../automation/dataService.js";
import { removePlayerCountSkeleton } from "../ui/skeleton.js";

export async function createPlayerCountChart() {
    var data = await getData(API_ENDPOINTS.playerCount);
    var forecast = await getData(API_ENDPOINTS.forecast);

    // convert timestamps to milliseconds
    for (let index = 0; index < data.length; index++) {
        data[index][0] *= 1000;
    }
    for (let index = 0; index < forecast.length; index++) {
        forecast[index][1] *= 1000;
    }

    let forecasted_mean = forecast.slice(0, forecast.length).map(i => [i[1], i[2]]);
    let one_sd = forecast.slice(0, forecast.length).map(i => [i[1], i[3], i[4]]);
    let two_sd = forecast.slice(0, forecast.length).map(i => [i[1], i[5], i[6]]);
    let three_sd = forecast.slice(0, forecast.length).map(i => [i[1], i[7], i[8]]);

    /*
    var fakeData = new Array();
    for (let index = 1; index < 49; index++) {
        fakeData.push([data[data.length-1][0] + index * 300 * 1000, data[data.length-1][1] - 2 * index, data[data.length-1][1] + 2 * index]);
    }
    var fakeData2 = new Array();
    for (let index = 1; index < 49; index++) {
        fakeData2.push([data[data.length-1][0] + index * 300 * 1000, data[data.length-1][1] - 4 * index, data[data.length-1][1] + 4 * index]);
    }*/

        
    // set global Highcharts options
    Highcharts.setOptions(BASE_CHART_OPTIONS);
    Highcharts.seriesTypes.scatter.prototype.getPointSpline = Highcharts.seriesTypes.spline.prototype.getPointSpline;
    
    var chart = Highcharts.stockChart("playercount-chart", {
        chart: {
            reflow: true,
            type: "arearange",
            events: {
                async load() {
                    removePlayerCountSkeleton();
                } 
            }
        },
        plotOptions: {
        arearange: {
            enableMouseTracking: false,
            states: {
                inactive: {
                    enabled: false
                }
            },
            color: COLORS.forecastColor,
            fillOpacity: 0.1,
            lineWidth: 0
        }
        },
        navigator: {
            enabled: true,
            maskFill: "rgba(133, 133, 133, 0.08)",
            xAxis: {
                labels: {
                    style: {
                        color: COLORS.linesInChartColor
                    }
                },
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
        title: {
            enabled: false
        },
        rangeSelector: {
            enabled: true,
            buttons: [
                {
                    type: "day",
                    count: 2,
                    text: "48h"
                }, {
                    type: "minute",
                    count: 10110,
                    text: "7d"
                }, {
                    type: "month",
                    count: 1,
                    text: "1m",
                    enabled: false,
                }, {
                    type: "year",
                    count: 1,
                    text: "1y",
                    enabled: false,
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
                border: "none"
            },
            labelStyle: {
                color: COLORS.zoomLabelColor
            },
            inputBoxBorderColor: COLORS.backgroundColor
        },
        series: [{
            type: "line",
            name: "Players",
            data: data,
            lineWidth: 3,
            showInNavigator: true,
            color: COLORS.seriesColor,
            tooltip: {
                backgroundColor: COLORS.backgroundColor,
                hideDelay: 0,
                style: {
                    color: COLORS.textColor,
                },
                pointFormatter: function() {
                    return `<span style="color:${this.color}">\u25CF</span> ${this.series.name}:`
                        + ` <b>${parseFloat(this.y.toFixed(2))}</b><br/>`;
                }
            },
            showInLegend: true
        }, {
            name: "Forecasted mean",
            type: "line",
            lineWidth: 3,
            showInNavigator: true,
            data: forecasted_mean,
            color: COLORS.forecastColor,
            tooltip: {
                backgroundColor: COLORS.backgroundColor,
                hideDelay: 0,
                style: {
                    color: COLORS.textColor,
                },
                pointFormatter: function() {
                    return `<span style="color:${this.color}">\u25CF</span> ${this.series.name}:`
                        + ` <b>${parseFloat(this.y.toFixed(2))}</b><br/>`;
                }
            },
        }, {
            name: "1σ",
            data: one_sd,
            color: COLORS.forecastColor,
        }, {
            name: "2σ",
            data: two_sd,
            color: COLORS.forecastColor,
        }, {
            name: "3σ",
            data: three_sd,
            color: COLORS.forecastColor,
        }],
        xAxis: {
            lineColor: COLORS.linesInChartColor,
            tickColor: COLORS.linesInChartColor,
            gridLineWidth: 0,
            type: "datetime",
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
            min: Date.now() - (3 * 24 * 60 * 60 * 1000),//Date.now() - (24 * 7 * 60 * 60 * 1000 + 30 * 60 * 1000), // 7 days, 30 min
            max: forecast[forecast.length - 1][1],//Date.now(),
            plotBands: [{
                color: 'rgba(201, 113, 255, 0.05)',
                from: forecast[0][1] - 300,
                to: Number.MAX_SAFE_INTEGER,
                label: {
                    text: "Forecast",
                    style: {
                        color: COLORS.textColor,
                    }
                }
            }],
            plotLines: [{
                dashStyle: "dash",
                color: COLORS.plotBandLineColor,
                width: 4,
                value: 5
            }]
        },
        yAxis: {
            gridLineColor: COLORS.yAxisLineColor,
            labels: {
                style: {
                    color: COLORS.axisLabelColor
                }
            }
        },
        tooltip: {
            shared: true,
            backgroundColor: COLORS.backgroundColor,
            hideDelay: 0,
            style: {
                color: COLORS.textColor,
            }
        }
    });
    
    return [chart, data];
}