
# 🎓 IITU AI Assistant - Student Forum & Access Logic

## 1. Core Philosophy: "Collective Knowledge"
Instead of isolated private chats, the platform functions as a **Knowledge Forum**. Questions asked by one student become an instant resource for all others.

## 2. User Roles & Permissions

### A. Unregistered Users (Guests)
*   **Rights**: Read-Only + Logical Search.
*   **Capabilities**:
    *   Can view the "Course Card".
    *   Can browse the full history of previous Q&A in that course.
    *   **Action**: Can type in the search bar.
        *   **Mechanism**: The input is NOT sent to the LLM.
        *   **Logic**: System performs a **Semantic Search** against the *Historical Q&A Database*.
        *   **Result**: Returns the most relevant previously answered question. If no match is found, prompts them to "Login to Ask AI".
*   **Data Privacy**: Cannot see *who* asked the questions.

### B. Registered Students
*   **Rights**: Read + Write (Ask AI).
*   **Capabilities**:
    *   All Guest capabilities.
    *   **Action**: Can type a new question.
        *   **Mechanism**: Request is processed by the **RAG Engine + LLM**.
        *   **Result**: Generates a new answer from course materials.
    *   **Persistence**: The Q&A pair is saved to the Global Course History for everyone to see.

### C. Teachers & Admins
*   **Rights**: Superview.
*   **Capabilities**:
    *   Can see the full history.
    *   **Identity Reveal**: Can see exactly *which student* (`user_id`, `name`) asked a specific question.
    *   Can moderate/delete questions.

## 3. Data Architecture (Backend)

### Global Chat Storage (SQLite)
Moved from Client-Side (Dexie) to Server-Side (SQLite) to enable sharing.

| Field | Type | Description |
| :--- | :--- | :--- |
| `id` | INTEGER | Primary Key |
| `course_id` | TEXT | Links to specific course |
| `user_id` | TEXT | ID of the asker |
| `user_name` | TEXT | Name of asker (Hidden from students) |
| `question` | TEXT | The prompt |
| `answer` | TEXT | The AI Usage |
| `timestamp` | REAL | Time of Q&A |
| `embedding` | BLOB | (Optional) Vector of question for fast semantic search |

## 4. Workflows

### Scenario 1: Guest Search
1.  Guest types: "When is the exam?"
2.  Backend receives request (No Auth Token).
3.  Backend embeds query -> Searches `chat_messages` vector space.
4.  Found match found (Similiary > 0.8): "Midterm is on Oct 10th".
5.  Return: Cached Answer.

### Scenario 2: Student Ask
1.  Student types: "Explain Quantum Entanglement".
2.  Backend receives request (Has Auth Token).
3.  Backend runs RAG (Search VectorDB -> Generate with Qwen).
4.  Backend saves Q&A to `chat_messages`.
5.  Frontend updates Live Feed for all connected users.
