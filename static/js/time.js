//参考URL: https://poisoncreation.wordpress.com/2020/09/11/stopwatch/

'use strict';

{
  const timer = document.getElementById('timer');
  const start = document.getElementById('start');
  const finish = document.getElementById('finish');

  let startTime;       // Startボタンクリック時の時刻
  let elapsedTime = 0; // StartからStopまでの経過時間
  let movingTimer;  // 繰り返し処理で使う用

  let state = localStorage.getItem('state');

  // home.jsで入れたローカルストレージから値を取って、HTML上に表示
  const housework_name = localStorage.getItem('housework');
  const partner_username = localStorage.getItem('friend_name');

  document.getElementById('housework_name').innerHTML = housework_name;
  document.getElementById('partner_username').innerHTML = partner_username;


  // タイマーが動作中だったら
  if (state === '1') {
    start.classList.add('inactive');   // 非活性
    finish.classList.remove('inactive');
    callPrintTime();
  }
  // 動作していない場合はstateに0を入れてボタンを初期状態に
  else {
    localStorage.setItem('state', 0);
    start.classList.remove('inactive'); // 活性
    finish.classList.add('inactive');
  }


  // 状態:初期 または Reset直後
  // inactiveとかは特定の要素のクラスのこと(分類の一つだね。)
  function setButtonStateInitial() {
    start.classList.remove('inactive'); // 活性
    finish.classList.add('inactive');

    }

  // 状態:タイマー動作中
  function setButtonStateRunning() {
    start.classList.add('inactive');   // 非活性
    finish.classList.remove('inactive');  //活性
  }

  /*
  function setButtonStateStopped() {
    start.classList.add('inactive');   // 非活性
    finish.classList.remove('inactive');  //活性
  }
  */

  // ボタンを'初期'状態とする
  // setButtonStateInitial()

  // Startボタンクリック
  // …タイマーを開始します
  start.addEventListener('click', () => {
    if (start.classList.contains('inactive') === true) {
      return;
    }
    // ボタンをタイマー'動作中'状態とする
    setButtonStateRunning();
    // 現在の時間を取得して、ローカルストレージに格納
    startTime = Date.now();
    localStorage.setItem('startTime', startTime);  // startTimeというkeyに対応するstartTime変数をローカルストレージに入れる
    localStorage.setItem('state', 1);

    callPrintTime();
  });

  function callPrintTime () {
    // setIntervalによって、1マイクロ秒ごとにprintTimeを呼び起こす
    movingTimer = setInterval(printTime, 1);
  }

  function printTime() {
    // この処理によって、HTMLのid=timerの部分のtextが右辺のものになる
    document.querySelector('#timer').textContent = getTimeString();
  }

  function getTimeString() {
    const now = Date.now();
    const time = now - localStorage.getItem('startTime');
    localStorage.setItem('elapsedTime', time);  // 今の時間から、startを押した時間を引くことで経過時間を示す
    // localStorage.setItem('time', time);


    const main =
              String(Math.floor(time/ 3600000) % 60).padStart(2, '0') + ':' +  // .padstartは文字列の長さと埋める文字を指定するもの→2文字で、残りは0で埋める
              String(Math.floor(time / 60000) % 60).padStart(2, '0') + ':' +
              String(Math.floor(time / 1000) % 60).padStart(2, '0');

    return main;
  }


  /*
  stop.addEventListener('click', () => {
    if (stop.classList.contains('inactive') === true) {
      return;
    }
    // ボタンをタイマー'停止中'状態とする
    setButtonStateStopped();
    // 現在の時間を取得して、ローカルストレージに格納
    startTime = Date.now();
    localStorage.setItem('startTime', startTime);  // startTimeというkeyに対応するstartTime変数をローカルストレージに入れる
    localStorage.setItem('state', 1);
  });
*/

  // finishが押されたら
  finish.addEventListener('click', () => {
    // finishがまだinactiveなら、何も動かないようにする
    if (finish.classList.contains('inactive') === true) {
      return;
    }

    elapsedTime = localStorage.getItem('elapsedTime');

    clearInterval(movingTimer);
    // setTimeout(printTime, 1);

    //elapsedTime = Math.floor(time / 60000);
    //elapsedTime += Date.now() - localStorage.getItem('startTime');
    elapsedTime = Math.floor(elapsedTime / 60000);  // m秒をminに変換して、小数点以下切り捨て

    // 表示するメッセージ
    var message = housework_name + 'を' + elapsedTime + '分しました！\n' + partner_username + 'さんに通知を送りました！';

    // sweatalert
    swal({
      text: message,
      icon: 'success',
    })

    // 渡すデータをひとまとめに(pythonだと辞書型になると思う)
    var forLineMessage = {
      'elapsedTime': elapsedTime,
      'housework_name': housework_name,
      'partner_username': partner_username
    }

    $.ajax({
      type: "POST",
      contentType: "application/json; charset=utf-8",
      url: "/message-send",
      data: JSON.stringify(forLineMessage),// JSON文字列への変換をして、辞書をpythonに送る
      dataType: "json"
    });

    // メッセージを消してから1秒後にページ遷移できるようにする
    //
    setTimeout(function(){
      window.location.href = 'https://ide-7ebceea5200d4ec6b5f68152dd2b843c-8080.cs50.ws/home';
    }, 2*1000);

    localStorage.clear();  // finishを押すと、localstorageが初期化

  });
}