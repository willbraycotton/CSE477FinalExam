document.addEventListener('DOMContentLoaded', function() {
    const createBoardBtn = document.getElementById('create-board-btn');
    const newBoardForm = document.getElementById('new-board-form');
    const existingBoardForm = document.getElementById('old-board-form');
    const openExistingBtn = document.getElementById('open-existing-btn');
    const existingBoardList = document.createElement('ul');
    existingBoardForm.appendChild(existingBoardList);

    createBoardBtn.addEventListener('click', function() {
        newBoardForm.style.display = 'block';
        existingBoardForm.style.display = 'none';
    });

    openExistingBtn.addEventListener('click', function() {
        existingBoardForm.style.display = 'block';
        newBoardForm.style.display = 'none';
        fetchUserBoards();
        console.log('fetching user boards');
    });

    const newSubmitBtn = document.getElementById('new-submit-board');
    newSubmitBtn.addEventListener('click', function() {
        submitBoard('new');
    });

    const existingSubmitBtn = document.getElementById('existing-submit-board');
    existingSubmitBtn.addEventListener('click', function() {
        submitBoard('existing');
    });

    function submitBoard(type) {
        const boardName = document.getElementById(`${type}-board-name`).value.trim();
        const boardMembers = document.getElementById(`${type}-board-members`).value.trim();
        if (boardName) {
            createBoard(boardName, boardMembers.split(','), type);
        } else {
            alert("Please fill out both the project name and member emails.");
        }
    }

    function createBoard(boardName, boardMembers) {
        fetch('/create_board', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name: boardName,
                members: boardMembers
            })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            if (data.board_id) {
                window.location.href = `/board/${data.board_id}`;
            } else {
                console.error('Failed to create board:', data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }

    function fetchUserBoards() {
        fetch('/user_boards')
        .then(response => response.json())
        .then(boards => {
            existingBoardList.innerHTML = '';
            boards.forEach(board => {
                const listItem = document.createElement('li');
                const link = document.createElement('a');
                link.href = `/board/${board.board_id}`;
                link.textContent = board.name;
                listItem.appendChild(link);
                existingBoardList.appendChild(listItem);
            });
        })
        .catch(error => {
            console.error('Error fetching user boards:', error);
        });
    }
});
