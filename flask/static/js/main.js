import { createPlayerCountChart } from './charts/playerCount.js';
import { createReviewsChart } from './charts/reviews.js';
import { updateCards, updateCardsJob, updatePlayerCountTimeUpdated, updateReviewsTimeUpdated } from './api/dataService.js';
import { positionTooltips, enableReviewSkeleton } from './ui/skeleton.js';

async function main() {
    // first loading in
    // players
    let [chart, data] = await createPlayerCountChart();
    updatePlayerCountTimeUpdated(data);
    positionTooltips();
    await updateCards(data);

    //reviews
    let [review_chart, review_data] = await createReviewsChart();
    console.log(review_data[5]);
    var lastReviewUpdateTime = 0;
    updateReviewsTimeUpdated(lastReviewUpdateTime, true).then(result => {
        lastReviewUpdateTime = result;
    })
    setInterval(updatePlayerCountTimeUpdated, 1000, data);
    let updateReviewIntervalId = setInterval(() => {
        updateReviewsTimeUpdated(lastReviewUpdateTime, false).then(result => {
            lastReviewUpdateTime = result;
        })
    }, 1000);

    // live update logic
    // players
    var now = new Date();
    const msUntilFirstUpdate = Math.max(60000 - (now - data[data.length - 1][0]), 1) + 1000;
    const firstPlayerUpdateId = setTimeout(() => {

        // first, update player dash area based on how much time left until next update
        updateCardsJob(chart, data).then(result => {
            [chart, data] = result;
            const playerUpdateIntervalId = setInterval(() => {
                // then, update dash every minute
                updateCardsJob(chart, data).then(result => {
                    [chart, data] = result;
                });
            }, 60000);
        });
    }, msUntilFirstUpdate);

    // reviews
    const reviewPollerIntervalID = setInterval(() => {
        now = new Date();
        // steam reviews finishes scraping <= 3 minutes, empirically speaking
        // need to push the check later >50k reviews
        if (now.getMinutes() === 5) {
            clearInterval(updateReviewIntervalId);
            review_chart.destroy();
            enableReviewSkeleton();
            (async() => {
                [review_chart, review_data] = await createReviewsChart();
                console.log(review_data);
            })();
            updateReviewIntervalId = setInterval(() => {
                    updateReviewsTimeUpdated(lastReviewUpdateTime, false).then(result => {
                        lastReviewUpdateTime = result;
                    })
                }, 1000);
            updateReviewsTimeUpdated(lastReviewUpdateTime, true).then(result => {
                lastReviewUpdateTime = result;
            });
        }
    }, 60000);
}

main();