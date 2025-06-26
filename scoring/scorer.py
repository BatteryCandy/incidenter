"""
Scoring System for Incidenter
Evaluates player performance and provides detailed feedback
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import timedelta
from enum import Enum


class ScoreCategory(Enum):
    """Categories for scoring different aspects of performance"""

    INVESTIGATION_TECHNIQUE = "investigation_technique"
    EVIDENCE_ANALYSIS = "evidence_analysis"
    THEORY_ACCURACY = "theory_accuracy"
    TIME_EFFICIENCY = "time_efficiency"
    COMPLETENESS = "completeness"
    METHODOLOGY = "methodology"


@dataclass
class ScoreBreakdown:
    """Detailed breakdown of scoring"""

    category: ScoreCategory
    points_earned: int
    points_possible: int
    feedback: str
    details: List[str] = field(default_factory=list)

    @property
    def percentage(self) -> float:
        """Calculate percentage score for this category"""
        if self.points_possible == 0:
            return 0.0
        return (self.points_earned / self.points_possible) * 100


@dataclass
class GameScore:
    """Complete scoring results for a game session"""

    total_points: int
    possible_points: int
    percentage: float
    grade: str
    breakdowns: List[ScoreBreakdown]
    overall_feedback: str
    strengths: List[str] = field(default_factory=list)
    improvements: List[str] = field(default_factory=list)
    time_taken: Optional[timedelta] = None
    efficiency_rating: str = "Average"


class IncidenterScorer:
    """Main scoring engine for Incidenter scenarios"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # Scoring weights for different categories
        self.category_weights = {
            ScoreCategory.INVESTIGATION_TECHNIQUE: 0.25,
            ScoreCategory.EVIDENCE_ANALYSIS: 0.20,
            ScoreCategory.THEORY_ACCURACY: 0.30,
            ScoreCategory.TIME_EFFICIENCY: 0.10,
            ScoreCategory.COMPLETENESS: 0.10,
            ScoreCategory.METHODOLOGY: 0.05,
        }

        # Grade thresholds
        self.grade_thresholds = {
            90: "A+",
            85: "A",
            80: "A-",
            75: "B+",
            70: "B",
            65: "B-",
            60: "C+",
            55: "C",
            50: "C-",
            45: "D+",
            40: "D",
            0: "F",
        }

    def score_game_session(
        self,
        scenario_data: Dict[str, Any],
        session_data: Dict[str, Any],
        facilitator_evaluations: List[Dict[str, Any]] = None,
    ) -> GameScore:
        """
        Score a complete game session

        Args:
            scenario_data: The scenario definition
            session_data: Player actions and responses during the session
            facilitator_evaluations: AI facilitator's evaluations during the game

        Returns:
            Complete GameScore with detailed breakdown
        """
        breakdowns = []

        # Score each category
        breakdowns.append(
            self._score_investigation_technique(scenario_data, session_data)
        )
        breakdowns.append(self._score_evidence_analysis(scenario_data, session_data))
        breakdowns.append(
            self._score_theory_accuracy(
                scenario_data, session_data, facilitator_evaluations
            )
        )
        breakdowns.append(self._score_time_efficiency(scenario_data, session_data))
        breakdowns.append(self._score_completeness(scenario_data, session_data))
        breakdowns.append(self._score_methodology(scenario_data, session_data))

        # Calculate weighted total
        total_points = 0
        possible_points = 0

        for breakdown in breakdowns:
            weight = self.category_weights[breakdown.category]
            weighted_points = breakdown.points_earned * weight
            weighted_possible = breakdown.points_possible * weight

            total_points += weighted_points
            possible_points += weighted_possible

        percentage = (
            (total_points / possible_points * 100) if possible_points > 0 else 0
        )
        grade = self._calculate_grade(percentage)

        # Generate overall feedback and recommendations
        overall_feedback, strengths, improvements = self._generate_overall_feedback(
            breakdowns, percentage
        )

        # Calculate time efficiency rating
        time_taken = session_data.get("total_time")
        efficiency_rating = self._calculate_efficiency_rating(
            time_taken, scenario_data.get("estimated_duration")
        )

        return GameScore(
            total_points=int(total_points),
            possible_points=int(possible_points),
            percentage=round(percentage, 1),
            grade=grade,
            breakdowns=breakdowns,
            overall_feedback=overall_feedback,
            strengths=strengths,
            improvements=improvements,
            time_taken=time_taken,
            efficiency_rating=efficiency_rating,
        )

    def _score_investigation_technique(
        self, scenario_data: Dict, session_data: Dict
    ) -> ScoreBreakdown:
        """Score investigation methodology and techniques used"""
        points_possible = 100
        points_earned = 0
        details = []

        actions = session_data.get("investigation_actions", [])

        # Check for systematic approach
        if len(actions) >= 5:
            points_earned += 20
            details.append("Conducted thorough investigation with multiple actions")
        elif len(actions) >= 3:
            points_earned += 15
            details.append("Performed adequate number of investigation actions")
        else:
            details.append("Limited investigation actions taken")

        # Check for diverse investigation types
        action_types = set()
        for action in actions:
            action_type = action.get("action", "").lower()
            if any(term in action_type for term in ["log", "network", "forensic"]):
                action_types.add("technical")
            elif any(term in action_type for term in ["interview", "question", "ask"]):
                action_types.add("human")
            elif any(term in action_type for term in ["timeline", "sequence", "order"]):
                action_types.add("temporal")

        diversity_score = min(len(action_types) * 15, 30)
        points_earned += diversity_score
        if diversity_score > 0:
            details.append(
                f"Used {len(action_types)} different investigation approaches"
            )

        # Check for logical progression
        if self._check_logical_progression(actions):
            points_earned += 25
            details.append("Demonstrated logical investigation progression")
        else:
            details.append("Investigation could benefit from more systematic approach")

        # Check for evidence-based decisions
        evidence_based_actions = sum(
            1
            for action in actions
            if action.get("details", "").lower().find("evidence") != -1
            or action.get("details", "").lower().find("based on") != -1
        )

        if evidence_based_actions >= 2:
            points_earned += 25
            details.append("Made evidence-based investigation decisions")
        elif evidence_based_actions >= 1:
            points_earned += 15
            details.append("Some evidence-based decision making observed")
        else:
            details.append("Could improve by making more evidence-based decisions")

        feedback = f"Investigation technique score: {points_earned}/{points_possible}. " + (
            "Strong systematic approach demonstrated."
            if points_earned >= 70
            else (
                "Good investigation skills with room for improvement."
                if points_earned >= 50
                else "Consider developing more systematic investigation methodology."
            )
        )

        return ScoreBreakdown(
            category=ScoreCategory.INVESTIGATION_TECHNIQUE,
            points_earned=points_earned,
            points_possible=points_possible,
            feedback=feedback,
            details=details,
        )

    def _score_evidence_analysis(
        self, scenario_data: Dict, session_data: Dict
    ) -> ScoreBreakdown:
        """Score how well evidence was analyzed and utilized"""
        points_possible = 100
        points_earned = 0
        details = []

        evidence_discovered = session_data.get("evidence_discovered", [])
        total_evidence = len(scenario_data.get("evidence", {}).get("items", []))

        # Points for evidence discovery
        if total_evidence > 0:
            discovery_rate = len(evidence_discovered) / total_evidence
            discovery_points = int(discovery_rate * 40)
            points_earned += discovery_points
            details.append(
                f"Discovered {len(evidence_discovered)}/{total_evidence} pieces of evidence"
            )

        # Points for evidence correlation
        correlations = session_data.get("evidence_correlations", [])
        correlation_points = min(len(correlations) * 15, 30)
        points_earned += correlation_points
        if correlations:
            details.append(
                f"Successfully correlated {len(correlations)} pieces of evidence"
            )

        # Points for evidence interpretation
        interpretations = session_data.get("evidence_interpretations", [])
        interpretation_points = min(len(interpretations) * 10, 30)
        points_earned += interpretation_points
        if interpretations:
            details.append(f"Provided {len(interpretations)} evidence interpretations")

        feedback = f"Evidence analysis score: {points_earned}/{points_possible}. " + (
            "Excellent evidence discovery and analysis."
            if points_earned >= 70
            else (
                "Good evidence handling with room for deeper analysis."
                if points_earned >= 50
                else "Focus on discovering and analyzing more evidence systematically."
            )
        )

        return ScoreBreakdown(
            category=ScoreCategory.EVIDENCE_ANALYSIS,
            points_earned=points_earned,
            points_possible=points_possible,
            feedback=feedback,
            details=details,
        )

    def _score_theory_accuracy(
        self,
        scenario_data: Dict,
        session_data: Dict,
        facilitator_evaluations: List[Dict] = None,
    ) -> ScoreBreakdown:
        """Score accuracy of theories submitted"""
        points_possible = 100
        points_earned = 0
        details = []

        theories = session_data.get("theories_submitted", [])
        scenario_solution = scenario_data.get("solution", {})

        if not theories:
            feedback = "No theories submitted for evaluation."
            return ScoreBreakdown(
                category=ScoreCategory.THEORY_ACCURACY,
                points_earned=0,
                points_possible=points_possible,
                feedback=feedback,
                details=["No theories submitted"],
            )

        # Score each theory
        theory_scores = []
        for theory in theories:
            theory_score = self._evaluate_theory_accuracy(theory, scenario_solution)
            theory_scores.append(theory_score)
            details.append(f"Theory accuracy: {theory_score}%")

        # Use best theory score (allows for iteration and improvement)
        best_theory_score = max(theory_scores) if theory_scores else 0
        points_earned = int(best_theory_score)

        # Bonus points for multiple reasonable theories (shows thorough thinking)
        if len([score for score in theory_scores if score >= 60]) > 1:
            points_earned += 10
            details.append("Bonus: Multiple viable theories developed")

        # Cap at maximum possible
        points_earned = min(points_earned, points_possible)

        feedback = f"Theory accuracy score: {points_earned}/{points_possible}. " + (
            "Excellent understanding of the incident."
            if points_earned >= 80
            else (
                "Good grasp of the incident with minor gaps."
                if points_earned >= 60
                else "Theory needs refinement - consider reviewing evidence more carefully."
            )
        )

        return ScoreBreakdown(
            category=ScoreCategory.THEORY_ACCURACY,
            points_earned=points_earned,
            points_possible=points_possible,
            feedback=feedback,
            details=details,
        )

    def _score_time_efficiency(
        self, scenario_data: Dict, session_data: Dict
    ) -> ScoreBreakdown:
        """Score time efficiency compared to expected duration"""
        points_possible = 100
        points_earned = 50  # Default/baseline score
        details = []

        actual_time = session_data.get("total_time")
        expected_time = scenario_data.get("estimated_duration", 3600)  # Default 1 hour

        if actual_time:
            if isinstance(actual_time, (int, float)):
                time_ratio = actual_time / expected_time
            else:
                # Handle timedelta objects
                time_ratio = actual_time.total_seconds() / expected_time

            if time_ratio <= 0.8:
                points_earned = 100
                details.append("Completed significantly faster than expected")
            elif time_ratio <= 1.0:
                points_earned = 85
                details.append("Completed within expected timeframe")
            elif time_ratio <= 1.2:
                points_earned = 70
                details.append("Took slightly longer than expected")
            elif time_ratio <= 1.5:
                points_earned = 50
                details.append("Took moderately longer than expected")
            else:
                points_earned = 25
                details.append("Took significantly longer than expected")
        else:
            details.append("Time tracking not available")

        feedback = f"Time efficiency score: {points_earned}/{points_possible}. " + (
            "Excellent time management."
            if points_earned >= 85
            else (
                "Good time management."
                if points_earned >= 70
                else "Consider more efficient investigation strategies."
            )
        )

        return ScoreBreakdown(
            category=ScoreCategory.TIME_EFFICIENCY,
            points_earned=points_earned,
            points_possible=points_possible,
            feedback=feedback,
            details=details,
        )

    def _score_completeness(
        self, scenario_data: Dict, session_data: Dict
    ) -> ScoreBreakdown:
        """Score completeness of investigation"""
        points_possible = 100
        points_earned = 0
        details = []

        # Check coverage of key areas
        required_areas = scenario_data.get("required_investigation_areas", [])
        covered_areas = session_data.get("areas_investigated", [])

        if required_areas:
            coverage_rate = len(set(covered_areas) & set(required_areas)) / len(
                required_areas
            )
            points_earned += int(coverage_rate * 60)
            details.append(
                f"Covered {len(set(covered_areas) & set(required_areas))}"
                f"/{len(required_areas)} required areas"
            )
        else:
            # Fallback scoring based on action diversity
            actions = session_data.get("investigation_actions", [])
            if len(actions) >= 8:
                points_earned += 60
            elif len(actions) >= 5:
                points_earned += 40
            elif len(actions) >= 3:
                points_earned += 25
            details.append(f"Performed {len(actions)} investigation actions")

        # Check if all major evidence was discovered
        evidence_items = scenario_data.get("evidence", {}).get("items", [])
        critical_evidence = [
            e for e in evidence_items if e.get("importance", "medium") == "critical"
        ]
        discovered_critical = session_data.get("critical_evidence_found", [])

        if critical_evidence:
            critical_rate = len(discovered_critical) / len(critical_evidence)
            points_earned += int(critical_rate * 40)
            details.append(
                f"Found {len(discovered_critical)}/{len(critical_evidence)} critical evidence items"
            )
        else:
            points_earned += 40  # Give full points if no critical evidence defined

        feedback = f"Completeness score: {points_earned}/{points_possible}. " + (
            "Thorough and complete investigation."
            if points_earned >= 80
            else (
                "Good coverage with some areas missed."
                if points_earned >= 60
                else "Investigation needs to be more comprehensive."
            )
        )

        return ScoreBreakdown(
            category=ScoreCategory.COMPLETENESS,
            points_earned=points_earned,
            points_possible=points_possible,
            feedback=feedback,
            details=details,
        )

    def _score_methodology(
        self, scenario_data: Dict, session_data: Dict
    ) -> ScoreBreakdown:
        """Score adherence to incident response methodology"""
        points_possible = 100
        points_earned = 0
        details = []

        actions = session_data.get("investigation_actions", [])

        # Check for proper IR phases (NIST or similar)
        phases_covered = set()

        for action in actions:
            action_text = (
                action.get("action", "").lower()
                + " "
                + action.get("details", "").lower()
            )

            if any(term in action_text for term in ["identify", "detect", "alert"]):
                phases_covered.add("identification")
            elif any(term in action_text for term in ["contain", "isolate", "block"]):
                phases_covered.add("containment")
            elif any(term in action_text for term in ["eradicate", "remove", "clean"]):
                phases_covered.add("eradication")
            elif any(term in action_text for term in ["recover", "restore", "resume"]):
                phases_covered.add("recovery")
            elif any(term in action_text for term in ["lesson", "review", "improve"]):
                phases_covered.add("lessons_learned")

        # Award points for methodology coverage
        methodology_points = len(phases_covered) * 20
        points_earned += methodology_points
        details.append(f"Covered {len(phases_covered)} IR methodology phases")

        # Check for documentation habits
        documented_actions = sum(
            1 for action in actions if len(action.get("details", "")) > 20
        )
        if documented_actions >= len(actions) * 0.8:
            points_earned += 20
            details.append("Excellent documentation of actions")
        elif documented_actions >= len(actions) * 0.5:
            points_earned += 10
            details.append("Good documentation practices")

        feedback = f"Methodology score: {points_earned}/{points_possible}. " + (
            "Strong adherence to IR methodology."
            if points_earned >= 70
            else (
                "Good methodology with room for improvement."
                if points_earned >= 50
                else "Consider following established IR frameworks more closely."
            )
        )

        return ScoreBreakdown(
            category=ScoreCategory.METHODOLOGY,
            points_earned=points_earned,
            points_possible=points_possible,
            feedback=feedback,
            details=details,
        )

    def _check_logical_progression(self, actions: List[Dict]) -> bool:
        """Check if investigation actions follow logical progression"""
        if len(actions) < 3:
            return False

        # Simple heuristic: early actions should be broader, later actions more specific
        early_actions = actions[: len(actions) // 2]
        later_actions = actions[len(actions) // 2 :]  # noqa E203

        early_specificity = self._calculate_action_specificity(early_actions)
        later_specificity = self._calculate_action_specificity(later_actions)

        return later_specificity > early_specificity

    def _calculate_action_specificity(self, actions: List[Dict]) -> float:
        """Calculate specificity score for a set of actions"""
        if not actions:
            return 0

        specificity_keywords = [
            "specific",
            "detailed",
            "exact",
            "particular",
            "precise",
        ]
        general_keywords = ["overview", "general", "broad", "initial", "scan"]

        total_specificity = 0
        for action in actions:
            text = (action.get("action", "") + " " + action.get("details", "")).lower()

            specific_count = sum(
                1 for keyword in specificity_keywords if keyword in text
            )
            general_count = sum(1 for keyword in general_keywords if keyword in text)

            # Base specificity on keyword balance and detail length
            specificity = (
                specific_count - general_count + len(action.get("details", "")) / 100
            )
            total_specificity += specificity

        return total_specificity / len(actions)

    def _evaluate_theory_accuracy(self, theory: Dict, solution: Dict) -> float:
        """Evaluate how accurate a theory is against the solution"""
        theory_text = theory.get("theory", "").lower()

        # Extract key solution elements
        attack_type = solution.get("attack_type", "").lower()
        attack_vector = solution.get("attack_vector", "").lower()
        key_indicators = [
            indicator.lower() for indicator in solution.get("key_indicators", [])
        ]

        accuracy_score = 0

        # Check attack type accuracy
        if attack_type and attack_type in theory_text:
            accuracy_score += 30

        # Check attack vector accuracy
        if attack_vector and attack_vector in theory_text:
            accuracy_score += 25

        # Check key indicators
        indicators_found = sum(
            1 for indicator in key_indicators if indicator in theory_text
        )
        if key_indicators:
            accuracy_score += (indicators_found / len(key_indicators)) * 30

        # Check for common theory elements
        theory_elements = ["timeline", "motivation", "impact", "technique"]
        elements_mentioned = sum(
            1 for element in theory_elements if element in theory_text
        )
        accuracy_score += (elements_mentioned / len(theory_elements)) * 15

        return min(accuracy_score, 100)

    def _calculate_grade(self, percentage: float) -> str:
        """Convert percentage to letter grade"""
        for threshold, grade in self.grade_thresholds.items():
            if percentage >= threshold:
                return grade
        return "F"

    def _calculate_efficiency_rating(self, actual_time, expected_time) -> str:
        """Calculate efficiency rating based on time comparison"""
        if not actual_time or not expected_time:
            return "Unknown"

        if isinstance(actual_time, timedelta):
            actual_seconds = actual_time.total_seconds()
        else:
            actual_seconds = actual_time

        ratio = actual_seconds / expected_time

        if ratio <= 0.7:
            return "Excellent"
        elif ratio <= 0.9:
            return "Very Good"
        elif ratio <= 1.1:
            return "Good"
        elif ratio <= 1.3:
            return "Average"
        elif ratio <= 1.5:
            return "Below Average"
        else:
            return "Needs Improvement"

    def _generate_overall_feedback(
        self, breakdowns: List[ScoreBreakdown], percentage: float
    ) -> Tuple[str, List[str], List[str]]:
        """Generate overall feedback, strengths, and improvement suggestions"""
        strengths = []
        improvements = []

        # Identify strengths (categories scoring >= 75%)
        for breakdown in breakdowns:
            if breakdown.percentage >= 75:
                strengths.append(f"Strong {breakdown.category.value.replace('_', ' ')}")

        # Identify improvement areas (categories scoring < 60%)
        for breakdown in breakdowns:
            if breakdown.percentage < 60:
                improvements.append(
                    f"Improve {breakdown.category.value.replace('_', ' ')}"
                )

        # Generate overall feedback
        if percentage >= 85:
            overall = (
                "Excellent performance! You demonstrated strong incident "
                "response skills across all areas."
            )
        elif percentage >= 75:
            overall = (
                "Good performance with solid incident response fundamentals. "
                "Some areas for refinement identified."
            )
        elif percentage >= 65:
            overall = (
                "Satisfactory performance. Focus on the identified improvement "
                "areas to enhance your IR skills."
            )
        elif percentage >= 50:
            overall = (
                "Basic incident response skills demonstrated. Significant "
                "improvement needed in multiple areas."
            )
        else:
            overall = (
                "Performance indicates need for additional training in "
                "incident response fundamentals."
            )

        return overall, strengths, improvements

    def score_theory(self, theory_record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Score a player's theory submission

        Args:
            theory_record: Dictionary containing theory data and game context

        Returns:
            Dictionary with scoring results for display
        """
        theory = theory_record["theory"]

        # Extract basic metrics
        theory_completeness = self._assess_theory_completeness(theory)
        theory_accuracy = self._assess_theory_plausibility(theory)

        # Calculate scores for each component
        max_component_score = 100  # noqa F841
        components = {
            "initial_access": 20,
            "techniques_used": 20,
            "timeline": 15,
            "objective": 15,
            "attribution": 10,
            "impact": 10,
            "additional_iocs": 10,
        }

        total_score = 0
        max_possible_score = sum(components.values())
        component_scores = {}

        for component, max_points in components.items():
            if component in theory and theory[component].strip():
                # Score based on length and detail
                response_length = len(theory[component])
                if response_length > 50:  # Detailed response
                    score = int(max_points * 0.9)
                elif response_length > 20:  # Moderate response
                    score = int(max_points * 0.7)
                else:  # Brief response
                    score = int(max_points * 0.5)
            else:
                score = 0

            component_scores[component] = score
            total_score += score  # Calculate percentage and grade
        percentage = (total_score / max_possible_score) * 100
        grade = self._calculate_grade(percentage)

        # Determine performance level
        if percentage >= 90:
            performance_level = "Outstanding"
        elif percentage >= 80:
            performance_level = "Excellent"
        elif percentage >= 70:
            performance_level = "Good"
        elif percentage >= 60:
            performance_level = "Satisfactory"
        else:
            performance_level = "Needs Improvement"

        # Format category scores for display
        category_scores = []
        for component, score in component_scores.items():
            max_points = components[component]
            category_scores.append(
                {
                    "category": component.replace("_", " ").title(),
                    "earned_points": score,
                    "max_points": max_points,
                    "feedback": (
                        "Good detail provided"
                        if score > max_points * 0.7
                        else "Could use more detail"
                    ),
                }
            )

        # Generate feedback
        feedback = self._generate_theory_feedback(theory, component_scores, percentage)

        return {
            "total_score": total_score,
            "max_possible_score": max_possible_score,
            "percentage": percentage,
            "grade": grade,
            "performance_level": performance_level,
            "component_scores": component_scores,
            "category_scores": category_scores,
            "feedback": feedback,
            "completeness": theory_completeness,
            "accuracy_assessment": theory_accuracy,
        }

    def _assess_theory_completeness(self, theory: Dict[str, str]) -> float:
        """Assess how complete the theory is (0.0 to 1.0)"""
        required_components = [
            "initial_access",
            "techniques_used",
            "timeline",
            "objective",
        ]
        completed = sum(
            1 for comp in required_components if comp in theory and theory[comp].strip()
        )
        return completed / len(required_components)

    def _assess_theory_plausibility(self, theory: Dict[str, str]) -> str:
        """Assess the plausibility of the theory"""
        # Simple heuristic based on response detail
        total_length = sum(len(str(value)) for value in theory.values())
        if total_length > 500:
            return "Highly detailed analysis"
        elif total_length > 200:
            return "Good level of detail"
        else:
            return "Basic analysis provided"

    def _generate_theory_feedback(
        self, theory: Dict[str, str], scores: Dict[str, int], percentage: float
    ) -> str:
        """Generate feedback for the theory submission"""
        if percentage >= 85:
            overall = "Excellent analysis! Your theory demonstrates strong understanding of the incident."
        elif percentage >= 70:
            overall = (
                "Good analysis with solid reasoning. Some areas could use more detail."
            )
        elif percentage >= 55:
            overall = "Reasonable analysis, but several areas need more investigation."
        else:
            overall = "Basic analysis provided. Consider gathering more evidence before forming conclusions."

        # Identify strongest and weakest areas
        if scores:
            best_component = max(scores.items(), key=lambda x: x[1])
            worst_component = min(scores.items(), key=lambda x: x[1])

            feedback = f"{overall}\n\n"
            feedback += f"Strongest area: {best_component[0].replace('_', ' ').title()} ({best_component[1]} points)\n"
            if worst_component[1] < best_component[1]:
                feedback += f"Area for improvement: {worst_component[0].replace('_', ' ').title()}\n"

            return feedback

        return overall


def create_score_report(score: GameScore, scenario_name: str = "") -> str:
    """Create a formatted text report of the scoring results"""
    report = []
    report.append("=" * 60)
    report.append("INCIDENTER PERFORMANCE REPORT")
    if scenario_name:
        report.append(f"Scenario: {scenario_name}")
    report.append("=" * 60)
    report.append("")

    # Overall score
    report.append(
        f"Overall Score: {score.total_points}/{score.possible_points} "
        f"({score.percentage}%) - Grade: {score.grade}"
    )
    if score.time_taken:
        report.append(f"Time Efficiency: {score.efficiency_rating}")
    report.append("")

    # Category breakdown
    report.append("CATEGORY BREAKDOWN:")
    report.append("-" * 40)
    for breakdown in score.breakdowns:
        category_name = breakdown.category.value.replace("_", " ").title()
        report.append(
            f"{category_name}: {breakdown.points_earned}/{breakdown.points_possible} ({breakdown.percentage:.1f}%)"
        )
        report.append(f"  {breakdown.feedback}")
        for detail in breakdown.details:
            report.append(f"  • {detail}")
        report.append("")

    # Overall feedback
    report.append("OVERALL FEEDBACK:")
    report.append("-" * 40)
    report.append(score.overall_feedback)
    report.append("")

    # Strengths
    if score.strengths:
        report.append("STRENGTHS:")
        for strength in score.strengths:
            report.append(f"✓ {strength}")
        report.append("")

    # Improvements
    if score.improvements:
        report.append("AREAS FOR IMPROVEMENT:")
        for improvement in score.improvements:
            report.append(f"→ {improvement}")
        report.append("")

    report.append("=" * 60)

    return "\n".join(report)
