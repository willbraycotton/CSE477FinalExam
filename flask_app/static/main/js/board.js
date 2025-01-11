var socket1;
$(document).ready(function(){
    socket1 = io.connect('https://' + document.domain + ':' + location.port + '/board');
    socket1.on('connect', function() {
        const boardId = document.getElementById('board-id').value;
        socket1.emit('joined', {board_id: boardId});
    });


    socket1.on('displayaddcard', function(data) {
        const card_html = data.card_html;
        const column = data.list;
        const cardItem = document.createElement('li');
        cardItem.className = 'card-item';
        cardItem.setAttribute('data-id', data.card_id);
        cardItem.innerHTML = card_html;
        document.getElementById(`${column}-list`).appendChild(cardItem);
    

    });

    socket1.on('displaydeletecard', function(data){
        var cardId = data.card_id;
        const cardItem = document.querySelector(`.card-item[data-id="${cardId}"]`);
        if (cardItem) {
            cardItem.remove();
        }
    });

    socket1.on('cardlocked', function(data) {
        const cardId = data.card_id;
        const cardItem1 = document.querySelector(`.card-item[data-id="${cardId}"]`);
        cardItem1.classList.add('locked');
    });

    socket1.on('cardunlocked', function(data) {
        const cardId = data.card_id;
        const cardItem = document.querySelector(`.card-item[data-id="${cardId}"]`);
        if (cardItem) {
            //cardItem.classList.remove('locked');
            const editButton = cardItem.querySelector('button[onclick^="editCard"]');
            const saveButton = cardItem.querySelector('button[onclick^="saveCard"]');
            editButton.disabled = false;
            saveButton.disabled = false;
        }
    });

    socket1.on('test', function(data){
    });


});



document.addEventListener('DOMContentLoaded', function() {



    function showAddCardForm(column) {
        document.getElementById(`add-card-form-${column}`).style.display = 'block';
    }

    function addCard(event, column) {
        event.preventDefault();
        const cardName = document.getElementById(`new-card-name-${column}`).value.trim();
        const boardId = document.getElementById('board-id').value;
        if (cardName && boardId) {
            socket1.emit('addcard', {name: cardName, list: column, board_id: boardId});
        }
    }

    function deleteCard(cardId) {
        socket1.emit('deletecard', {card_id: cardId});;
    }

    function editCard(cardId) {
        const boardId = document.getElementById('board-id').value;
        //socket1.emit('test', {card_id: cardId});
        socket1.emit('lockcard', { card_id: cardId, board_id: boardId }, function(response) {
            if (response.status === 'failed'){
                return;
            }
            else{
                const cardId = response.card_id;
                //socket1.emit('cardlocked', { card_id: cardId}, broadcast= true);
                const cardNameInput = document.getElementById(`card-name-${cardId}`);
                cardNameInput.removeAttribute('readonly');
                cardNameInput.focus();
                cardNameInput.addEventListener('keydown', function(event) {
                    if (event.key === 'Enter') {
                        saveCard(cardId);
                    }
                });
                const cardItem = cardNameInput.closest('.card-item');
                const editButton = cardItem.querySelector('button[onclick^="editCard"]');
                const saveButton = cardItem.querySelector('button[onclick^="saveCard"]');
        
                editButton.style.display = 'none';
                saveButton.style.display = 'inline-block';
                
            }
        });

        
        

    }

    function saveCard(cardId) {
        const cardNameInput = document.getElementById(`card-name-${cardId}`);
        const cardName = cardNameInput.value.trim();
        const boardId = document.getElementById('board-id').value;

        const cardItem = document.querySelector(`.card-item[data-id="${cardId}"]`);
        const listColumn = cardItem.parentElement.getAttribute('id').replace('-list', '');

        if (cardName) {
            socket1.emit('updatecard', {card_id: cardId, card_name: cardName, board_id: boardId, list: listColumn});

            cardNameInput.setAttribute('readonly', 'readonly');
            const cardItem = cardNameInput.closest('.card-item');
            const editButton = cardItem.querySelector('button[onclick^="editCard"]');
            const saveButton = cardItem.querySelector('button[onclick^="saveCard"]');
            editButton.style.display = 'inline-block';
            saveButton.style.display = 'none';

            socket1.emit('unlockcard', { card_id: cardId });
        }
    }

    var todoList = document.getElementById('todo-list');
    var doingList = document.getElementById('doing-list');
    var completedList = document.getElementById('completed-list');

    function handleCardMove(evt) {
        var cardId = evt.item.getAttribute('data-id');
        var newList = evt.to.getAttribute('id').replace('-list', '');
        var boardId = document.getElementById('board-id').value;
        var cardName = document.getElementById(`card-name-${cardId}`).value.trim();

        socket1.emit('updatecardlist', {card_id: cardId , new_list: newList, board_id: boardId, card_name: cardName});;
    }

    var sortableTodo = Sortable.create(todoList, {
        group: 'cards',
        animation: 150,
        filter: '.locked',
        onMove: function (evt) {
            return !evt.related.classList.contains('locked'); // Prevent dragging of locked cards
        },
        onEnd: handleCardMove
    });

    var sortableDoing = Sortable.create(doingList, {
        group: 'cards',
        animation: 150,
        filter: '.locked',
        onMove: function (evt) {
            return !evt.related.classList.contains('locked'); // Prevent dragging of locked cards
        },
        onEnd: handleCardMove
    });

    var sortableDone = Sortable.create(completedList, {
        group: 'cards',
        animation: 150,
        filter: '.locked',
        onMove: function (evt) {
            return !evt.related.classList.contains('locked'); // Prevent dragging of locked cards
        },
        onEnd: handleCardMove
    });

    window.showAddCardForm = showAddCardForm;
    window.addCard = addCard;
    window.deleteCard = deleteCard;
    window.editCard = editCard;
    window.saveCard = saveCard;
});
