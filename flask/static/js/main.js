import { createPlayerCountChart } from "./charts/playerCount.js";
import { createReviewsChart } from "./charts/reviews.js";
import { updateCards, updatePlayerCountTimeUpdated } from "./automation/dataService.js";
import { updatePlayerChart, updateReviewChart, updateReviewTime } from "./automation/timeouts.js"
import { positionTooltips } from "./ui/skeleton.js";

async function main() {

    // first loading in, load biggest api calls
    var playerChartPromise = createPlayerCountChart();
    var reviewChartPromise = createReviewsChart();
    var [[chart, data], reviewChart] = await Promise.all([
        playerChartPromise,
        reviewChartPromise
    ]);
    // smaller jobs
    await updateCards(data);
    updatePlayerCountTimeUpdated(data);
    positionTooltips();

    // live update logic
    // array is pass by ref...
    var lastReviewUpdateTime = [0];
    const reviewTimeId = setTimeout(updateReviewTime, 1000, lastReviewUpdateTime, true);
    // use setInterval for data b/c need data as global, fine if drifts.
    setInterval(updatePlayerCountTimeUpdated, 1000, data);

    // players
    var now = new Date().valueOf();
    const msUntilFirstUpdate = Math.max(60000 - (now - data[data.length - 1][0]), 1) + 3000;
    const playerUpdateId = setTimeout(updatePlayerChart, msUntilFirstUpdate, chart, data);
    // reviews
    const reviewUpdateId = setTimeout(updateReviewChart, 60000, reviewChart, lastReviewUpdateTime, reviewTimeId);
}

main();