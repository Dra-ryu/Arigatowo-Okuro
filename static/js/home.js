'use strict';

{
    // 定数を定義して、HTMLから要素を取得
    const cooking = document.getElementById('cooking');
    const shopping = document.getElementById('shopping');
    const cleaning = document.getElementById('cleaning');
    const washing = document.getElementById('washing');
    const garbage = document.getElementById('garbage');
    const transfer = document.getElementById('transfer');
    const others = document.getElementById('others');
    const decision = document.getElementById('decision');

    // 最初に初期化して、家事のボタンを押すまで決定を押せなくする
    (function () {
        decision.classList.add('inactive');
    }());

    // ボタンが1つ押された時、他のボタンをinactiveに変更して押せなくする
    function cookingOn() {
        shopping.classList.add('inactive');
        cleaning.classList.add('inactive');
        washing.classList.add('inactive');
        garbage.classList.add('inactive');
        transfer.classList.add('inactive');
        others.classList.add('inactive');
        decision.classList.remove('inactive');
    }

    function shoppingOn() {
        cooking.classList.add('inactive');
        cleaning.classList.add('inactive');
        washing.classList.add('inactive');
        garbage.classList.add('inactive');
        transfer.classList.add('inactive');
        others.classList.add('inactive');
        decision.classList.remove('inactive');
    }

    function cleaningOn() {
        cooking.classList.add('inactive');
        shopping.classList.add('inactive');
        washing.classList.add('inactive');
        garbage.classList.add('inactive');
        transfer.classList.add('inactive');
        others.classList.add('inactive');
        decision.classList.remove('inactive');
    }

    function washingOn() {
        cooking.classList.add('inactive');
        shopping.classList.add('inactive');
        cleaning.classList.add('inactive');
        garbage.classList.add('inactive');
        transfer.classList.add('inactive');
        others.classList.add('inactive');
        decision.classList.remove('inactive');
    }

    function garbageOn() {
        cooking.classList.add('inactive');
        shopping.classList.add('inactive');
        cleaning.classList.add('inactive');
        washing.classList.add('inactive');
        transfer.classList.add('inactive');
        others.classList.add('inactive');
        decision.classList.remove('inactive');
    }

    function transferOn() {
        cooking.classList.add('inactive');
        shopping.classList.add('inactive');
        cleaning.classList.add('inactive');
        washing.classList.add('inactive');
        garbage.classList.add('inactive');
        others.classList.add('inactive');
        decision.classList.remove('inactive');
    }

    function othersOn() {
        cooking.classList.add('inactive');
        shopping.classList.add('inactive');
        cleaning.classList.add('inactive');
        washing.classList.add('inactive');
        garbage.classList.add('inactive');
        transfer.classList.add('inactive');
        decision.classList.remove('inactive');
    }


    // 料理ボタンが押された時の処理
    // 他のボタンが押されてinactiveになっていたら、反応しない
    cooking.addEventListener('click', () => {
    if (cooking.classList.contains('inactive') === true) {
      return;
    }

    // houseworkというkeyにcookingを入れる
    // 家事名を入れることで、そのままtimerの表示でも使えるように改良(代入とかが必要ない)
    localStorage.setItem('housework', '料理');

    // cookingボタンが押された状態にする
    cookingOn();
    });


    // 買い物ボタンが押された時
    shopping.addEventListener('click', () => {
    if (shopping.classList.contains('inactive') === true) {
      return;
    }

    localStorage.setItem('housework', '買い物');
    shoppingOn();
    });


    // 掃除ボタンが押された時
    cleaning.addEventListener('click', () => {
    if (cleaning.classList.contains('inactive') === true) {
      return;
    }

    localStorage.setItem('housework', '掃除');
    cleaningOn();
    });


    // 洗濯ボタンが押された時
    washing.addEventListener('click', () => {
    if (washing.classList.contains('inactive') === true) {
      return;
    }

    localStorage.setItem('housework', '洗濯');
    washingOn();
    });


    // ゴミ捨てボタンが押された時
    garbage.addEventListener('click', () => {
    if (garbage.classList.contains('inactive') === true) {
      return;
    }

    localStorage.setItem('housework', 'ゴミ捨て');
    garbageOn();
    });


    // 送迎ボタンが押された時
    transfer.addEventListener('click', () => {
    if (transfer.classList.contains('inactive') === true) {
      return;
    }

    localStorage.setItem('housework', '送迎');
    transferOn();
    });


    // その他の家事ボタンが押された時
    others.addEventListener('click', () => {
    if (others.classList.contains('inactive') === true) {
      return;
    }

    localStorage.setItem('housework', 'その他の家事');
    othersOn();
    });



    // 決定のボタンが押された時の処理
    decision.addEventListener('click', () => {

    // 家事のボタンが押されていない時には決定を押せなくする
    if (decision.classList.contains('inactive') === true) {
      return;
    }

    // 送る相手の選択と名前の取得
    const friend_name = document.getElementById('friend_name').value;

    // 送る相手が選択されていなかった場合、決定を押せなくする
    if (friend_name === '選択してください') {
      return;
    }

    // 選択されたfriend_nameをローカルストレージへ
    localStorage.setItem('friend_name', friend_name);

    // 100マイクロ秒後に画面遷移→タイマー機能へ
    setTimeout(function(){
      window.location.href = 'https://ide-7ebceea5200d4ec6b5f68152dd2b843c-8080.cs50.ws/timer';
    }, 100);

  });
}