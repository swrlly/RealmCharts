import { updatePlayersJob, updateReviewsTimeUpdated } from "./dataService.js";
import { createReviewsChart } from "../charts/reviews.js";
import { enableReviewSkeleton } from "../ui/skeleton.js"

// use setTimeout instead of setInterval becuase setInterval drifts on firefox
export async function updatePlayerChart(chart, data) {
    updatePlayersJob(chart, data).then(result => {
        [chart, data] = result;
        var now = new Date().valueOf();
        const msUntilUpdate = Math.max(60000 - (now - data[data.length - 1][0]), 1) + 3000;
        const playerChartUpdateId = setTimeout(updatePlayerChart, msUntilUpdate, chart, data);
    });
}

// timeout for updating reviews text so no drift
export async function updateReviewTime(lastReviewUpdateTime, fetchNew) {
    updateReviewsTimeUpdated(lastReviewUpdateTime[0], fetchNew).then(result => {
        lastReviewUpdateTime[0] = result;
        const reviewUpdateId = setTimeout(updateReviewTime, 1000, lastReviewUpdateTime, false);
    });
}

export async function updateReviewChart(reviewChart, lastReviewUpdateTime, reviewTimeId) {
    var now = new Date();
    if (now.getMinutes() === 4) {
        updateReviewsTimeUpdated(lastReviewUpdateTime[0], true).then(result => {
            lastReviewUpdateTime[0] = result;
            reviewChart.destroy();
            enableReviewSkeleton();
            (async() => {
                reviewChart = await createReviewsChart();
                const reviewUpdateId = setTimeout(updateReviewChart, 60000, reviewChart, lastReviewUpdateTime, reviewTimeId);
            })();
        });
    }
    else {
        const reviewUpdateId = setTimeout(updateReviewChart, 60000, reviewChart, lastReviewUpdateTime, reviewTimeId);
    }
    
}