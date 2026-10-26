import random

# question_bank[topic][difficulty] -> list of questions
QUESTION_BANK = {
    "JavaScript": {
        "Easy": [
            "What is the difference between 'var', 'let', and 'const'?",
            "Explain what 'NaN' means in JavaScript.",
            "What is the difference between '==' and '==='?",
        ],
        "Medium": [
            "Explain closures in JavaScript with an example.",
            "What is event delegation and why is it useful?",
            "Explain how the 'this' keyword behaves in different contexts.",
        ],
        "Hard": [
            "Explain the JavaScript event loop and how microtasks/macrotasks are handled.",
            "How would you implement a debounce function from scratch?",
            "Explain prototypal inheritance and how it differs from classical inheritance.",
        ],
    },
    "React": {
        "Easy": [
            "What is JSX and why is it used?",
            "What is the difference between props and state?",
            "What is a functional component?",
        ],
        "Medium": [
            "Explain the useEffect hook and its dependency array.",
            "How does React's virtual DOM improve performance?",
            "What is prop drilling and how can it be avoided?",
        ],
        "Hard": [
            "Explain how React's reconciliation algorithm works.",
            "How would you optimize a large React app that is re-rendering too often?",
            "Explain the difference between useMemo and useCallback with examples.",
        ],
    },
    "Python": {
        "Easy": [
            "What is the difference between a list and a tuple in Python?",
            "What are Python decorators, in simple terms?",
            "Explain the difference between '==' and 'is'.",
        ],
        "Medium": [
            "Explain list comprehensions and give an example.",
            "What is the Global Interpreter Lock (GIL)?",
            "How does exception handling work in Python (try/except/finally)?",
        ],
        "Hard": [
            "Explain how Python's garbage collection works.",
            "How would you implement a custom context manager?",
            "Explain the difference between multithreading and multiprocessing in Python.",
        ],
    },
    "SQL": {
        "Easy": [
            "What is the difference between WHERE and HAVING?",
            "What is a primary key vs a foreign key?",
            "Write a query to select all employees earning more than 50000.",
        ],
        "Medium": [
            "Explain the different types of SQL joins.",
            "What is normalization and why is it important?",
            "What is the difference between DELETE, TRUNCATE, and DROP?",
        ],
        "Hard": [
            "Explain how indexes improve query performance and their trade-offs.",
            "Write a query to find the second-highest salary without using LIMIT/TOP.",
            "Explain ACID properties in the context of transactions.",
        ],
    },
    "DBMS": {
        "Easy": [
            "What is a database management system?",
            "What is the difference between a DBMS and RDBMS?",
            "What is a schema?",
        ],
        "Medium": [
            "Explain the different normal forms (1NF, 2NF, 3NF).",
            "What is a deadlock and how can it be prevented?",
            "Explain the difference between clustered and non-clustered indexes.",
        ],
        "Hard": [
            "Explain the CAP theorem and its implications for distributed databases.",
            "How does two-phase locking ensure serializability?",
            "Explain the differences between OLTP and OLAP systems.",
        ],
    },
    "OOP": {
        "Easy": [
            "What are the four pillars of object-oriented programming?",
            "What is the difference between a class and an object?",
            "What is method overloading?",
        ],
        "Medium": [
            "Explain the difference between abstraction and encapsulation.",
            "What is polymorphism, and what are its types?",
            "What is the difference between an interface and an abstract class?",
        ],
        "Hard": [
            "Explain the SOLID principles with brief examples.",
            "What is the diamond problem in multiple inheritance and how is it resolved?",
            "Explain composition vs inheritance and when to prefer each.",
        ],
    },
    "Operating Systems": {
        "Easy": [
            "What is the difference between a process and a thread?",
            "What is virtual memory?",
            "What is a system call?",
        ],
        "Medium": [
            "Explain the difference between paging and segmentation.",
            "What is a race condition and how can it be avoided?",
            "Explain the producer-consumer problem.",
        ],
        "Hard": [
            "Explain different CPU scheduling algorithms and their trade-offs.",
            "How does a operating system handle deadlock detection and recovery?",
            "Explain the difference between preemptive and non-preemptive kernels.",
        ],
    },
    "DSA": {
        "Easy": [
            "What is the time complexity of binary search?",
            "Explain the difference between a stack and a queue.",
            "What is a linked list, and when would you use one over an array?",
        ],
        "Medium": [
            "Explain how a hash table handles collisions.",
            "What is the difference between BFS and DFS?",
            "Explain how merge sort works and its time complexity.",
        ],
        "Hard": [
            "Explain how a balanced binary search tree (e.g. AVL/Red-Black) stays balanced.",
            "How would you detect a cycle in a directed graph?",
            "Explain dynamic programming with an example (e.g. 0/1 knapsack).",
        ],
    },
    "HR": {
        "Easy": [
            "Tell me about yourself.",
            "Why do you want to work at this company?",
            "What are your strengths and weaknesses?",
        ],
        "Medium": [
            "Describe a time you faced a conflict in a team and how you resolved it.",
            "Where do you see yourself in five years?",
            "Describe a challenging project and how you overcame the difficulties.",
        ],
        "Hard": [
            "Tell me about a time you failed. What did you learn from it?",
            "How do you handle receiving critical feedback?",
            "Describe a situation where you had to make a decision with incomplete information.",
        ],
    },
}

ROLES = [
    "Software Developer",
    "Frontend Developer",
    "Backend Developer",
    "Data Analyst",
]

TOPICS = list(QUESTION_BANK.keys())
DIFFICULTIES = ["Easy", "Medium", "Hard"]


def get_random_question(topic, difficulty):
    bank = QUESTION_BANK.get(topic, {}).get(difficulty)
    if not bank:
        # Reasonable fallback if an unexpected topic/difficulty combination is requested
        return f"Explain a key concept in {topic} that every {difficulty.lower()}-level candidate should know."
    return random.choice(bank)


def evaluate_answer_rule_based(question, answer):
    """A simple heuristic evaluator used when the AI API is unavailable."""
    answer = (answer or "").strip()
    word_count = len(answer.split())

    strengths = []
    improvements = []

    if word_count == 0:
        return {
            "score": 0,
            "strengths": [],
            "improvements": ["No answer was submitted. Try to always attempt an answer, even a partial one."],
        }

    score = 30

    if word_count >= 40:
        score += 25
        strengths.append("Answer is reasonably detailed.")
    elif word_count >= 15:
        score += 15
        strengths.append("Answer covers the basics.")
    else:
        improvements.append("Try to elaborate further with more detail and examples.")

    has_example = any(w in answer.lower() for w in ["example", "for instance", "e.g.", "such as"])
    if has_example:
        score += 20
        strengths.append("Answer includes a concrete example.")
    else:
        improvements.append("Support your answer with a concrete example where possible.")

    has_structure = any(w in answer.lower() for w in ["first", "second", "then", "finally", "because"])
    if has_structure:
        score += 15
        strengths.append("Answer is logically structured.")
    else:
        improvements.append("Structure your answer clearly, e.g. explain the concept, then give an example.")

    score = max(0, min(100, score))

    if not strengths:
        strengths.append("You attempted the question, which is a good starting point.")
    if not improvements:
        improvements.append("Keep practicing to build confidence and speed.")

    return {"score": score, "strengths": strengths, "improvements": improvements}
