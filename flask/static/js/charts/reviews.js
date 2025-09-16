import { COLORS, API_ENDPOINTS, RANGE_SELECTOR_THEME } from '../config/constants.js';
import { getData } from '../api/dataService.js';
import { removeReviewSkeleton } from '../ui/skeleton.js';

export async function createReviewsChart() {
    var data = await getData(API_ENDPOINTS.reviews);
    
    // process data for dual-axis chart
    let reviews = data.slice(0, data.length - 1).map(i => i.slice(0, 2));
    let proportions = data.slice(0, data.length - 1).map(i => [i[0], i[2] * 100]);
    
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
            enabled: false
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
                text: "% positive reviews"
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
            name: "Positive reviews",
            type: "spline",
            yAxis: 0, // left axis
            lineWidth: 3,
            data: proportions,
            color: COLORS.seriesColor,
            tooltip: {
                valueSuffix: "%",
                pointFormatter: function() {
                    return `<span style="color:${this.color}">\u25CF</span> ${this.series.name}:`
                        + ` <b>${this.y.toFixed(2)}%</b><br/>`;
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
                dashStyle: 'ShortDash'
            },
            tickPixelInterval: 120,
        },
        legend: {
            align: 'left',
            verticalAlign: 'top'
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