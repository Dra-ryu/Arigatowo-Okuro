/* グローバル変数 */
var thankyou_point = 0;    //ありがとうの数
var count_disp = document.getElementById("disp_count");
var thankyou_btn = document.getElementById("thankyou_btn");
var send = document.getElementById('send');


thankyou_btn.addEventListener('click', function(){

    //ありがとうポイント加算
    thankyou_point++;

    if (thankyou_point >= 20)
    {
        thankyou_point = 20
        document.getElementById("disp_count").style.color = "red";
    }

    // 現在のポイントを画面に表示
    count_disp.innerHTML = thankyou_point;
}, false);


send.addEventListener('click', function(){

    // 送る相手の選択
    const friend_name = document.getElementById('friend_name').value;

    // pythonに送る情報
    var point_information = {
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

    // 表示するメッセージ
    var message = friend_name + 'さんに' + thankyou_point + 'ありがとうポイントを送りました！';

    // sweatalert
    swal({
        text: message,
        icon: 'success',
    })

    // 2秒後にページ遷移する
    setTimeout(function(){
        window.location.href = 'https://ide-7ebceea5200d4ec6b5f68152dd2b843c-8080.cs50.ws/home';
    }, 2*1000);

});