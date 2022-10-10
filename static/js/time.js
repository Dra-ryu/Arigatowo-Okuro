//参考URL: https://poisoncreation.wordpress.com/2020/09/11/stopwatch/

'use strict';

{
    const timer = document.getElementById('timer');
    const start = document.getElementById('start');
    const finish = document.getElementById('finish');

    let startTime;       // Startボタンクリック時の時刻
    let elapsedTime = 0; // StartからStopまでの経過時間
    let movingTimer;     // 繰り返し処理で使う用

    let timerOn = localStorage.getItem('timer_on'); //タイマーの動作状況

    // home.jsにおいて値を入力したローカルストレージから値を取りだし、HTML上に表示
    const housework_name = localStorage.getItem('housework');
    const partner_username = localStorage.getItem('friend_name');

    document.getElementById('housework_name').innerHTML = housework_name;
    document.getElementById('partner_username').innerHTML = partner_username;


    // タイマーが動作中だったら
    if (timerOn === 'on') {
        start.classList.add('inactive');   // 非活性
        finish.classList.remove('inactive');
        callPrintTime();
    }
    // 動作していない場合はstateに0を入れてボタンを初期状態に
    else {
        localStorage.setItem('timer_on', 'off');
        start.classList.remove('inactive'); // 活性
        finish.classList.add('inactive');
    }


    // 状態:初期
    function setButtonStateInitial() {
        start.classList.remove('inactive'); // 活性
        finish.classList.add('inactive');
    }

    // 状態:タイマー動作中
    function setButtonStateRunning() {
        start.classList.add('inactive');   // 非活性
        finish.classList.remove('inactive');  //活性
    }

    // タイマー部分の処理
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

        const main =
                  String(Math.floor(time/ 3600000) % 60).padStart(2, '0') + ':' +  // .padstartは文字列の長さと埋める文字を指定するもの→2文字で、残りは0で埋める
                  String(Math.floor(time / 60000) % 60).padStart(2, '0') + ':' +
                  String(Math.floor(time / 1000) % 60).padStart(2, '0');

        return main;
    }


    // Startボタンクリック
    start.addEventListener('click', () => {
        if (start.classList.contains('inactive') === true) {
            return;
    }

        setButtonStateRunning();  // ボタンをタイマー'動作中'状態とする

        // 現在の時間を取得して、ローカルストレージに格納
        startTime = Date.now();
        localStorage.setItem('startTime', startTime);  // startTimeというkeyに対応するstartTime変数をローカルストレージに入れる
        localStorage.setItem('timer_on', 'on');

        callPrintTime();
    });

    // finishボタンクリック
    finish.addEventListener('click', () => {
        // finishがinactiveなら、何も動かないようにする
        if (finish.classList.contains('inactive') === true) {
            return;
      }

        elapsedTime = localStorage.getItem('elapsedTime');

        clearInterval(movingTimer);  // タイマーを止める

        elapsedTime = Math.floor(elapsedTime / 60000);  // ミリ秒をminに変換して、小数点以下切り捨て

        // 表示するメッセージ
        var message = housework_name + 'を' + elapsedTime + '分しました！\n' + partner_username + 'さんに通知を送りました！';

        // sweatalert
        swal({
            text: message,
            icon: 'success',
        })

        // 渡すデータをひとまとめに(pythonだと辞書型になる)
        var forLineMessage = {
            'elapsedTime': elapsedTime,
            'housework_name': housework_name,
            'partner_username': partner_username
        }

        // python(timer.py)にデータを送る
        $.ajax({
            type: "POST",
            contentType: "application/json; charset=utf-8",
            url: "/message-send",
            data: JSON.stringify(forLineMessage),  // JSON文字列への変換をして、辞書をpythonに送る
            dataType: "json"
        });

        // 2秒後にページ遷移する
        setTimeout(function(){
            window.location.href = 'http://127.0.0.1:5000/home';
        }, 2*1000);

        localStorage.clear();  // localstorage初期化

    });
}