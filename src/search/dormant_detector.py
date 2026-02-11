"""
Dormant Talent Detector - Automatically rediscover qualified past candidates
Unique innovation: identifies candidates who applied months/years ago and may have evolved
"""

import json
from datetime import datetime, timedelta
from typing import List, Dict
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent.parent))
from config import *
from src.search.matching_engine import MatchingEngine


class DormantTalentDetector:
    """
    Detect and alert on dormant candidates who are now relevant for new positions
    """
    
    def __init__(self, matching_engine: MatchingEngine = None):
        """Initialize dormant talent detector"""
        print("Initializing Dormant Talent Detector...")
        
        self.matching_engine = matching_engine or MatchingEngine()
        
        # Load all candidates
        with open(CV_DATA_FILE, 'r', encoding='utf-8') as f:
            self.all_candidates = json.load(f)
        
        # Filter dormant candidates
        self.dormant_candidates = [
            c for c in self.all_candidates if c.get('is_dormant', False)
        ]
        
        print(f"✅ Found {len(self.dormant_candidates)} dormant candidates (out of {len(self.all_candidates)} total)")
    
    def detect_dormant_matches(self, job: Dict, min_score: float = DORMANT_MIN_SCORE) -> List[Dict]:
        """
        Detect dormant candidates who match a new job posting
        
        Args:
            job: Job dictionary
            min_score: Minimum matching score to trigger alert
            
        Returns:
            List of dormant candidate matches with evolution scores
        """
        print(f"\n{'='*60}")
        print(f"Scanning dormant candidates for: {job['title']}")
        print(f"{'='*60}")
        
        # Get dormant candidate IDs for filtering
        dormant_ids = {c['id'] for c in self.dormant_candidates}
        
        # Run matching on full pool, then filter to dormant only
        all_matches = self.matching_engine.match_candidates(
            job, 
            top_k=min(len(self.dormant_candidates), 100),
            filters=None
        )
        
        # Filter to only dormant candidates
        dormant_matches = []
        
        for match in all_matches:
            candidate_id = match['candidate']['id']
            
            # Skip if not dormant
            if candidate_id not in dormant_ids:
                continue
            
            # Only process if score is above threshold
            if match['scores']['total'] >= min_score:
                # Calculate evolution score
                evolution_data = self._calculate_evolution_score(match['candidate'], job)
                
                # Add evolution data to match
                match['evolution'] = evolution_data
                match['is_dormant_alert'] = True
                
                # Adjust total score with evolution bonus
                match['scores']['evolution'] = evolution_data['score']
                match['scores']['total_with_evolution'] = (
                    match['scores']['total'] + 
                    DORMANT_EVOLUTION_WEIGHT * evolution_data['score']
                )
                
                dormant_matches.append(match)
        
        # Sort by total score with evolution
        dormant_matches.sort(
            key=lambda x: x['scores']['total_with_evolution'], 
            reverse=True
        )
        
        print(f"✅ Found {len(dormant_matches)} dormant candidates above threshold ({min_score:.2f})")
        
        return dormant_matches
    
    def _calculate_evolution_score(self, candidate: Dict, job: Dict) -> Dict:
        """
        Calculate evolution score based on how long candidate has been dormant
        Hypothesis: longer dormant period = more likely to have gained experience
        
        Args:
            candidate: Candidate dictionary
            job: Job dictionary
            
        Returns:
            Dictionary with evolution score and metadata
        """
        # Calculate months dormant
        last_app_date = datetime.strptime(candidate['last_application_date'], '%Y-%m-%d')
        months_dormant = (datetime.now() - last_app_date).days / 30
        
        # Evolution score increases with time dormant (up to a maximum)
        # Formula: min(months_dormant / 24, 1.0)  -> caps at 2 years
        raw_score = min(months_dormant / 24, 1.0)
        
        # Apply scaling factor
        evolution_score = raw_score * 0.5  # Max evolution score is 0.5
        
        # Generate evolution narrative
        narrative = self._generate_evolution_narrative(
            candidate, job, months_dormant, evolution_score
        )
        
        return {
            "score": evolution_score,
            "months_dormant": int(months_dormant),
            "last_application": candidate['last_application_date'],
            "original_title": candidate['current_title'],
            "new_opportunity": job['title'],
            "narrative": narrative,
            "growth_potential": self._assess_growth_potential(months_dormant, candidate, job)
        }
    
    def _generate_evolution_narrative(self, candidate: Dict, job: Dict, 
                                     months_dormant: float, evolution_score: float) -> str:
        """Generate human-readable evolution narrative"""
        
        months_int = int(months_dormant)
        
        if months_int >= 24:
            time_phrase = f"over {months_int // 12} years ago"
        elif months_int >= 12:
            time_phrase = f"{months_int // 12} year{'s' if months_int >= 24 else ''} ago"
        else:
            time_phrase = f"{months_int} months ago"
        
        narrative = (
            f"{candidate['name']} applied {time_phrase} as a {candidate['current_title']}. "
            f"Given this time period, they may have gained {months_int // 12} year(s) of additional experience "
            f"and developed new skills relevant to the {job['title']} position."
        )
        
        return narrative
    
    def _assess_growth_potential(self, months_dormant: float, 
                                 candidate: Dict, job: Dict) -> str:
        """Assess potential growth during dormant period"""
        
        years_dormant = months_dormant / 12
        
        if years_dormant >= 2:
            return "HIGH - Significant time for skill development and career progression"
        elif years_dormant >= 1:
            return "MEDIUM - Reasonable time for professional growth"
        elif years_dormant >= 0.5:
            return "MODERATE - Some potential for skill enhancement"
        else:
            return "LOW - Short dormant period"
    
    def generate_alert_summary(self, dormant_matches: List[Dict]) -> Dict:
        """
        Generate summary of dormant talent alerts
        
        Args:
            dormant_matches: List of dormant candidate matches
            
        Returns:
            Summary dictionary
        """
        if not dormant_matches:
            return {
                "total_alerts": 0,
                "message": "No dormant candidates match this position"
            }
        
        # Calculate statistics
        avg_months_dormant = sum(m['evolution']['months_dormant'] for m in dormant_matches) / len(dormant_matches)
        avg_match_score = sum(m['scores']['total'] for m in dormant_matches) / len(dormant_matches)
        
        # Group by growth potential
        growth_distribution = {}
        for match in dormant_matches:
            potential = match['evolution']['growth_potential']
            growth_distribution[potential] = growth_distribution.get(potential, 0) + 1
        
        summary = {
            "total_alerts": len(dormant_matches),
            "avg_months_dormant": round(avg_months_dormant, 1),
            "avg_match_score": round(avg_match_score, 3),
            "growth_distribution": growth_distribution,
            "top_candidate": {
                "name": dormant_matches[0]['candidate']['name'],
                "score": round(dormant_matches[0]['scores']['total_with_evolution'], 3),
                "months_dormant": dormant_matches[0]['evolution']['months_dormant']
            },
            "message": f"Found {len(dormant_matches)} dormant candidates who may have evolved to match this role"
        }
        
        return summary
    
    def create_alert_notifications(self, dormant_matches: List[Dict], job: Dict) -> List[Dict]:
        """
        Create notification objects for dormant talent alerts
        
        Args:
            dormant_matches: List of dormant matches
            job: Job dictionary
            
        Returns:
            List of notification dictionaries
        """
        notifications = []
        
        for match in dormant_matches[:10]:  # Top 10 alerts
            candidate = match['candidate']
            evolution = match['evolution']
            scores = match['scores']
            
            notification = {
                "type": "DORMANT_TALENT_ALERT",
                "priority": self._calculate_priority(scores['total_with_evolution']),
                "job_id": job['id'],
                "job_title": job['title'],
                "candidate_id": candidate['id'],
                "candidate_name": candidate['name'],
                "match_score": scores['total'],
                "evolution_score": evolution['score'],
                "total_score": scores['total_with_evolution'],
                "months_dormant": evolution['months_dormant'],
                "message": f"Dormant talent alert: {candidate['name']} (applied {evolution['months_dormant']} months ago) is a {int(scores['total_with_evolution'] * 100)}% match for {job['title']}",
                "narrative": evolution['narrative'],
                "timestamp": datetime.now().isoformat()
            }
            
            notifications.append(notification)
        
        return notifications
    
    def _calculate_priority(self, total_score: float) -> str:
        """Calculate alert priority based on score"""
        if total_score >= 0.9:
            return "CRITICAL"
        elif total_score >= 0.8:
            return "HIGH"
        elif total_score >= 0.75:
            return "MEDIUM"
        else:
            return "LOW"


