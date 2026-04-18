# Module 03 — Portfolio Construction: Scenario Index

27 scenarios, five with published golden answers. The table below is
the navigable entry point for reviewers and for benchmark scripts that
want to iterate scenarios in a predictable order.

Grouped by scenario category so the dominant "position_sizing" cluster
is not lumped with the smaller thematic variants (healthcare pair,
crowding, healthcare-risk).

## Scenarios with Published Golden Answers

These five are benchmark-ready.

| Scenario | Title | Difficulty | Category |
|---|---|---|---|
| [crowding_risk_sizing](crowding_risk_sizing.yaml) | Crowding Risk and Position Sizing — When Consensus Becomes the Risk | hard | crowding_risk |
| [healthcare_services_policy_risk](healthcare_services_policy_risk.yaml) | Healthcare Services: Low Volatility, High Risk | hard | healthcare_risk |
| [pharma_biotech_pair](pharma_biotech_pair.yaml) | Pharma/Biotech Pair: Hedge the Environment, Size the Alpha | hard | healthcare_pairs |
| [risk_based_sizing](risk_based_sizing.yaml) | Capital vs. Risk: The High-Vol Trap | — | — |
| [risk_sizing_trap](risk_sizing_trap.yaml) | Notional vs. Risk-Based Sizing | — | — |

## Position-Sizing Scenarios (no golden answer yet)

These 22 are on disk but not yet anchored. Phase 1 prioritizes
authoring at least two additional goldens from this list; the rest
remain exploratory fodder for Phase 3 adversarial variants.

| Scenario | Title | Difficulty |
|---|---|---|
| [adding_to_a_confirmed_winner](adding_to_a_confirmed_winner.yaml) | Adding to a Confirmed Winner: When Appreciation Does the Sizing for You | hard |
| [asymmetric_payoff_restructuring_candidate](asymmetric_payoff_restructuring_candidate.yaml) | Asymmetric Payoff Restructuring Candidate: Positive EV Doesn't Mean Size Aggressively | hard |
| [averaging_down_thesis_intact](averaging_down_thesis_intact.yaml) | Averaging Down with Thesis Intact: When Cheaper Doesn't Mean Better Risk/Reward | hard |
| [beta_drift_momentum_reclassification](beta_drift_momentum_reclassification.yaml) | Beta Drift and Momentum Reclassification: Same Thesis, Different Risk Character | hard |
| [competitor_read_through_pre_earnings](competitor_read_through_pre_earnings.yaml) | Competitor Read-Through Pre-Earnings: Sizing for a Double Binary | hard |
| [correlated_position_addition](correlated_position_addition.yaml) | Correlated Position Addition: When 3% in Context Is Not 3% in Isolation | hard |
| [drawdown_budget_binding_constraint](drawdown_budget_binding_constraint.yaml) | Drawdown Budget as Binding Constraint: Survival Over Optimization | expert |
| [earnings_cluster_aggregate_risk](earnings_cluster_aggregate_risk.yaml) | Earnings Cluster Aggregate Risk: When Individual Sizing Is Right but Portfolio Risk Is Wrong | expert |
| [gross_leverage_ceiling_tradeoff](gross_leverage_ceiling_tradeoff.yaml) | Gross Leverage Ceiling Tradeoff: Every Entry Requires an Exit | hard |
| [idiosyncratic_to_systematic_risk_shift](idiosyncratic_to_systematic_risk_shift.yaml) | Idiosyncratic to Systematic Risk Shift: When Your Alpha Becomes Everyone's Beta | hard |
| [kelly_criterion_with_small_sample](kelly_criterion_with_small_sample.yaml) | Kelly Criterion with Small Sample: When Statistical Confidence Doesn't Support the Math | expert |
| [liquidity_deterioration_exit_risk](liquidity_deterioration_exit_risk.yaml) | Liquidity Deterioration and Exit Risk: When the Door Gets Smaller | hard |
| [marginal_var_contribution](marginal_var_contribution.yaml) | Marginal VaR Contribution: The Position That Looks Fine Alone | expert |
| [options_vs_equity_position_expression](options_vs_equity_position_expression.yaml) | Options vs Equity Position Expression: Same Thesis, Different Portfolio Impact | hard |
| [pair_trade_leg_divergence](pair_trade_leg_divergence.yaml) | Pair Trade Leg Divergence: When the Hedge Ratio Goes Stale | hard |
| [post_acquisition_spread_sizing](post_acquisition_spread_sizing.yaml) | Post-Acquisition Spread Sizing: When 8% Upside Masks 30% Downside | moderate |
| [post_earnings_position_doubling](post_earnings_position_doubling.yaml) | Post-Earnings Position Doubling: When Conviction Doubles but Risk Quadruples | hard |
| [redemption_liquidation_prioritization](redemption_liquidation_prioritization.yaml) | Redemption Liquidation Prioritization: Sizing in Reverse | expert |
| [sector_concentration_limit_breach](sector_concentration_limit_breach.yaml) | Sector Concentration Limit Breach: Discipline Over Conviction | hard |
| [short_borrow_cost_spike](short_borrow_cost_spike.yaml) | Short Borrow Cost Spike: When the Carry Changes the Calculus | moderate |
| [staged_entry_vs_full_allocation](staged_entry_vs_full_allocation.yaml) | Staged Entry vs Full Allocation: When Patience Helps and When It Hurts | moderate |
| [vol_regime_shift_resizing](vol_regime_shift_resizing.yaml) | Vol Regime Shift Resizing: When Mechanical Rules Meet Implementation Reality | hard |

## Counts

- Total scenarios: 27
- Difficulty breakdown: expert × 4, hard × 17, moderate × 3, unspecified × 2, other × 1
- With golden answer: 5 / 27
- Categories covered: position_sizing, crowding_risk, healthcare_risk, healthcare_pairs

This module is the most over-weighted in the repo. The Phase 1 plan
calls for golden-answer backfill before adding new scenarios; module
03 is not slated for further scenario additions in this phase.
