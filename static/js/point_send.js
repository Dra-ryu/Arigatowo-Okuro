'use strict';
{
    let thankyou_point = 0;
    const count_disp = document.getElementById("disp_count");
    const thankyou_btn = document.getElementById("thankyou_btn");
    const send = document.getElementById('send');

    thankyou_btn.addEventListener('click', function(){
        // ありがとうポイント加算
        thankyou_point++;

        if (thankyou_point >= 20) {
            thankyou_point = 20
            document.getElementById("disp_count").style.color = "red";
        }

        // 現在のポイントを画面に表示
        count_disp.innerHTML = thankyou_point;
    });


    send.addEventListener('click', function(){

        // 送る相手の選択
        const friend_name = document.getElementById('friend_name').value;

        // pythonに送る情報
        const point_information = {
            'thank_you': thankyou_point,
            'friend_name': friend_name
        }

        $.ajax({
            type: "POST",
            contentType: "application/json; charset=utf-8",
            url: "/point",
            data: JSON.stringify(point_information),// JSON文字列への変換をして、辞書をpythonに送る
            dataType: "json"
        });

        // sweatalertで表示するメッセージ
        const message = friend_name + 'さんに' + thankyou_point + 'ありがとうポイントを送りました！';
        swal({
            text: message,
            icon: 'success',
        })

        // 渡すデータをひとまとめに
        const forLineMessage = {
            'thankyou_point': thankyou_point,
            'friend_name': friend_name
        }

        $.ajax({
            type: "POST",
            contentType: "application/json; charset=utf-8",
            url: "/point-message-send",
            data: JSON.stringify(forLineMessage),  // JSON文字列への変換をして、辞書をpythonに送る
            dataType: "json"
        });

        // 2秒後にページ遷移する
        setTimeout(function(){
            window.location.href = 'https://presentthanks.pythonanywhere.com/home';
        }, 2*1000);

    });
}