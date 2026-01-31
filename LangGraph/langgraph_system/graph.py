"""
LangGraph Workflow Definition
전체 노드 연결 및 제어 흐름 정의(Graph)
"""
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver  # Checkpointer 추가
from langgraph_system.state import BrandConsultingState, create_initial_state

# Import Nodes
from langgraph_system.nodes.diagnosis_node import diagnosis_node
from langgraph_system.nodes.naming_node import naming_node
from langgraph_system.nodes.concept_node import concept_node
from langgraph_system.nodes.story_node import story_node
from langgraph_system.nodes.logo_node import logo_node
from langgraph_system.nodes.quality_check_node import quality_check_node
from langgraph_system.nodes.human_review_node import human_review_node

def route_step(state: BrandConsultingState) -> str:
    """
    라우터 함수: 현재 상태에 따라 다음 실행할 노드를 결정
    """
    current_step = state.get("current_step")
    regenerate_step = state.get("regenerate_step")
    
    # 1. 재생성 요청이 있는 경우 해당 단계로 되돌아감
    if regenerate_step is not None:
        step_mapping = {
            1: "diagnosis",
            2: "naming",
            3: "concept",
            4: "story",
            5: "logo"
        }
        target_node = step_mapping.get(regenerate_step)
        if target_node:
            print(f"[Router] 🔄 재생성 모드: Step {regenerate_step} ({target_node})로 이동")
            return target_node
    
    # 2. 일반 진행 (current_step 기준)
    # Human Review에서 승인 시 current_step이 이미 다음 단계로 업데이트 되어 있음
    step_mapping = {
        1: "diagnosis",
        2: "naming",
        3: "concept",
        4: "story",
        5: "logo",
        6: END  # Step 5 완료 후 +1 되면 6 -> 종료
    }
    
    next_node = step_mapping.get(current_step)
    
    if next_node:
        print(f"[Router] ➡️  다음 단계: Step {current_step} ({next_node})")
        return next_node
    else:
        print(f"[Router] 🏁 워크플로우 종료 (Step {current_step})")
        return END

def create_info_graph():
    """
    LangGraph StateGraph 생성 및 컴파일
    """
    workflow = StateGraph(BrandConsultingState)
    
    # 1. 노드 추가
    workflow.add_node("diagnosis", diagnosis_node)
    workflow.add_node("naming", naming_node)
    workflow.add_node("concept", concept_node)
    workflow.add_node("story", story_node)
    workflow.add_node("logo", logo_node)
    
    workflow.add_node("quality_check", quality_check_node)
    workflow.add_node("human_review", human_review_node)
    
    # 2. 엣지 연결
    # 각 단계 노드 완료 후 -> Quality Check
    step_nodes = ["diagnosis", "naming", "concept", "story", "logo"]
    for node in step_nodes:
        workflow.add_edge(node, "quality_check")
    
    # Quality Check -> Human Review
    workflow.add_edge("quality_check", "human_review")
    
    # Human Review -> Router (Conditional Edge)
    # Human Review 결과에 따라 다음 단계로 갈지, 이전 단계로 갈지 결정
    workflow.add_conditional_edges(
        "human_review",
        route_step
    )
    
    # 3. 시작점 설정
    workflow.set_entry_point("diagnosis")
    
    # 4. 컴파일 (Checkpointer 설정 추가)
    memory = MemorySaver()
    app = workflow.compile(
        checkpointer=memory,
        interrupt_before=["human_review"]
    )
    
    return app
