from graphviz import Digraph

def create_emoji_diagram():
    # Use a directed graph with smooth spline curves
    dot = Digraph('Nyaya_Mitra_Visual', format='png')
    dot.attr(rankdir='LR', size='12,6', splines='spline', nodesep='0.8', ranksep='1.2')

    # Global node settings for a softer, more visual look
    dot.attr('node', shape='box', style='rounded,filled', fontname='Arial', fontsize='14', margin='0.3,0.3')
    dot.attr('edge', fontname='Arial', fontsize='12', color='#555555', penwidth='1.5')

    # --- 1. External Input ---
    dot.node('User', '👤 User Query\n"Section 318 BNS"', fillcolor='#E3F2FD', color='#90CAF9', penwidth='2')

    # --- 2. Agentic Core Cluster ---
    with dot.subgraph(name='cluster_agent') as core:
        core.attr(label='🤖 Nyaya-Mitra Agentic Core', style='rounded,dashed', color='#BDBDBD', bgcolor='#FAFAFA', fontname='Arial', fontsize='16')

        # Explorer (Hybrid Search)
        core.node('Explorer', '🕵️‍♂️ Explorer Module\n(ChromaDB + BM25)', fillcolor='#E8F5E9', color='#81C784', penwidth='2')

        # Verifier
        core.node('Verifier', '🛡️ Deep Verifier\n(Regex & Math Check)', fillcolor='#FFF9C4', color='#FFF176', penwidth='2')

        # Memory
        core.node('Memory', '📚 Statutory Memory\n(BNS 2023)', shape='cylinder', fillcolor='#F3E5F5', color='#BA68C8', penwidth='2')

        # Internal Reasoning Loop
        with core.subgraph(name='cluster_loop') as loop:
            loop.attr(label='🔄 Verification Loop', style='rounded,dotted', color='#9E9E9E', bgcolor='#FFFFFF')
            loop.node('Retrieve', '📥 1. Retrieve Context', shape='ellipse', fillcolor='#E1F5FE', color='#29B6F6')
            loop.node('Check', '⚖️ 2. Fact Check Law', shape='ellipse', fillcolor='#E8F5E9', color='#66BB6A')
            loop.node('Draft', '✍️ 3. LLM Draft', shape='ellipse', fillcolor='#FFF3E0', color='#FFA726')

    # --- 3. Output ---
    dot.node('Output', '📜 Verified Legal Advice\n(Zero Hallucination)', fillcolor='#E8EAF6', color='#7986CB', penwidth='2')

    # --- Edges / Routing ---
    dot.edge('User', 'Explorer', label=' Query Input')

    dot.edge('Explorer', 'Memory', label=' Search Context', dir='both')
    dot.edge('Explorer', 'Retrieve', label=' Raw Data')

    dot.edge('Retrieve', 'Check')
    dot.edge('Check', 'Draft')
    dot.edge('Draft', 'Verifier', label=' Propose Draft')

    # The Hallucination check / Self-Correction (Red, thick, dashed)
    dot.edge('Verifier', 'Explorer', label=' ❌ Hallucination Detected\n(Re-explore)', color='#EF5350', fontcolor='#EF5350', style='dashed', penwidth='2')

    # Success Route (Green, thick)
    dot.edge('Verifier', 'Output', label=' ✅ Pass', color='#66BB6A', fontcolor='#2E7D32', penwidth='2.5')

    # Render and open the file
    dot.render('Nyaya_Mitra_Visual_Diagram', view=True)
    print("Visual Emoji Diagram generated as Nyaya_Mitra_Visual_Diagram.png")

if __name__ == "__main__":
    create_emoji_diagram()
