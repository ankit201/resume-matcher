"""
ROI Calculator
Calculate return on investment for switching from current vendor.
Critical for CFO decision-making.
"""

from typing import Dict, Optional
from dataclasses import dataclass


@dataclass
class VendorComparison:
    """Comparison between baseline vendor and our solution"""
    baseline_annual_cost: float
    our_annual_cost: float
    annual_savings: float
    savings_percentage: float
    payback_period_months: float
    three_year_savings: float
    five_year_savings: float


class ROICalculator:
    """
    Calculate ROI and cost comparisons for executive decision-making.
    """
    
    def __init__(
        self,
        baseline_vendor_annual_cost: float = 2_000_000,
        baseline_false_rejection_rate: float = 0.40,
        baseline_time_to_shortlist_days: int = 21
    ):
        """
        Initialize ROI calculator with baseline metrics.
        
        Args:
            baseline_vendor_annual_cost: Current vendor cost
            baseline_false_rejection_rate: Current false rejection rate
            baseline_time_to_shortlist_days: Current time to shortlist
        """
        self.baseline_cost = baseline_vendor_annual_cost
        self.baseline_false_rejection = baseline_false_rejection_rate
        self.baseline_time = baseline_time_to_shortlist_days
    
    def calculate_direct_cost_savings(
        self,
        avg_cost_per_candidate: float,
        annual_candidate_volume: int = 250_000
    ) -> Dict[str, float]:
        """
        Calculate direct cost savings from switching vendors.
        
        Args:
            avg_cost_per_candidate: Our cost per candidate
            annual_candidate_volume: Expected annual candidates
        
        Returns:
            Dictionary with cost analysis
        """
        our_annual_cost = avg_cost_per_candidate * annual_candidate_volume
        annual_savings = self.baseline_cost - our_annual_cost
        savings_percentage = (annual_savings / self.baseline_cost) * 100
        
        return {
            "baseline_annual_cost": self.baseline_cost,
            "our_annual_cost": our_annual_cost,
            "annual_savings": annual_savings,
            "savings_percentage": savings_percentage,
            "monthly_savings": annual_savings / 12,
            "cost_per_candidate_baseline": self.baseline_cost / annual_candidate_volume,
            "cost_per_candidate_ours": avg_cost_per_candidate,
            "cost_reduction_per_candidate": (self.baseline_cost / annual_candidate_volume) - avg_cost_per_candidate
        }
    
    def calculate_quality_cost_savings(
        self,
        our_false_rejection_rate: float,
        avg_cost_per_hire: float = 5_000,
        annual_hires: int = 5_000
    ) -> Dict[str, float]:
        """
        Calculate cost savings from improved quality (fewer false rejections).
        False rejections mean missing qualified candidates = delayed hiring = lost productivity.
        
        Args:
            our_false_rejection_rate: Our false rejection rate
            avg_cost_per_hire: Average cost per hire
            annual_hires: Annual hiring volume
        
        Returns:
            Dictionary with quality-related savings
        """
        # Calculate candidates needed to achieve hire goals
        # If we reject 40% of qualified candidates, we need to source more
        baseline_candidates_needed = annual_hires / (1 - self.baseline_false_rejection)
        our_candidates_needed = annual_hires / (1 - our_false_rejection_rate)
        
        # Fewer candidates needed = sourcing cost savings
        candidate_reduction = baseline_candidates_needed - our_candidates_needed
        sourcing_cost_per_candidate = 50  # Approximate cost to source one candidate
        sourcing_savings = candidate_reduction * sourcing_cost_per_candidate
        
        # Time-to-hire impact
        # Fewer false rejections = faster hiring = less lost productivity
        days_saved_per_hire = 7  # Approximate days saved per hire
        productivity_cost_per_day = 500  # Lost productivity cost
        productivity_savings = annual_hires * days_saved_per_hire * productivity_cost_per_day
        
        total_quality_savings = sourcing_savings + productivity_savings
        
        return {
            "false_rejection_improvement": self.baseline_false_rejection - our_false_rejection_rate,
            "candidate_reduction": candidate_reduction,
            "sourcing_cost_savings": sourcing_savings,
            "productivity_savings": productivity_savings,
            "total_quality_savings": total_quality_savings,
            "quality_savings_percentage": (total_quality_savings / (avg_cost_per_hire * annual_hires)) * 100
        }
    
    def calculate_time_savings_value(
        self,
        our_time_to_shortlist_hours: float,
        annual_hires: int = 5_000,
        recruiter_hourly_cost: float = 75
    ) -> Dict[str, float]:
        """
        Calculate value of time savings for recruiters.
        
        Args:
            our_time_to_shortlist_hours: Our time to shortlist (hours)
            annual_hires: Annual hiring volume
            recruiter_hourly_cost: Cost per recruiter hour
        
        Returns:
            Dictionary with time savings value
        """
        baseline_hours = self.baseline_time * 24  # 21 days in hours
        time_saved_per_hire = baseline_hours - our_time_to_shortlist_hours
        
        # Assume each hire requires reviewing ~50 candidates
        candidates_per_hire = 50
        total_candidates = annual_hires * candidates_per_hire
        
        # Time savings
        total_hours_saved = (time_saved_per_hire / candidates_per_hire) * total_candidates
        labor_cost_savings = total_hours_saved * recruiter_hourly_cost
        
        # FTE equivalents freed up
        hours_per_fte_year = 2080
        ftes_freed = total_hours_saved / hours_per_fte_year
        
        return {
            "time_saved_per_candidate_hours": time_saved_per_hire / candidates_per_hire,
            "total_hours_saved_annually": total_hours_saved,
            "labor_cost_savings": labor_cost_savings,
            "ftes_freed": ftes_freed,
            "ftes_value": ftes_freed * recruiter_hourly_cost * hours_per_fte_year,
            "time_efficiency_gain_percentage": (time_saved_per_hire / baseline_hours) * 100
        }
    
    def calculate_risk_reduction_value(
        self,
        bias_flags_reduction_percentage: float = 95
    ) -> Dict[str, float]:
        """
        Estimate value of risk reduction (avoiding lawsuits, compliance issues).
        
        Args:
            bias_flags_reduction_percentage: % reduction in bias indicators
        
        Returns:
            Dictionary with risk reduction value
        """
        # Industry average discrimination lawsuit costs
        avg_lawsuit_cost = 500_000  # Settlement + legal fees
        lawsuit_probability_baseline = 0.05  # 5% chance per year (already had lawsuits)
        lawsuit_probability_ours = 0.01  # 1% with our solution
        
        expected_lawsuit_cost_baseline = avg_lawsuit_cost * lawsuit_probability_baseline
        expected_lawsuit_cost_ours = avg_lawsuit_cost * lawsuit_probability_ours
        risk_reduction_value = expected_lawsuit_cost_baseline - expected_lawsuit_cost_ours
        
        # Compliance cost savings
        audit_cost_reduction = 50_000  # Less compliance audits needed
        
        # Reputation risk (harder to quantify, conservative estimate)
        reputation_risk_reduction = 100_000  # Brand protection value
        
        total_risk_value = risk_reduction_value + audit_cost_reduction + reputation_risk_reduction
        
        return {
            "lawsuit_risk_reduction": risk_reduction_value,
            "compliance_cost_savings": audit_cost_reduction,
            "reputation_protection_value": reputation_risk_reduction,
            "total_risk_reduction_value": total_risk_value,
            "bias_reduction_percentage": bias_flags_reduction_percentage
        }
    
    def calculate_comprehensive_roi(
        self,
        avg_cost_per_candidate: float,
        our_false_rejection_rate: float,
        our_time_to_shortlist_hours: float,
        implementation_cost: float = 50_000,
        annual_candidate_volume: int = 250_000,
        annual_hires: int = 5_000
    ) -> Dict[str, any]:
        """
        Calculate comprehensive ROI including all value factors.
        
        Args:
            avg_cost_per_candidate: Our processing cost per candidate
            our_false_rejection_rate: Our false rejection rate
            our_time_to_shortlist_hours: Our time to shortlist
            implementation_cost: One-time implementation cost
            annual_candidate_volume: Annual candidates to process
            annual_hires: Annual hires to make
        
        Returns:
            Complete ROI analysis
        """
        # Calculate all savings categories
        direct_savings = self.calculate_direct_cost_savings(
            avg_cost_per_candidate, annual_candidate_volume
        )
        
        quality_savings = self.calculate_quality_cost_savings(
            our_false_rejection_rate, annual_hires=annual_hires
        )
        
        time_savings = self.calculate_time_savings_value(
            our_time_to_shortlist_hours, annual_hires=annual_hires
        )
        
        risk_savings = self.calculate_risk_reduction_value()
        
        # Total annual value
        total_annual_savings = (
            direct_savings["annual_savings"] +
            quality_savings["total_quality_savings"] +
            time_savings["labor_cost_savings"] +
            risk_savings["total_risk_reduction_value"]
        )
        
        # ROI calculations
        first_year_net_savings = total_annual_savings - implementation_cost
        payback_period_months = (implementation_cost / (total_annual_savings / 12))
        
        three_year_value = (total_annual_savings * 3) - implementation_cost
        five_year_value = (total_annual_savings * 5) - implementation_cost
        
        roi_percentage = (total_annual_savings / implementation_cost) * 100
        
        return {
            "summary": {
                "total_annual_savings": total_annual_savings,
                "implementation_cost": implementation_cost,
                "first_year_net_savings": first_year_net_savings,
                "payback_period_months": payback_period_months,
                "three_year_total_value": three_year_value,
                "five_year_total_value": five_year_value,
                "roi_percentage": roi_percentage
            },
            "savings_breakdown": {
                "direct_cost_savings": direct_savings["annual_savings"],
                "quality_improvement_savings": quality_savings["total_quality_savings"],
                "time_efficiency_savings": time_savings["labor_cost_savings"],
                "risk_reduction_value": risk_savings["total_risk_reduction_value"]
            },
            "detailed_analysis": {
                "direct_costs": direct_savings,
                "quality_costs": quality_savings,
                "time_savings": time_savings,
                "risk_reduction": risk_savings
            },
            "comparison": VendorComparison(
                baseline_annual_cost=self.baseline_cost,
                our_annual_cost=direct_savings["our_annual_cost"],
                annual_savings=total_annual_savings,
                savings_percentage=(total_annual_savings / self.baseline_cost) * 100,
                payback_period_months=payback_period_months,
                three_year_savings=three_year_value,
                five_year_savings=five_year_value
            ),
            "executive_summary": [
                f"Total annual savings: ${total_annual_savings:,.0f}",
                f"ROI: {roi_percentage:.0f}% return on investment",
                f"Payback period: {payback_period_months:.1f} months",
                f"3-year value: ${three_year_value:,.0f}",
                f"5-year value: ${five_year_value:,.0f}"
            ]
        }
    
    def create_comparison_table(
        self,
        avg_cost_per_candidate: float,
        our_false_rejection_rate: float,
        our_time_to_shortlist_hours: float
    ) -> Dict[str, any]:
        """
        Create side-by-side comparison table for presentation.
        
        Returns:
            Formatted comparison data
        """
        return {
            "metrics": [
                {
                    "metric": "Annual Cost",
                    "baseline_vendor": f"${self.baseline_cost:,.0f}",
                    "our_solution": f"${avg_cost_per_candidate * 250_000:,.0f}",
                    "improvement": f"${self.baseline_cost - (avg_cost_per_candidate * 250_000):,.0f} saved"
                },
                {
                    "metric": "False Rejection Rate",
                    "baseline_vendor": f"{self.baseline_false_rejection * 100:.0f}%",
                    "our_solution": f"{our_false_rejection_rate * 100:.0f}%",
                    "improvement": f"{(self.baseline_false_rejection - our_false_rejection_rate) * 100:.0f}% reduction"
                },
                {
                    "metric": "Time to Shortlist",
                    "baseline_vendor": f"{self.baseline_time} days",
                    "our_solution": f"{our_time_to_shortlist_hours / 24:.2f} days",
                    "improvement": f"{self.baseline_time - (our_time_to_shortlist_hours / 24):.1f} days faster"
                },
                {
                    "metric": "Decision Transparency",
                    "baseline_vendor": "None",
                    "our_solution": "Full explanations",
                    "improvement": "100% transparency"
                },
                {
                    "metric": "Bias Detection",
                    "baseline_vendor": "Not available",
                    "our_solution": "Active monitoring",
                    "improvement": "Risk mitigation"
                },
                {
                    "metric": "Audit Trail",
                    "baseline_vendor": "Limited",
                    "our_solution": "Complete",
                    "improvement": "Full compliance"
                }
            ]
        }
