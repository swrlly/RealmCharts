import { COLORS, API_ENDPOINTS, BASE_CHART_OPTIONS, RANGE_SELECTOR_THEME } from '../config/constants.js';
import { getData } from '../api/dataService.js';
import { removeSkeleton } from '../ui/skeleton.js';

export async function createPlayerCountChart() {
    var data = await getData(API_ENDPOINTS.playerCount);

    // convert timestamps to milliseconds and hide 0 values
    for (let index = 0; index < data.length; index++) {
        data[index][0] *= 1000;
        data[index][1] = data[index][1] === 0 ? null : data[index][1];
    }
        
    // set global Highcharts options
    Highcharts.setOptions(BASE_CHART_OPTIONS);
    Highcharts.seriesTypes.scatter.prototype.getPointSpline = Highcharts.seriesTypes.spline.prototype.getPointSpline;
    
    var chart = Highcharts.stockChart("playercount-chart", {
        chart: {
            reflow: true,
            events: {
                async load() {
                    removeSkeleton();
                } 
            }
        },
        navigator: {
            enabled: true,
            maskFill: "rgba(102,133,194,0.08)",
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
            name: 'Players',
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
            type: 'datetime',
            labels: {
                style: {
                    color: COLORS.axisLabelColor
                }
            },
            ordinal: false,
            crosshair: {
                dashStyle: 'ShortDash'
            },
            tickPixelInterval: 120,
            min: Date.now() - (24 * 7 * 60 * 60 * 1000 + 5 * 60 * 1000), // 7 days, 5 min
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