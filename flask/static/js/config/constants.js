var debug = false;

// color scheme for dashboard
export const COLORS = {
    backgroundColor: "#141414",
    seriesColor: "#517affff",
    columnColor: "#7b7b7b80",
    reviewColor: "#47bfff80",
    linesInChartColor: "#969696",
    yAxisLineColor: "#5e5e5e",
    inputBoxBorderColor: "#6e6e6e",
    axisLabelColor: "#adadadff",
    zoomLabelColor: "#c9c9c9",
    rangeSelectorColorDisabled: "rgba(16, 16, 16, 1)",
    rangeSelectorColor: "#1c1c1cff",
    rangeSelectorEnabled: "#343434ff",
    rangeSelectorHover: "#343434ff",
    textColor: "#c9c9c9",
    disabledTextColor: "#4a4a4aff"
};

// chart configuration
export const CHART_CONFIG = {
    font: "Open Sans"
};

// API endpoints
export const API_ENDPOINTS = {
    
    serverUp: debug == false ? "https://realmcharts.swrlly.com/api/is-game-online" : "http://localhost:8001/api/is-game-online",
    playerCount: debug == false ? "https://realmcharts.swrlly.com/api/playercount" : "http://localhost:8001/api/playercount",
    latestPlayerCount: debug == false ? "https://realmcharts.swrlly.com/api/players-now" : "http://localhost:8001/api/players-now",
    playersLastWeek: debug == false ? "https://realmcharts.swrlly.com/api/players-last-week" : "http://localhost:8001/api/players-last-week",
    reviews: debug == false ? "https://realmcharts.swrlly.com/api/review-proportions" : "http://localhost:8001/api/review-proportions",
    lastReviewTimeScraped: debug == false ? "https://realmcharts.swrlly.com/api/reviews-last-scraped" : "http://localhost:8001/api/reviews-last-scraped",
};

// common chart options that can be reused
export const BASE_CHART_OPTIONS = {
    chart: {
        backgroundColor: COLORS.backgroundColor,
        style: {
            fontFamily: CHART_CONFIG.font,
            color: COLORS.linesInChartColor,
            fontSize: "1rem"
        }
    }
};

// chart range selector
export const RANGE_SELECTOR_THEME = {
    fill: COLORS.rangeSelectorColor,
    states: {
        hover: {
            fill: COLORS.rangeSelectorHover,
            style: {
                color: COLORS.textColor
            }
        }, 
        select: {
            fill: COLORS.rangeSelectorEnabled,
        },
        disabled: {
            fill: COLORS.rangeSelectorColorDisabled,
            style: {
                color: COLORS.disabledTextColor
            }
        }
    },
    style: {
        color: COLORS.zoomLabelColor
    }
};