'use strict';

{
    // 定数を定義して、HTMLから要素を取得
    const del = document.getElementById('del');

    // 削除のボタンが押された時の処理
    del.addEventListener('click', () => {

    // セレクトボックスの値を取得する
    const deleted_friend_name = document.getElementById('friend_delete').value;

    // /deleteのルートに値を送る
    $.ajax({
      type: "POST",
      contentType: "application/json; charset=utf-8",
      url: "/delete",
      data: JSON.stringify(deleted_friend_name),// JSON文字列への変換をして、辞書をpythonに送る
      dataType: "json"
    });

    
    // 100マイクロ秒後に画面遷移→タイマー機能へ
    //(1マイクロ秒だと、データベースに入れるのが間に合わず、リロードしないとフレンドリストに反映されない)
    
    setTimeout(function(){
      window.location.href = 'https://ide-7ebceea5200d4ec6b5f68152dd2b843c-8080.cs50.ws/friend';
    }, 100);

    });

}