$(document).ready(()=>{

    $('.create-account').click(function(){
        $.post('/account', success=(response)=>{console.log(response)});
    })


    $(".stock-chart").each((i, el)=>{
        const title = $el.data('title')
        const stockId = $el.data('stockId')

        const $el = $(el);

        const options = {
            'title': {
                'text': title
            },
            data: [{
                type: "candlestick",
                dataPoints: []
            }]
        }

        const $chart = $el.CanvasJSChart(options);

        setTimeout(()=>{
            const dp = options.data[0].datapoints;

            let timestamp = '';
            if (dp.length)
                 timestamp = dp[dp.length-1]
            $.get(
                `/api/prices?stock_id=${stockId}&timestamp=${timestamp}`,
                (response)=>{
                    console.log(response);
                }
            );
        }, 10000)

        console.log($el);



    })


});