import { createPlayerCountChart } from './charts/playerCount.js';
import { createReviewsChart } from './charts/reviews.js';
import { updateCards, updateCardsJob, updatePlayerCountTimeUpdated } from './api/dataService.js';
import { positionTooltips } from './ui/skeleton.js';

async function main() {
    let [chart, data] = await createPlayerCountChart();
    updatePlayerCountTimeUpdated(data);
    positionTooltips();
    await updateCards(data);
    let [review_chart, review_data] = await createReviewsChart();
    setInterval(updatePlayerCountTimeUpdated, 1000, data);
    // begin live update logic
    const now = new Date();
    const msUntilFirstUpdate = Math.max(60000 - (now - data[data.length - 1][0]), 1) + 1000;
    //console.log("waiting", msUntilFirstUpdate / 1000, "seconds");
    const firstJobId = setTimeout(() => {
        updateCardsJob(chart, data).then(result => {
            [chart, data] = result;
            //console.log("first update", data[data.length - 1])
            const intervalJobId = setInterval(() => {
                updateCardsJob(chart, data).then(result => {
                    [chart, data] = result;
                    //console.log("reg update", data[data.length - 1]);
                });
            }, 60000);
        });
    }, msUntilFirstUpdate);
}

main();