import { COLORS, API_ENDPOINTS, BASE_CHART_OPTIONS, RANGE_SELECTOR_THEME } from "../config/constants.js";
import { getData } from "../automation/dataService.js";
import { removePlayerCountSkeleton } from "../ui/skeleton.js";

export async function createPlayerCountChart() {
    var data = await getData(API_ENDPOINTS.playerCount);

    // convert timestamps to milliseconds
    for (let index = 0; index < data.length; index++) {
        data[index][0] *= 1000;
    }
        
    // set global Highcharts options
    Highcharts.setOptions(BASE_CHART_OPTIONS);
    Highcharts.seriesTypes.scatter.prototype.getPointSpline = Highcharts.seriesTypes.spline.prototype.getPointSpline;
    
    var chart = Highcharts.stockChart("playercount-chart", {
        chart: {
            reflow: true,
            events: {
                async load() {
                    removePlayerCountSkeleton();
                } 
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
        title: {
            enabled: false
        },
        rangeSelector: {
            enabled: true,
            buttons: [
                {
                    type: "day",
                    count: 1,
                    text: "24h"
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
            name: "Players",
            data: data,
            lineWidth: 3,
            color: COLORS.seriesColor,
            tooltip: {
                backgroundColor: COLORS.backgroundColor,
                hideDelay: 0,
                style: {
                    color: COLORS.textColor,
                },
                pointFormatter: function() {
                    return `<span style="color:${this.color}">\u25CF</span> ${this.series.name}:`
                        + ` <b>${this.y.toFixed(2)}</b><br/>`;
                }
            },
            showInLegend: true
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
            min: Date.now() - (24 * 7 * 60 * 60 * 1000 + 30 * 60 * 1000), // 7 days, 30 min
            max: Date.now()
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