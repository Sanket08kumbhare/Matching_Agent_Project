from matching_agent import run_initial_agent, conversation_node

def main():
    state = run_initial_agent()
    print("=" * 70)
    print("MATCHING AGENT — LangGraph Resume Screening")
    print("=" * 70)
    print(state["report"]["summary"])
    print("\nTop matches:")
    for row in state["report"]["top_candidates"]:
        print(
            f"{row['rank']:>2}. {row['name']:<20} {row['score']:>6}/100 | "
            f"Strengths: {', '.join(row['strengths'][:4]) or 'None'}"
        )

    print("\nTry:")
    print("  Find me candidates with React and 3+ years experience")
    print("  Compare the top 3 matches side by side")
    print("  Why did John rank higher than Jane?")
    print("  Add Python as a must-have")
    print("  Make API testing a nice-to-have")
    print("  Run deep screening")
    print("  Give hire/no-hire recommendations")
    print("  quit")

    while True:
        try:
            query = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break
        if query.lower() in {"quit", "exit", "q"}:
            print("Goodbye.")
            break
        if not query:
            continue
        state["user_query"] = query
        state = conversation_node(state)
        print("\nAgent:")
        print(state.get("response", "No response."))

if __name__ == "__main__":
    main()
