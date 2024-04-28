$(document).ready(()=>{

    $('.create-account').click(function(){
        $.post('/account', success=(response)=>{
            $('main.main').prepend(`
                <div class="alert alert-primary" role="alert">
                  <a href="${response.url}">Для вас создан счет ${response.account.code}</a>
                </div>
            `)
        });
    })

    $('.delete-account').click(function(){
        const account_id = $(this).data('account_id');
        $.ajax({
            url: `/account/${account_id}`,
            type: 'DELETE',
            success: function(result) {
                console.log(result);
                window.location = '/dashboard';
            }
        });
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
            setInterval(update, 5000);
        //}
    })

    $('button.buy_sell').click((e)=>{
        const $button = $(e.target);
        const $form = $button.closest('form.buy_sell');
        const action = $button.data('action');
        const size = $form.find('input[name="size"]').val();
        const stock_id = $form.find('input[name="stock_id"]').val();
        const account_id = $form.find('input[name="account_id"]').val();
        $.ajax({
            url: `/api/${action}/${account_id}/${stock_id}?size=${size}`,
            success: function(result){
                console.log(result);
            }
        });
    })
});