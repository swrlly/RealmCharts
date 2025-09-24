import { API_ENDPOINTS } from "../config/constants.js";

// functions for updating dashboard cards + getting data

// data fetching function
export async function getData(link) {
    return Promise.resolve(fetch(link).then(response => response.json()));
}

// time utility function
export function tsToSeconds(time) {
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

// update player count timestamp display based on last player count time scraped
export function updatePlayerCountTimeUpdated(data) {
    const txt = tsToSeconds(data[data.length - 1][0]);
    let content = document.getElementById("players-last-updated");
    content.innerHTML = "Updated " + txt + " ago";
}

// update steam reviews last time updated
export async function updateReviewsTimeUpdated(time, fetchNew) {
    if (fetchNew) {
        const data = await getData(API_ENDPOINTS.lastReviewTimeScraped);
        time = data * 1000;
    }
    const txt = tsToSeconds(time);
    let content = document.getElementById("reviews-last-updated");
    content.innerHTML = "Updated " + txt + " ago";
    return Promise.resolve(time);
}

// update playercount dashboard cards with latest data
export async function updateCards(data) {

    var playersLastWeekPromise = getData(API_ENDPOINTS.playersLastWeek);
    var serverStatusPromise = getData(API_ENDPOINTS.serverUp);
    var [playersLastWeek, serverStatus] = await Promise.all([
        playersLastWeekPromise,
        serverStatusPromise
    ]);
    // update players now
    let content = document.getElementById("players-online");
    let num = data[data.length - 1][1];
    if (isFinite(num) && !isNaN(num) && num !== null) {
        if (num >= 1000) {
            let remainder = num % 1000;
            let thousands_digit = (num - remainder) / 1000;
            content.innerHTML = thousands_digit.toString() + "," + remainder.toString().padStart(3, "0");
        }
        else {
            content.innerHTML = num;
        }
    }
    else {
        content.innerHTML = "-"
    }
    
    // update weekly % change
    content = document.getElementById("players-weekly-change");

    let percent = parseFloat(((data[data.length-1][1] / playersLastWeek[1]) * 100  - 100).toFixed(2));
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

// update cards and chart data every minute
export async function updatePlayersJob(chart, data) {
    var latestPlayersPromise = getData(API_ENDPOINTS.latestPlayerCount);
    var updateCardsPromise = updateCards(data);
    var [newData, _] = await Promise.all([latestPlayersPromise, updateCardsPromise]);
    newData[0] *= 1000;
    // highcharts adds newData to original data. no need to do data.push(newData);
    chart.series[0].addPoint(newData);
    var now = new Date();
    if ((now.getMinutes() % 5) === 1 || (now.getMinutes() % 5) === 6) {
        var forecast = await getData(API_ENDPOINTS.forecast);

        for (let index = 0; index < forecast.length; index++) {
            forecast[index][1] = forecast.length == 0 ? null : forecast[index][1] * 1000;
        }
        let forecasted_mean = forecast.slice(0, forecast.length).map(i => [i[1], i[2]]);
        let one_sd = forecast.slice(0, forecast.length).map(i => [i[1], i[3], i[4]]);
        let two_sd = forecast.slice(0, forecast.length).map(i => [i[1], i[5], i[6]]);
        let three_sd = forecast.slice(0, forecast.length).map(i => [i[1], i[7], i[8]]);
        let content = document.getElementsByClassName("forecast-disabled-warning")[0];
        if (forecast.length == 0) {
            content.innerHTML = "Forecast disabled until 60 minutes after data collection returns.";
        }
        else {
            content.innerHTML = "";
            chart.series[1].setData(forecasted_mean, true, true, false);
            chart.series[2].setData(one_sd, true, true, false);
            chart.series[3].setData(two_sd, true, true, false);
            chart.series[4].setData(three_sd, true, true, false);
        }
    }

    return Promise.resolve([chart, data]);
}