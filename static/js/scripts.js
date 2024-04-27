$(document).ready(()=>{

    $('.create-account').click(function(){
        $.post('/account', success=(response)=>{console.log(response)});
    })

    $('.user-avatar-active').click(()=>{
        $('.user-avatar-change').trigger('click');
    })


    $(".stock-chart").each((i, el)=>{
        const $el = $(el);

        const title = $el.data('title')
        const stock_id = $el.data('stock_id')

        const options = {
            'title': {
                'text': 'Акции ' + title
            },
            data: [{
                type: "candlestick",
                dataPoints: []
            }]
        }

        const $chart = $el.CanvasJSChart(options);

        //if (stock_id == 1){

            const update = () => {
                const dp = options.data[0].dataPoints;

                let timestamp = '';
                if (dp.length){
                     timestamp = dp[dp.length-1]['x'].getTime() / 1000;
                }

                $.get(
                    `/api/prices?stock_id=${stock_id}&timestamp=${timestamp}`,
                    (response)=>{
                        if (response){
                            console.log(response);
                            for(i=0; i<response.length; i++){
                                let y = response[i].y;
                                response[i].x = new Date(response[i].x*1000);
                                options.data[0].dataPoints.push(response[i])
                            }
                            //options.data[0].dataPoints.push(response)
                            $chart.CanvasJSChart().render();
                        }
                    }
                );
            }
            //window.UPD = update;
            setInterval(update, 5000);
        //}
    })
});