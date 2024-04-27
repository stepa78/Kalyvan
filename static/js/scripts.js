$(document).ready(()=>{

    $('.create-account').click(function(){
        $.post('/account', success=(response)=>{console.log(response)});
    })


    $(".stock-chart").each((i, el)=>{
        const $el = $(el);

        const title = $el.data('title')
        const stock_id = $el.data('stock_id')

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

        if (stock_id == 1)
        {

//        setInterval(()=>{
            const dp = options.data[0].dataPoints;

            let timestamp = '';
            if (dp.length)
                 timestamp = dp[dp.length-1]

            $.get(
                `/api/prices?stock_id=${stock_id}&timestamp=${timestamp}`,
                (response)=>{
                    console.log(response);
                }
            );
//        }, 10000)
        }
    })
});