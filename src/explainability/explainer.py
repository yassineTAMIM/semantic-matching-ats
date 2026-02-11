"""
Explainability Module - Transparent AI decision making
Provides detailed score breakdowns and natural language explanations
"""

from typing import Dict, List
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))
from config import *


class ExplainabilityEngine:
    """
    Generate transparent explanations for matching scores
    """
    
    @staticmethod
    def generate_explanation(match: Dict) -> Dict:
        """
        Generate comprehensive explanation for a match
        
        Args:
            match: Match dictionary from MatchingEngine
            
        Returns:
            Dictionary with detailed explanations
        """
        candidate = match['candidate']
        scores = match['scores']
        breakdown = match['breakdown']
        
        explanation = {
            "summary": ExplainabilityEngine._generate_summary(candidate, scores),
            "score_components": ExplainabilityEngine._explain_score_components(scores, breakdown),
            "strengths": ExplainabilityEngine._identify_strengths(breakdown),
            "weaknesses": ExplainabilityEngine._identify_weaknesses(breakdown),
            "recommendation": ExplainabilityEngine._generate_recommendation(scores['total']),
            "detailed_analysis": breakdown
        }
        
        return explanation
    
    @staticmethod
    def _generate_summary(candidate: Dict, scores: Dict) -> str:
        """Generate high-level summary"""
        name = candidate.get('name', 'Candidate')
        title = candidate.get('current_title', 'Professional')
        total_score = scores['total']
        
        if total_score >= 0.85:
            quality = "excellent"
        elif total_score >= 0.75:
            quality = "strong"
        elif total_score >= 0.65:
            quality = "good"
        elif total_score >= 0.55:
            quality = "moderate"
        else:
            quality = "partial"
        
        summary = (
            f"{name} is a {title} with an overall match score of {total_score:.1%}, "
            f"indicating a {quality} fit for this position."
        )
        
        return summary
    
    @staticmethod
    def _explain_score_components(scores: Dict, breakdown: Dict) -> List[Dict]:
        """Explain each score component"""
        components = []
        
        # Semantic similarity
        semantic = breakdown['semantic_similarity']
        components.append({
            "name": "Semantic Match",
            "score": scores['semantic'],
            "weight": WEIGHTS['semantic'],
            "contribution": scores['semantic'] * WEIGHTS['semantic'],
            "explanation": (
                f"{semantic['interpretation']}. The candidate's profile shows strong semantic "
                f"alignment with the job requirements based on deep language understanding."
            )
        })
        
        # Skills match
        skills = breakdown['skills_match']
        matched = len(skills['matched_skills'])
        total_required = len(skills['matched_skills']) + len(skills['missing_skills'])
        
        components.append({
            "name": "Skills Match",
            "score": scores['skills'],
            "weight": WEIGHTS['skills'],
            "contribution": scores['skills'] * WEIGHTS['skills'],
            "explanation": (
                f"Candidate possesses {matched} out of {total_required} required skills "
                f"({matched/total_required:.0%} coverage)." if total_required > 0 else
                "No specific skills required for this position."
            )
        })
        
        # Experience match
        experience = breakdown['experience_match']
        components.append({
            "name": "Experience Match",
            "score": scores['experience'],
            "weight": WEIGHTS['experience'],
            "contribution": scores['experience'] * WEIGHTS['experience'],
            "explanation": (
                f"Candidate has {experience['candidate_years']} years of experience. "
                f"Position requires {experience['required_range']} years. "
                f"Status: {experience['status']}."
            )
        })
        
        # Location match
        location = breakdown['location_match']
        components.append({
            "name": "Location Match",
            "score": scores['location'],
            "weight": WEIGHTS['location'],
            "contribution": scores['location'] * WEIGHTS['location'],
            "explanation": (
                f"Candidate location ({location['candidate_location']}) vs. "
                f"job location ({location['job_location']})."
            )
        })
        
        return components
    
    @staticmethod
    def _identify_strengths(breakdown: Dict) -> List[str]:
        """Identify candidate's key strengths for this role"""
        strengths = []
        
        # Semantic strength
        semantic_score = breakdown['semantic_similarity']['score']
        if semantic_score >= 0.75:
            strengths.append(
                f"Exceptional semantic match ({semantic_score:.0%}) - profile aligns "
                f"closely with job requirements"
            )
        
        # Skills strengths
        matched_skills = breakdown['skills_match']['matched_skills']
        if len(matched_skills) >= 5:
            top_skills = ', '.join(matched_skills[:5])
            strengths.append(f"Strong skill set including: {top_skills}")
        elif len(matched_skills) >= 3:
            strengths.append(f"Relevant skills: {', '.join(matched_skills)}")
        
        # Experience strengths
        exp_score = breakdown['experience_match']['score']
        if exp_score >= 0.9:
            strengths.append(
                f"{breakdown['experience_match']['candidate_years']} years of highly "
                f"relevant experience"
            )
        
        # Location advantage
        loc_score = breakdown['location_match']['score']
        if loc_score >= 0.8:
            strengths.append("Location alignment or remote flexibility")
        
        return strengths if strengths else ["Profile shows general alignment with requirements"]
    
    @staticmethod
    def _identify_weaknesses(breakdown: Dict) -> List[str]:
        """Identify potential gaps or concerns"""
        weaknesses = []
        
        # Semantic weakness
        semantic_score = breakdown['semantic_similarity']['score']
        if semantic_score < 0.60:
            weaknesses.append(
                "Limited semantic alignment - profile may not fully match job context"
            )
        
        # Skills gaps
        missing_skills = breakdown['skills_match']['missing_skills']
        if len(missing_skills) > 0:
            if len(missing_skills) <= 3:
                weaknesses.append(f"Missing skills: {', '.join(missing_skills)}")
            else:
                weaknesses.append(
                    f"Missing {len(missing_skills)} required skills including: "
                    f"{', '.join(missing_skills[:3])}"
                )
        
        # Experience concerns
        exp_status = breakdown['experience_match']['status']
        exp_score = breakdown['experience_match']['score']
        if exp_score < 0.7:
            weaknesses.append(exp_status)
        
        # Location concern
        loc_score = breakdown['location_match']['score']
        if loc_score < 0.5:
            weaknesses.append("Location mismatch may require relocation or remote work arrangement")
        
        return weaknesses if weaknesses else ["No significant weaknesses identified"]
    
    @staticmethod
    def _generate_recommendation(total_score: float) -> Dict:
        """Generate hiring recommendation"""
        if total_score >= 0.85:
            decision = "STRONG RECOMMEND"
            rationale = "Excellent overall match. Candidate should be prioritized for interview."
            next_steps = ["Schedule interview immediately", "Prepare detailed technical assessment"]
        
        elif total_score >= 0.75:
            decision = "RECOMMEND"
            rationale = "Strong match across multiple criteria. Solid candidate worth pursuing."
            next_steps = ["Schedule phone screening", "Review portfolio/work samples"]
        
        elif total_score >= 0.65:
            decision = "CONSIDER"
            rationale = "Good potential match. Review in detail and compare with other candidates."
            next_steps = ["Detailed CV review", "Skills assessment", "Compare with shortlist"]
        
        elif total_score >= 0.55:
            decision = "MAYBE"
            rationale = "Moderate match. Consider if candidate pool is limited or specific strengths align."
            next_steps = ["Assess specific skill gaps", "Consider for different role"]
        
        else:
            decision = "NOT RECOMMENDED"
            rationale = "Insufficient match for this particular role."
            next_steps = ["Consider for other positions", "Keep in talent pool for future opportunities"]
        
        return {
            "decision": decision,
            "rationale": rationale,
            "confidence": total_score,
            "next_steps": next_steps
        }
    
    @staticmethod
    def generate_comparison_report(matches: List[Dict]) -> Dict:
        """
        Generate comparative analysis across multiple candidates
        
        Args:
            matches: List of match dictionaries
            
        Returns:
            Comparative analysis
        """
        if not matches:
            return {"error": "No matches to compare"}
        
        report = {
            "total_candidates": len(matches),
            "score_distribution": ExplainabilityEngine._analyze_score_distribution(matches),
            "top_candidates": ExplainabilityEngine._summarize_top_candidates(matches[:5]),
            "skill_coverage": ExplainabilityEngine._analyze_skill_coverage(matches),
            "insights": ExplainabilityEngine._generate_insights(matches)
        }
        
        return report
    
    @staticmethod
    def _analyze_score_distribution(matches: List[Dict]) -> Dict:
        """Analyze score distribution across candidates"""
        scores = [m['scores']['total'] for m in matches]
        
        return {
            "mean": sum(scores) / len(scores),
            "max": max(scores),
            "min": min(scores),
            "range": max(scores) - min(scores),
            "above_75": sum(1 for s in scores if s >= 0.75),
            "above_65": sum(1 for s in scores if s >= 0.65)
        }
    
    @staticmethod
    def _summarize_top_candidates(top_matches: List[Dict]) -> List[Dict]:
        """Summarize top candidates"""
        summaries = []
        
        for i, match in enumerate(top_matches, 1):
            candidate = match['candidate']
            scores = match['scores']
            
            summaries.append({
                "rank": i,
                "name": candidate['name'],
                "title": candidate['current_title'],
                "score": scores['total'],
                "key_strength": ExplainabilityEngine._get_top_strength(match)
            })
        
        return summaries
    
    @staticmethod
    def _get_top_strength(match: Dict) -> str:
        """Identify top strength for a candidate"""
        scores = match['scores']
        
        # Find highest weighted contribution
        contributions = {
            "semantic": scores['semantic'] * WEIGHTS['semantic'],
            "skills": scores['skills'] * WEIGHTS['skills'],
            "experience": scores['experience'] * WEIGHTS['experience'],
            "location": scores['location'] * WEIGHTS['location']
        }
        
        top_component = max(contributions, key=contributions.get)
        
        strength_map = {
            "semantic": "Exceptional profile alignment",
            "skills": "Strong skill match",
            "experience": "Ideal experience level",
            "location": "Perfect location fit"
        }
        
        return strength_map.get(top_component, "Overall strong fit")
    
    @staticmethod
    def _analyze_skill_coverage(matches: List[Dict]) -> Dict:
        """Analyze skill coverage across candidates"""
        all_matched_skills = []
        all_missing_skills = []
        
        for match in matches[:10]:  # Top 10
            breakdown = match['breakdown']
            all_matched_skills.extend(breakdown['skills_match']['matched_skills'])
            all_missing_skills.extend(breakdown['skills_match']['missing_skills'])
        
        # Count frequencies
        from collections import Counter
        matched_freq = Counter(all_matched_skills)
        missing_freq = Counter(all_missing_skills)
        
        return {
            "most_common_skills": matched_freq.most_common(5),
            "commonly_missing": missing_freq.most_common(5)
        }
    
    @staticmethod
    def _generate_insights(matches: List[Dict]) -> List[str]:
        """Generate actionable insights"""
        insights = []
        
        if not matches:
            return ["No candidates available for analysis"]
        
        # Score quality insight
        avg_score = sum(m['scores']['total'] for m in matches) / len(matches)
        if avg_score >= 0.75:
            insights.append("Strong candidate pool with high average match scores")
        elif avg_score >= 0.65:
            insights.append("Moderate candidate quality - consider broadening search criteria")
        else:
            insights.append("Limited match quality - may need to adjust job requirements or search parameters")
        
        # Skills insight
        skill_scores = [m['scores']['skills'] for m in matches]
        avg_skill_score = sum(skill_scores) / len(skill_scores)
        
        if avg_skill_score < 0.5:
            insights.append("Low skill match across candidates - consider skills training programs or adjusted requirements")
        
        # Experience insight
        exp_scores = [m['scores']['experience'] for m in matches]
        avg_exp_score = sum(exp_scores) / len(exp_scores)
        
        if avg_exp_score < 0.6:
            insights.append("Experience mismatch - consider adjusting required years of experience")
        
        return insights


def main():
    """Test explainability engine"""
    # This would typically be called from the matching engine
    print("Explainability Engine loaded successfully")
    print("Use generate_explanation() with match results from MatchingEngine")


if __name__ == "__main__":
    main()
