/* グローバル変数 */
var thank_you = 0;    //ありがとうの数
var count_disp = document.getElementById("disp_count");
var img = document.getElementById("view_area");
var send = document.getElementById('send');


/* クリックイベント処理 */
img.addEventListener('click', function(){
    //ありがとう加算
    thank_you++;

    if (thank_you > 20)
    {
        thank_you = 20
    }

    count_disp.innerHTML = thank_you;
}, false);





send.addEventListener('click', function(){

    // 送る相手の選択
    // ちゃんとやるなら、PHPが必要そう
    const friend_name = document.getElementById('friend_name').value;

    var arigato = {
      'thank_you': thank_you,
      'friend_name': friend_name
    }

    $.ajax({
      type: "POST",
      contentType: "application/json; charset=utf-8",
      url: "/point",
      data: JSON.stringify(arigato),// JSON文字列への変換をして、辞書をpythonに送る
      dataType: "json"
    });

    // 100マイクロ秒後に画面遷移→message_sent.htmlに
    setTimeout(function(){
      window.location.href = 'https://ide-7ebceea5200d4ec6b5f68152dd2b843c-8080.cs50.ws/point_sent';
    }, 100);

});