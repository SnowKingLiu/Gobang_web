// 获得棋盘
var chess = document.getElementById("mycanvas");
var context = chess.getContext('2d');
var isBlack = true;
var computerFirst = false;

// 用于存放棋盘中落子的情况
var chessBox = [];

// 初始化棋盘,i代表行，j代表列
for(var i=0;i<15;i++){
    chessBox[i]=[];
    for(var j=0;j<15;j++){
        chessBox[i][j]=0;
    }
}

// 定义棋盘
function drawChessBoard(){
    for(var i=0;i<15;i++){
        context.strokeStyle="#D6D1D1";
        // 垂直方向画15根线，相距30px;
        context.moveTo(15+i*30,15);
        context.lineTo(15+i*30,435);
        context.stroke();
        // 水平方向画15根线，相距30px;棋盘为14*14；
        context.moveTo(15,15+i*30);
        context.lineTo(435,15+i*30);
        context.stroke();
    }
}

// 绘制棋盘
drawChessBoard();

function oneStep(i,j,k){
    context.beginPath();
    // 绘制棋子
    context.arc(15+j*30,15+i*30,13,0,2*Math.PI);
    // 设置渐变
    var g=context.createRadialGradient(15+j*30,15+i*30,13,15+j*30,15+i*30,0);
    // k=true是黑棋，否则是白棋
    if(k){ //黑棋
        g.addColorStop(0,'#0A0A0A');
        g.addColorStop(1,'#636766');
    }else { //白棋
        g.addColorStop(0,'#D1D1D1');
        g.addColorStop(1,'#F9F9F9');
    }
    context.fillStyle=g;
    context.fill();
    context.closePath();
}

// 落子
chess.onclick=function(e){
    // 相对于棋盘左上角的x坐标
    var x = e.offsetX;
    // 相对于棋盘左上角的y坐标
    var y = e.offsetY;
    var j = Math.floor(x/30);
    var i = Math.floor(y/30);
    // 判断是否已落过子，黑棋是1，白棋是-1
    if(chessBox[i][j] == 0) {
        if(isBlack){
            if(!computerFirst){
                oneStep(i,j,isBlack);
                chessBox[i][j]=1;
                // 换人
                isBlack=!isBlack;
                // 汇报一次局势
                updateChessboard();
            }
        }else{
            if(computerFirst) {
                oneStep(i, j, isBlack);
                chessBox[i][j] = -1;
                // 换人
                isBlack=!isBlack;
                // 汇报一次局势
                updateChessboard();
            }
        }
    }
}

// 下完了一次，向服务器汇报一次局势
function updateChessboard() {
    // 发送棋盘去服务器
    // $.get("send_chessboard/?chessBox=" + chessBox.valueOf(), function (data, status) {
    //     // alert("ok");
    //
    // })
    $.ajax({
        url: 'send_chessboard',
        data: {"chessBox": JSON.stringify( chessBox)},
        dataType: "json",
        type: "POST",
        //traditional: true,
        success: function (data) {
            // your logic
            // alert('Ok');
        }
    });

}
