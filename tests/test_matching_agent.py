from matching_agent import run_initial_agent, conversation_node

def test_initial_graph_returns_shortlist():
    state = run_initial_agent()
    assert len(state["candidate_shortlist"]) > 0
    assert state["candidate_shortlist"][0]["score"] >= 0

def test_compare_command():
    state = run_initial_agent()
    state["user_query"] = "Compare the top 3 matches side by side"
    state = conversation_node(state)
    assert "Candidate comparison:" in state["response"]

def test_requirement_refinement():
    state = run_initial_agent()
    state["user_query"] = "Add Python as a must-have"
    state = conversation_node(state)
    assert "Requirements updated" in state["response"]
    assert "Python" in state["job_requirements"]["must_have"]

def test_deep_and_final_rounds():
    state = run_initial_agent()
    state["user_query"] = "Run deep screening"
    state = conversation_node(state)
    assert state["screening_round"] == 2
    state["user_query"] = "Give hire/no-hire recommendations"
    state = conversation_node(state)
    assert state["screening_round"] == 3
    assert state["final_recommendations"]
