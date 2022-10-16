'use strict';

{
    // 定数を定義して、HTMLから要素を取得
    const add = document.getElementById('add');

    // 追加のボタンが押された時の処理
    add.addEventListener('click', () => {

    // セレクトボックスの値を取得
    const added_friend_name = document.getElementById('friend_add').value;

    // /addのルートに値を送る
    $.ajax({
      type: "POST",
      contentType: "application/json; charset=utf-8",
      url: "/add",
      data: JSON.stringify(added_friend_name),// JSON文字列への変換をして、辞書をpythonに送る
      dataType: "json"
    });

    // 1マイクロ秒後に画面遷移→タイマー機能へ
    setTimeout(function(){
      window.location.href = 'https://presentthanks.pythonanywhere.com/friend';
    }, 100);

    });

}
