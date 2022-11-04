'use strict';
{
    // 定数を定義して、HTMLから要素を取得
    const del = document.getElementById('del');

    // 削除のボタンが押された時の処理
    del.addEventListener('click', () => {
      // プルダウンの値を取得する
      const deleted_friend_name = document.getElementById('friend_delete').value;

      // /deleteのルートにデータを渡す
      $.ajax({
        type: "POST",
        contentType: "application/json; charset=utf-8",
        url: "/delete",
        data: JSON.stringify(deleted_friend_name),
        dataType: "json"
      });

      setTimeout(function(){
        window.location.href = 'https://presentthanks.pythonanywhere.com/friend';
      }, 100);

    });

}