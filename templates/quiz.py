import random

# Dictionary to store questions and answers
quiz_data = {
    "What is the largest primate in Indonesia?": ["Sumatran Orangutan", "orangutan"],
    "Which species of turtle is critically endangered in Indonesia?": ["Leatherback Turtle", "leatherback"],
    "What is the national animal of Indonesia?": ["Javan Hawk-Eagle", "hawk-eagle"],
    "Which big cat is found in Sumatra and is critically endangered?": ["Sumatran Tiger", "tiger"],
    "What is the world's rarest rhinoceros, found in Indonesia?": ["Javan Rhino", "rhino"],
}

def ask_question(question, correct_answer):
    user_answer = input(question + " ").lower()
    return user_answer == correct_answer

def quiz():
    print("Welcome to the Endangered Indonesian Animals Quiz!\n")
    score = 0

    # Shuffle the questions
    questions = list(quiz_data.keys())
    random.shuffle(questions)

    for question in questions:
        correct_answer = quiz_data[question][0].lower()
        if ask_question(question, correct_answer):
            print("Correct!\n")
            score += 1
        else:
            print(f"Wrong! The correct answer is {quiz_data[question][0]}.\n")

    print(f"Quiz completed! Your score is {score}/{len(quiz_data)}.")

if __name__ == "__main__":
    quiz()
