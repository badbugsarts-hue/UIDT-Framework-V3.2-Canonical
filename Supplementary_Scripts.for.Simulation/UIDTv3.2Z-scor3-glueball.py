# Z-Score Analyse der Simulationsergebnisse
def calculate_evidence_strength(z_scores):
    """
    Bewertet empirische Evidenz basierend auf Z-Scores
    """
    strong_evidence = sum(1 for z in z_scores if z < 2.0)
    moderate_evidence = sum(1 for z in z_scores if 2.0 <= z < 3.0)
    weak_evidence = sum(1 for z in z_scores if z >= 3.0)
    
    total_simulations = len(z_scores)
    
    print("📊 EMPIRISCHE EVIDENZ-ANALYSE")
    print("=" * 50)
    print(f"Starke Evidenz (Z < 2σ): {strong_evidence}/{total_simulations} ({strong_evidence/total_simulations*100:.1f}%)")
    print(f"Moderate Evidenz (2σ ≤ Z < 3σ): {moderate_evidence}/{total_simulations} ({moderate_evidence/total_simulations*100:.1f}%)")
    print(f"Schwache Evidenz (Z ≥ 3σ): {weak_evidence}/{total_simulations} ({weak_evidence/total_simulations*100:.1f}%)")
    
    # Wissenschaftliche Bewertung
    if strong_evidence / total_simulations >= 0.8:
        return "HOHE EVIDENZ", "Theorie zeigt konsistente Übereinstimmung"
    elif strong_evidence / total_simulations >= 0.6:
        return "MODERATE EVIDENZ", "Vielversprechende Hinweise, weitere Tests nötig"
    else:
        return "GERINGE EVIDENZ", "Keine robuste empirische Unterstützung"

# Simulierte Z-Scores aus verschiedenen Simulationen
z_scores_simulated = [1.2, 1.8, 2.5, 1.1, 3.2, 1.7, 2.1, 1.4, 2.8, 1.6]
evidence_level, interpretation = calculate_evidence_strength(z_scores_simulated)