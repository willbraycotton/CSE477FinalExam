var socket;
$(document).ready(function(){
    socket = io.connect('https://' + document.domain + ':' + location.port + '/chat');
    socket.on('connect', function() {
        const boardId = document.getElementById('board-id').value;
        socket.emit('joined', {board_id: boardId});
    });

    socket.on('status', function(data) {
        let tag = document.createElement("p");
        let text = document.createTextNode(data.msg);
        let element = document.getElementById("chat");
        tag.appendChild(text);
        tag.style.cssText = data.style;
        element.appendChild(tag);
        $('#chat').scrollTop($('#chat')[0].scrollHeight);
    });

    const display = document.getElementById('user-message');
    display.addEventListener('keypress', (event) => {
        if (event.key === 'Enter') {
            const message = display.value.trim();
            if (message) {
                const boardId = document.getElementById('board-id').value;
                socket.emit('displaymessage', {message: message, board_id: boardId});
                display.value = '';
            }
        }
    });
});