def main():
    """Main execution function for testing"""
    print("="*60)
    print("DORMANT TALENT DETECTOR TEST")
    print("="*60)
    
    # Load a sample job
    with open(JOB_DATA_FILE, 'r', encoding='utf-8') as f:
        jobs = json.load(f)
    
    test_job = jobs[2]  # Third job as test
    
    # Initialize detector
    detector = DormantTalentDetector()
    
    # Detect dormant matches
    dormant_matches = detector.detect_dormant_matches(test_job, min_score=0.70)
    
    # Generate summary
    summary = detector.generate_alert_summary(dormant_matches)
    
    # Create notifications
    notifications = detector.create_alert_notifications(dormant_matches, test_job)
    
    # Display results
    print(f"\n{'='*60}")
    print(f"DORMANT TALENT ALERTS FOR: {test_job['title']}")
    print(f"{'='*60}")
    print(f"\nSummary:")
    print(f"  Total Alerts: {summary['total_alerts']}")
    print(f"  Avg Months Dormant: {summary['avg_months_dormant']}")
    print(f"  Avg Match Score: {summary['avg_match_score']:.3f}")
    
    if dormant_matches:
        print(f"\n  Top Candidate: {summary['top_candidate']['name']}")
        print(f"    Score: {summary['top_candidate']['score']:.3f}")
        print(f"    Dormant: {summary['top_candidate']['months_dormant']} months")
        
        print(f"\n{'='*60}")
        print("TOP 5 DORMANT CANDIDATES:")
        print(f"{'='*60}")
        
        for i, match in enumerate(dormant_matches[:5], 1):
            candidate = match['candidate']
            scores = match['scores']
            evolution = match['evolution']
            
            print(f"\n{i}. {candidate['name']} - {candidate['current_title']}")
            print(f"   Match Score: {scores['total']:.3f}")
            print(f"   Evolution Bonus: +{scores['evolution']:.3f}")
            print(f"   Total with Evolution: {scores['total_with_evolution']:.3f}")
            print(f"   Dormant: {evolution['months_dormant']} months")
            print(f"   Growth Potential: {evolution['growth_potential']}")
            print(f"   Narrative: {evolution['narrative']}")


if __name__ == "__main__":
    main()