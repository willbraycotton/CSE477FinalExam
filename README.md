# CSE477FinalExam


The final exam for CSE 477, where I was tasked with creating a web application of a task management system like Trello.

Link to Web app (Hosted on Google Cloud):

https://exam-555867872511.us-central1.run.app/home



###  Authentication System
- **User Signup and Login**: Users can sign up with an email and password and log in to access the application interface.
- **Password Encryption**: All stored passwords are securely encrypted in the database.
- **Logout Functionality**: Users can log out to end their session.

### Project Board Management
- Board Selection: Upon first sign-in, users can either:
- Open an existing Board (display a list of Boards the user is part of).
- Create a new Board (input project name and add member emails).
- Board Access Control: Only authorized members can view or access a Board.

### Board Interface Features
- Default Lists: Each Board contains three default lists: "To Do," "Doing," and "Completed."
- Card Management:
  - Add Cards: Users can add new Cards to any list.
  - Edit Cards: Users can edit a Card's content after clicking an Edit button, which turns into a Save button during editing.
  - Delete Cards: Users can permanently delete Cards.
  - Card Movement: Cards can be dragged and dropped across lists.
  - Edit Locking: When one user is editing a Card, its position and content are locked for others.

### Real-Time Updates
- Live Synchronization: Changes to Boards, Lists, or Cards are reflected in real-time for all logged-in users without requiring manual page refreshes.
Persistent Storage
- Relational Database: Board states, including lists, cards, and user access data, are stored persistently, ensuring continuity across user sessions.

### Chat System
- Group Chat: A chat window on each Board page allows active members to communicate in real-time.
- Input Window: For typing and submitting messages.
- Display Window: For showing chat messages from all users.
- Chat Visibility: Only members currently logged into the same Board page can see and participate in the chat.


