/* グローバル変数 */
var thank_you = 0;    //ありがとうの数
var canvas = document.getElementById('view_area');  //htmlのcanvasを取得

var send = document.getElementById('send');


/* クリックイベント処理 */
canvas.addEventListener('click', function(){
    //ありがとう加算
    thank_you++;

    if (thank_you > 20)
    {
        thank_you = 20
    }
    //画面更新
    draw();
}, false);

/* 描画関数 */
function draw(){
    if (canvas.getContext) {
        var context = canvas.getContext('2d');
        //幅と高さ取得
        var w = canvas.width;
        var h = canvas.height;
        //Canvas全体をクリア
        context.clearRect(0, 0, w, h);

        //ありがとうの描画
        context.fillStyle = "red";
        context.font = "25px 'ＭＳ ゴシック'";
        context.textAlign = "left";
        context.textBaseline = "top";
        context.fillText(thank_you, 150, 100); //文字の描画
    }
}




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